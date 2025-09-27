"""
Base downloader class for all data source types.
"""
import abc
import logging
from typing import Dict, Any


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
        
    @abc.abstractmethod
    def download(self) -> str:
        """
        Download data from the vendor source.
        
        Returns:
            str: Path to the downloaded file
            
        Raises:
            Exception: If download fails
        """
        pass
    
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