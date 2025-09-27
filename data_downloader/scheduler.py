"""
Scheduler module for time-based feed downloads.
Handles both scheduled feeds and real-time feeds.
"""
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import pytz
from croniter import croniter


class FeedType(Enum):
    """Types of feed scheduling."""
    SCHEDULED = "scheduled"  # Download at specific times
    REAL_TIME = "real_time"  # Download continuously
    ON_DEMAND = "on_demand"  # Download when manually triggered


@dataclass
class ScheduleConfig:
    """Configuration for feed scheduling."""
    feed_type: FeedType
    cron_expression: Optional[str] = None  # For scheduled feeds
    interval_seconds: Optional[int] = None  # For real-time feeds (polling interval)
    timezone: str = "UTC"
    enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 300  # 5 minutes


class FeedScheduler:
    """
    Scheduler for managing feed downloads based on time schedules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scheduler.
        
        Args:
            config: Global configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("scheduler")
        self.running = False
        self.threads = {}
        self.schedule_configs = {}
        
        # Load schedule configurations
        self._load_schedule_configs()
    
    def _load_schedule_configs(self):
        """Load schedule configurations from vendor configs."""
        vendors = self.config.get("vendors", [])
        
        for vendor in vendors:
            vendor_name = vendor.get("name")
            schedule_config = vendor.get("schedule", {})
            
            if schedule_config:
                # Parse schedule configuration
                feed_type = FeedType(schedule_config.get("type", "real_time"))
                
                config = ScheduleConfig(
                    feed_type=feed_type,
                    cron_expression=schedule_config.get("cron"),
                    interval_seconds=schedule_config.get("interval_seconds", 300),
                    timezone=schedule_config.get("timezone", "UTC"),
                    enabled=schedule_config.get("enabled", True),
                    max_retries=schedule_config.get("max_retries", 3),
                    retry_delay=schedule_config.get("retry_delay", 300)
                )
                
                self.schedule_configs[vendor_name] = config
                self.logger.info(f"Loaded schedule config for {vendor_name}: {feed_type.value}")
    
    def start(self):
        """Start the scheduler for all enabled feeds."""
        self.running = True
        self.logger.info("Starting Feed Scheduler")
        
        for vendor_name, schedule_config in self.schedule_configs.items():
            if schedule_config.enabled:
                self._start_vendor_scheduler(vendor_name, schedule_config)
        
        self.logger.info(f"Scheduler started for {len(self.threads)} vendors")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        self.logger.info("Stopping Feed Scheduler")
        
        # Wait for all threads to finish
        for thread in self.threads.values():
            thread.join(timeout=10)
        
        self.threads.clear()
        self.logger.info("Scheduler stopped")
    
    def _start_vendor_scheduler(self, vendor_name: str, schedule_config: ScheduleConfig):
        """Start scheduler thread for a specific vendor."""
        if schedule_config.feed_type == FeedType.SCHEDULED:
            thread = threading.Thread(
                target=self._scheduled_download_loop,
                args=(vendor_name, schedule_config),
                name=f"scheduler-{vendor_name}"
            )
        elif schedule_config.feed_type == FeedType.REAL_TIME:
            thread = threading.Thread(
                target=self._realtime_download_loop,
                args=(vendor_name, schedule_config),
                name=f"realtime-{vendor_name}"
            )
        else:
            self.logger.warning(f"Unknown feed type for {vendor_name}: {schedule_config.feed_type}")
            return
        
        thread.daemon = True
        thread.start()
        self.threads[vendor_name] = thread
        self.logger.info(f"Started {schedule_config.feed_type.value} scheduler for {vendor_name}")
    
    def _scheduled_download_loop(self, vendor_name: str, schedule_config: ScheduleConfig):
        """Loop for scheduled downloads using cron expressions."""
        try:
            # Get timezone
            tz = pytz.timezone(schedule_config.timezone)
            
            # Create cron iterator
            cron = croniter(schedule_config.cron_expression, datetime.now(tz))
            
            while self.running:
                try:
                    # Get next execution time
                    next_run = cron.get_next(datetime)
                    current_time = datetime.now(tz)
                    
                    # Calculate sleep time
                    sleep_seconds = (next_run - current_time).total_seconds()
                    
                    if sleep_seconds > 0:
                        self.logger.info(
                            f"{vendor_name}: Next scheduled download at {next_run} "
                            f"(in {sleep_seconds/60:.1f} minutes)"
                        )
                        
                        # Sleep until next execution time
                        time.sleep(min(sleep_seconds, 3600))  # Max 1 hour sleep
                    
                    if self.running:
                        # Execute download
                        self._execute_download(vendor_name, schedule_config)
                        
                except Exception as e:
                    self.logger.error(f"Error in scheduled download loop for {vendor_name}: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
                    
        except Exception as e:
            self.logger.error(f"Fatal error in scheduled download loop for {vendor_name}: {e}")
    
    def _realtime_download_loop(self, vendor_name: str, schedule_config: ScheduleConfig):
        """Loop for real-time downloads with polling interval."""
        while self.running:
            try:
                # Execute download
                self._execute_download(vendor_name, schedule_config)
                
                # Sleep for the specified interval
                time.sleep(schedule_config.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in real-time download loop for {vendor_name}: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _execute_download(self, vendor_name: str, schedule_config: ScheduleConfig):
        """Execute download for a vendor with retry logic."""
        from downloader_factory import get_downloader
        from parsers.parser_factory import parse_file
        from utils.decompressor import decompress
        
        # Find vendor configuration
        vendor_config = None
        for vendor in self.config.get("vendors", []):
            if vendor.get("name") == vendor_name:
                vendor_config = vendor
                break
        
        if not vendor_config:
            self.logger.error(f"Vendor configuration not found: {vendor_name}")
            return
        
        retry_count = 0
        while retry_count <= schedule_config.max_retries:
            try:
                self.logger.info(f"Executing download for {vendor_name} (attempt {retry_count + 1})")
                
                # Create downloader
                downloader = get_downloader(vendor_config)
                
                # Download data with proper download type
                download_type = "scheduled" if schedule_config.feed_type == FeedType.SCHEDULED else "real_time"
                local_file = downloader.download(download_type=download_type)
                
                # Handle compressed files
                files_to_process = [local_file]
                if vendor_config.get("compressed", False):
                    compression_type = vendor_config.get("compression_type", "auto")
                    extracted_files = decompress(local_file, compression_type)
                    files_to_process = extracted_files
                
                # Parse and normalize data
                format_type = vendor_config.get("format")
                if format_type:
                    for file_path in files_to_process:
                        try:
                            parsed_data = parse_file(file_path, format_type)
                            
                            # Save normalized data
                            if isinstance(parsed_data, dict):
                                for sheet_name, df in parsed_data.items():
                                    output_path = file_path.replace(".", f"_{sheet_name}_parsed.")
                                    df.to_csv(output_path, index=False)
                            else:
                                output_path = file_path.replace(".", "_parsed.")
                                parsed_data.to_csv(output_path, index=False)
                            
                            self.logger.info(f"Successfully processed {vendor_name}: {output_path}")
                            
                        except Exception as e:
                            self.logger.error(f"Failed to parse {file_path}: {e}")
                
                # Success - break out of retry loop
                break
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"Download failed for {vendor_name} (attempt {retry_count}): {e}")
                
                if retry_count <= schedule_config.max_retries:
                    self.logger.info(f"Retrying {vendor_name} in {schedule_config.retry_delay} seconds")
                    time.sleep(schedule_config.retry_delay)
                else:
                    self.logger.error(f"Max retries exceeded for {vendor_name}")
    
    def get_next_run_times(self) -> Dict[str, Optional[datetime]]:
        """Get next run times for all scheduled vendors."""
        next_runs = {}
        
        for vendor_name, schedule_config in self.schedule_configs.items():
            if schedule_config.feed_type == FeedType.SCHEDULED and schedule_config.cron_expression:
                try:
                    tz = pytz.timezone(schedule_config.timezone)
                    cron = croniter(schedule_config.cron_expression, datetime.now(tz))
                    next_runs[vendor_name] = cron.get_next(datetime)
                except Exception as e:
                    self.logger.error(f"Error calculating next run for {vendor_name}: {e}")
                    next_runs[vendor_name] = None
            else:
                next_runs[vendor_name] = None
        
        return next_runs
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "running": self.running,
            "active_threads": len(self.threads),
            "vendors": list(self.threads.keys()),
            "next_runs": self.get_next_run_times()
        }


def validate_cron_expression(cron_expr: str) -> bool:
    """Validate a cron expression."""
    try:
        # Create a croniter instance to validate
        cron = croniter(cron_expr)
        # Try to get the next execution time to ensure it's valid
        # Use a fixed date to avoid timezone issues
        test_date = datetime(2024, 1, 1, 12, 0, 0)
        cron.get_next(test_date)
        return True
    except Exception:
        return False


def get_common_schedules() -> Dict[str, str]:
    """Get common cron expressions for financial data feeds."""
    return {
        "market_open": "0 9 * * 1-5",  # 9 AM weekdays
        "market_close": "0 16 * * 1-5",  # 4 PM weekdays
        "daily_morning": "0 8 * * *",  # 8 AM daily
        "daily_evening": "0 18 * * *",  # 6 PM daily
        "hourly": "0 * * * *",  # Every hour
        "every_15_minutes": "*/15 * * * *",  # Every 15 minutes
        "every_5_minutes": "*/5 * * * *",  # Every 5 minutes
        "weekly_monday": "0 9 * * 1",  # 9 AM Mondays
        "monthly_first": "0 9 1 * *",  # 9 AM first day of month
        "end_of_day": "0 23 * * *",  # 11 PM daily
        "pre_market": "0 6 * * 1-5",  # 6 AM weekdays
        "after_hours": "0 20 * * 1-5",  # 8 PM weekdays
    }