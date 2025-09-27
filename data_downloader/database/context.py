"""
Database context manager for download tracking.
"""
import logging
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any

from .manager import DatabaseManager


class DownloadTracker:
    """
    Context manager for tracking download activities in the database.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize download tracker.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger("database.tracker")
        self.download_id: Optional[int] = None
    
    @contextmanager
    def track_download(self, vendor_name: str, download_type: str, source_type: str,
                      source_url: str, local_path: str, schedule_config: Dict[str, Any] = None):
        """
        Context manager for tracking a download.
        
        Args:
            vendor_name: Name of the vendor
            download_type: Type of download (scheduled, real_time, on_demand)
            source_type: Type of source (sftp, rest_api, websocket, http)
            source_url: URL or path of the source
            local_path: Local file path
            schedule_config: Schedule configuration dictionary
            
        Yields:
            int: Download record ID
        """
        download_id = None
        
        try:
            # Start tracking
            download_id = self.db_manager.start_download(
                vendor_name=vendor_name,
                download_type=download_type,
                source_type=source_type,
                source_url=source_url,
                local_path=local_path,
                schedule_config=schedule_config
            )
            
            self.logger.debug(f"Started tracking download {download_id} for {vendor_name}")
            yield download_id
            
        except Exception as e:
            # Mark as failed if we have a download_id
            if download_id:
                try:
                    self.db_manager.fail_download(
                        download_id=download_id,
                        error_message=str(e)
                    )
                except Exception as db_error:
                    self.logger.error(f"Failed to record download failure: {db_error}")
            
            # Re-raise the original exception
            raise
        
        # If we reach here, the download was successful
        if download_id:
            try:
                # Get file size if local_path exists
                file_size = None
                metadata = {}
                
                if os.path.exists(local_path):
                    file_size = os.path.getsize(local_path)
                    metadata['file_size'] = file_size
                    metadata['file_exists'] = True
                else:
                    metadata['file_exists'] = False
                
                # Complete the download record
                self.db_manager.complete_download(
                    download_id=download_id,
                    file_size=file_size,
                    metadata=metadata
                )
                
                self.logger.debug(f"Completed tracking download {download_id} for {vendor_name}")
                
            except Exception as db_error:
                self.logger.error(f"Failed to complete download record {download_id}: {db_error}")


class DatabaseContext:
    """
    Database context for the entire application.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database context.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or "feed_downloader.db"
        self.db_manager = DatabaseManager(self.db_path)
        self.logger = logging.getLogger("database.context")
    
    def get_tracker(self) -> DownloadTracker:
        """
        Get a download tracker instance.
        
        Returns:
            DownloadTracker instance
        """
        return DownloadTracker(self.db_manager)
    
    def get_manager(self) -> DatabaseManager:
        """
        Get the database manager instance.
        
        Returns:
            DatabaseManager instance
        """
        return self.db_manager


# Global database context instance
db_context = None

def get_db_context(db_path: str = None) -> DatabaseContext:
    """
    Get or create database context.
    
    Args:
        db_path: Database path (optional)
        
    Returns:
        DatabaseContext instance
    """
    global db_context
    if db_context is None or (db_path and db_context.db_path != db_path):
        db_context = DatabaseContext(db_path)
    return db_context