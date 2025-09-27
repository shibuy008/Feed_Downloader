"""
Base downloader class for all data source types.
"""
import abc
import logging
import os
from typing import Dict, Any, Optional

from database import get_db_context, DownloadTracker


class BaseDownloader(abc.ABC):
    """
    Abstract base class for all downloaders.
    Each vendor source type should extend this class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the downloader with vendor configuration.
        
        Args:
            config: Dictionary containing vendor-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"downloader.{config.get('name', 'unknown')}")
        self.db_tracker = get_db_context().get_tracker()
        
    @abc.abstractmethod
    def _do_download(self) -> str:
        """
        Download data from the vendor source.
        
        Returns:
            str: Path to the downloaded file
            
        Raises:
            Exception: If download fails
        """
        pass
    
    def download(self, download_type: str = "on_demand") -> str:
        """
        Download data with database tracking.
        
        Args:
            download_type: Type of download (scheduled, real_time, on_demand)
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            Exception: If download fails
        """
        vendor_name = self.config.get("name", "unknown")
        source_type = self.config.get("type", "unknown")
        source_url = self._get_source_url()
        local_path = self.get_local_path()
        schedule_config = self.config.get("schedule")
        
        # Track download in database
        with self.db_tracker.track_download(
            vendor_name=vendor_name,
            download_type=download_type,
            source_type=source_type,
            source_url=source_url,
            local_path=local_path,
            schedule_config=schedule_config
        ) as download_id:
            self.logger.info(f"Starting download (ID: {download_id}) for {vendor_name}")
            
            # Perform the actual download
            result = self._do_download()
            
            self.logger.info(f"Completed download (ID: {download_id}) for {vendor_name}")
            return result
    
    def _get_source_url(self) -> str:
        """
        Get source URL for database tracking.
        
        Returns:
            str: Source URL or path
        """
        source_type = self.config.get("type", "")
        
        if source_type == "sftp":
            return f"sftp://{self.config.get('host', '')}:{self.config.get('port', 22)}{self.config.get('remote_path', '')}"
        elif source_type == "rest_api":
            return self.config.get("endpoint", "")
        elif source_type == "websocket":
            return self.config.get("url", "")
        elif source_type == "http":
            return self.config.get("url", "")
        else:
            return "unknown"
    
    def validate_config(self, required_fields: list) -> None:
        """
        Validate that required configuration fields are present.
        
        Args:
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required field is missing
        """
        missing_fields = [field for field in required_fields if field not in self.config]
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {missing_fields}")
    
    def get_local_path(self) -> str:
        """
        Get the local file path for saving downloaded data.
        
        Returns:
            str: Local file path
        """
        return self.config.get("local_path", "./downloads/default_file")