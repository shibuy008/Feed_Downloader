"""
Continuous runner for the Feed Downloader with scheduling capabilities.
This script runs the scheduler continuously and handles both scheduled and real-time feeds.
"""
import os
import sys
import signal
import argparse
import logging
import yaml
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import FeedScheduler, get_common_schedules


class SchedulerRunner:
    """
    Continuous runner for the Feed Downloader scheduler.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the scheduler runner.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = None
        self.scheduler = None
        self.logger = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def setup_logging(self, log_level: str = "INFO", log_file: str = None):
        """
        Setup logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        # Create logs directory if it doesn't exist
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file) if log_file else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger("scheduler_runner")
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info(f"Loaded configuration from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise Exception(f"Configuration loading failed: {str(e)}")
    
    def start(self):
        """Start the scheduler runner."""
        try:
            self.logger.info("Starting Feed Downloader Scheduler")
            self.logger.info("=" * 50)
            
            # Load configuration
            self.load_config()
            
            # Create scheduler
            self.scheduler = FeedScheduler(self.config)
            
            # Start scheduler
            self.scheduler.start()
            self.running = True
            
            # Display status
            self._display_status()
            
            # Main loop
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler runner."""
        if self.scheduler and self.running:
            self.logger.info("Stopping scheduler...")
            self.scheduler.stop()
            self.running = False
            self.logger.info("Scheduler stopped")
    
    def _main_loop(self):
        """Main loop for the scheduler runner."""
        try:
            while self.running:
                # Sleep for 1 minute and check status
                import time
                time.sleep(60)
                
                if self.running:
                    # Display periodic status update
                    self._display_status()
                    
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            self.stop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
            self.stop()
    
    def _display_status(self):
        """Display current scheduler status."""
        if not self.scheduler:
            return
        
        status = self.scheduler.get_status()
        
        self.logger.info("Scheduler Status:")
        self.logger.info(f"  Running: {status['running']}")
        self.logger.info(f"  Active Threads: {status['active_threads']}")
        self.logger.info(f"  Vendors: {', '.join(status['vendors'])}")
        
        # Display next run times
        next_runs = status['next_runs']
        if next_runs:
            self.logger.info("  Next Scheduled Runs:")
            for vendor, next_run in next_runs.items():
                if next_run:
                    self.logger.info(f"    {vendor}: {next_run}")
                else:
                    self.logger.info(f"    {vendor}: Real-time/On-demand")
        
        self.logger.info("-" * 50)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        if self.scheduler:
            return self.scheduler.get_status()
        return {"running": False, "active_threads": 0, "vendors": [], "next_runs": {}}


def main():
    """Main entry point for the scheduler runner."""
    parser = argparse.ArgumentParser(
        description="Feed Downloader Scheduler - Continuous runner for scheduled and real-time feeds"
    )
    parser.add_argument(
        "--config", "-c", 
        default="config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        help="Logging level"
    )
    parser.add_argument(
        "--log-file", 
        help="Log file path"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Show status and exit"
    )
    parser.add_argument(
        "--list-schedules", 
        action="store_true", 
        help="List common cron schedules and exit"
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = SchedulerRunner(args.config)
    
    # Setup logging
    runner.setup_logging(args.log_level, args.log_file)
    
    try:
        if args.list_schedules:
            # Display common schedules
            print("Common Cron Schedules for Financial Data:")
            print("=" * 50)
            schedules = get_common_schedules()
            for name, cron in schedules.items():
                print(f"{name:20} : {cron}")
            return 0
        
        if args.status:
            # Load config and show status
            runner.load_config()
            runner.scheduler = FeedScheduler(runner.config)
            status = runner.get_status()
            
            print("Feed Downloader Scheduler Status:")
            print("=" * 40)
            print(f"Running: {status['running']}")
            print(f"Active Threads: {status['active_threads']}")
            print(f"Vendors: {', '.join(status['vendors'])}")
            
            next_runs = status['next_runs']
            if next_runs:
                print("\nNext Scheduled Runs:")
                for vendor, next_run in next_runs.items():
                    if next_run:
                        print(f"  {vendor}: {next_run}")
                    else:
                        print(f"  {vendor}: Real-time/On-demand")
            
            return 0
        
        # Start the scheduler
        runner.start()
        
    except Exception as e:
        runner.logger.error(f"Application failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())