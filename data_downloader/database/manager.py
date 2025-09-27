"""
Database manager for SQLite operations.
"""
import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import (
    DownloadRecord, DownloadStatus, DownloadType, 
    VendorStats, SystemStats, DatabaseSchema
)


class DatabaseManager:
    """
    Manager for SQLite database operations.
    """
    
    def __init__(self, db_path: str = "feed_downloader.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger("database.manager")
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create downloads table
                cursor.execute(DatabaseSchema.DOWNLOADS_TABLE)
                
                # Create indexes
                for index_sql in DatabaseSchema.INDEXES:
                    cursor.execute(index_sql)
                
                # Create views
                cursor.execute(DatabaseSchema.VENDOR_STATS_VIEW)
                cursor.execute(DatabaseSchema.DAILY_STATS_VIEW)
                cursor.execute(DatabaseSchema.RECENT_FAILURES_VIEW)
                
                conn.commit()
                self.logger.info(f"Database initialized: {self.db_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def start_download(self, vendor_name: str, download_type: str, source_type: str, 
                      source_url: str, local_path: str, schedule_config: Dict[str, Any] = None) -> int:
        """
        Record the start of a download.
        
        Args:
            vendor_name: Name of the vendor
            download_type: Type of download (scheduled, real_time, on_demand)
            source_type: Type of source (sftp, rest_api, websocket, http)
            source_url: URL or path of the source
            local_path: Local file path
            schedule_config: Schedule configuration dictionary
            
        Returns:
            int: Download record ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                schedule_config_json = json.dumps(schedule_config) if schedule_config else None
                
                cursor.execute("""
                    INSERT INTO downloads 
                    (vendor_name, download_type, source_type, source_url, local_path, 
                     status, start_time, schedule_config, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vendor_name,
                    download_type,
                    source_type,
                    source_url,
                    local_path,
                    DownloadStatus.IN_PROGRESS.value,
                    datetime.now(),
                    schedule_config_json,
                    datetime.now(),
                    datetime.now()
                ))
                
                download_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Started download record: {download_id} for {vendor_name}")
                return download_id
                
        except Exception as e:
            self.logger.error(f"Failed to start download record: {e}")
            raise
    
    def complete_download(self, download_id: int, file_size: int = None, 
                         metadata: Dict[str, Any] = None):
        """
        Mark download as completed.
        
        Args:
            download_id: Download record ID
            file_size: Size of downloaded file in bytes
            metadata: Additional metadata dictionary
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get start time to calculate duration
                cursor.execute("SELECT start_time FROM downloads WHERE id = ?", (download_id,))
                row = cursor.fetchone()
                
                if row:
                    start_time = datetime.fromisoformat(row['start_time'])
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                else:
                    duration = None
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute("""
                    UPDATE downloads 
                    SET status = ?, end_time = ?, duration_seconds = ?, 
                        file_size = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    DownloadStatus.COMPLETED.value,
                    datetime.now(),
                    duration,
                    file_size,
                    metadata_json,
                    datetime.now(),
                    download_id
                ))
                
                conn.commit()
                self.logger.debug(f"Completed download record: {download_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to complete download record {download_id}: {e}")
            raise
    
    def fail_download(self, download_id: int, error_message: str, 
                     increment_retry: bool = True):
        """
        Mark download as failed.
        
        Args:
            download_id: Download record ID
            error_message: Error message
            increment_retry: Whether to increment retry count
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current retry count
                cursor.execute("SELECT retry_count FROM downloads WHERE id = ?", (download_id,))
                row = cursor.fetchone()
                retry_count = (row['retry_count'] + 1) if row and increment_retry else (row['retry_count'] if row else 0)
                
                cursor.execute("""
                    UPDATE downloads 
                    SET status = ?, end_time = ?, error_message = ?, 
                        retry_count = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    DownloadStatus.FAILED.value,
                    datetime.now(),
                    error_message,
                    retry_count,
                    datetime.now(),
                    download_id
                ))
                
                conn.commit()
                self.logger.debug(f"Failed download record: {download_id} - {error_message}")
                
        except Exception as e:
            self.logger.error(f"Failed to update download record {download_id}: {e}")
            raise
    
    def get_download_record(self, download_id: int) -> Optional[DownloadRecord]:
        """
        Get a download record by ID.
        
        Args:
            download_id: Download record ID
            
        Returns:
            DownloadRecord or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM downloads WHERE id = ?", (download_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_download_record(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get download record {download_id}: {e}")
            return None
    
    def get_vendor_downloads(self, vendor_name: str, limit: int = 100) -> List[DownloadRecord]:
        """
        Get recent downloads for a vendor.
        
        Args:
            vendor_name: Name of the vendor
            limit: Maximum number of records to return
            
        Returns:
            List of DownloadRecord objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM downloads 
                    WHERE vendor_name = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (vendor_name, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_download_record(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get vendor downloads for {vendor_name}: {e}")
            return []
    
    def get_recent_downloads(self, limit: int = 100) -> List[DownloadRecord]:
        """
        Get recent downloads across all vendors.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of DownloadRecord objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM downloads 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_download_record(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get recent downloads: {e}")
            return []
    
    def get_vendor_stats(self, vendor_name: str = None) -> List[VendorStats]:
        """
        Get vendor statistics.
        
        Args:
            vendor_name: Specific vendor name (None for all vendors)
            
        Returns:
            List of VendorStats objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if vendor_name:
                    cursor.execute("SELECT * FROM vendor_stats WHERE vendor_name = ?", (vendor_name,))
                else:
                    cursor.execute("SELECT * FROM vendor_stats ORDER BY total_downloads DESC")
                
                rows = cursor.fetchall()
                return [self._row_to_vendor_stats(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get vendor stats: {e}")
            return []
    
    def get_system_stats(self) -> Optional[SystemStats]:
        """
        Get overall system statistics.
        
        Returns:
            SystemStats object or None if error
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get overall stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_downloads,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_downloads,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_downloads,
                        SUM(COALESCE(file_size, 0)) as total_data_size,
                        AVG(duration_seconds) as avg_duration
                    FROM downloads
                """)
                
                row = cursor.fetchone()
                
                if row:
                    total_downloads = row['total_downloads']
                    successful_downloads = row['successful_downloads']
                    success_rate = (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0
                    
                    # Get uptime (time since first download)
                    cursor.execute("SELECT MIN(created_at) as first_download FROM downloads")
                    first_row = cursor.fetchone()
                    uptime_hours = 0
                    if first_row and first_row['first_download']:
                        first_download = datetime.fromisoformat(first_row['first_download'])
                        uptime_hours = (datetime.now() - first_download).total_seconds() / 3600
                    
                    # Get active vendors count
                    cursor.execute("SELECT COUNT(DISTINCT vendor_name) as active_vendors FROM downloads")
                    vendors_row = cursor.fetchone()
                    active_vendors = vendors_row['active_vendors'] if vendors_row else 0
                    
                    return SystemStats(
                        total_downloads=total_downloads,
                        successful_downloads=successful_downloads,
                        failed_downloads=row['failed_downloads'],
                        success_rate=round(success_rate, 2),
                        total_data_size=row['total_data_size'],
                        avg_duration=round(row['avg_duration'] or 0, 2),
                        uptime_hours=round(uptime_hours, 2),
                        active_vendors=active_vendors
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return None
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily statistics for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily statistics dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM daily_stats 
                    WHERE download_date >= DATE('now', '-{} days')
                    ORDER BY download_date DESC
                """.format(days))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get daily stats: {e}")
            return []
    
    def get_recent_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent failed downloads.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of failure records
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM recent_failures LIMIT ?", (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get recent failures: {e}")
            return []
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """
        Clean up old download records.
        
        Args:
            days_to_keep: Number of days of records to keep
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                cursor.execute("""
                    DELETE FROM downloads 
                    WHERE created_at < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old download records")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old records: {e}")
    
    def _row_to_download_record(self, row) -> DownloadRecord:
        """Convert database row to DownloadRecord object."""
        return DownloadRecord(
            id=row['id'],
            vendor_name=row['vendor_name'],
            download_type=row['download_type'],
            source_type=row['source_type'],
            source_url=row['source_url'],
            local_path=row['local_path'],
            file_size=row['file_size'],
            status=row['status'],
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_seconds=row['duration_seconds'],
            error_message=row['error_message'],
            retry_count=row['retry_count'],
            schedule_config=row['schedule_config'],
            metadata=row['metadata'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
    
    def _row_to_vendor_stats(self, row) -> VendorStats:
        """Convert database row to VendorStats object."""
        return VendorStats(
            vendor_name=row['vendor_name'],
            total_downloads=row['total_downloads'],
            successful_downloads=row['successful_downloads'],
            failed_downloads=row['failed_downloads'],
            success_rate=row['success_rate'],
            avg_duration=row['avg_duration'],
            total_data_size=row['total_data_size'],
            last_download=datetime.fromisoformat(row['last_download']) if row['last_download'] else None,
            last_success=datetime.fromisoformat(row['last_success']) if row['last_success'] else None,
            last_failure=datetime.fromisoformat(row['last_failure']) if row['last_failure'] else None
        )