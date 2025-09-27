"""
Factory for creating downloader instances based on configuration.
"""
from typing import Dict, Any
from downloaders.sftp_downloader import SFTPDownloader
from downloaders.rest_api_downloader import RESTAPIDownloader
from downloaders.websocket_downloader import WebSocketDownloader
from downloaders.http_downloader import HTTPDownloader


def get_downloader(config: Dict[str, Any]):
    """
    Create a downloader instance based on the configuration type.
    
    Args:
        config: Dictionary containing vendor configuration
        
    Returns:
        BaseDownloader: Appropriate downloader instance
        
    Raises:
        ValueError: If the downloader type is not supported
    """
    downloader_type = config.get("type", "").lower()
    
    if downloader_type == "sftp":
        return SFTPDownloader(config)
    elif downloader_type == "rest_api":
        return RESTAPIDownloader(config)
    elif downloader_type == "websocket":
        return WebSocketDownloader(config)
    elif downloader_type == "http":
        return HTTPDownloader(config)
    else:
        raise ValueError(f"Unsupported downloader type: {downloader_type}. "
                        f"Supported types: sftp, rest_api, websocket, http")


def get_supported_types() -> list:
    """
    Get list of supported downloader types.
    
    Returns:
        list: List of supported downloader type strings
    """
    return ["sftp", "rest_api", "websocket", "http"]


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that the configuration contains required fields.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["name", "type", "local_path"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate type-specific requirements
    downloader_type = config.get("type", "").lower()
    
    if downloader_type == "sftp":
        sftp_required = ["host", "username", "password", "remote_path"]
        return all(field in config for field in sftp_required)
    elif downloader_type == "rest_api":
        return "endpoint" in config
    elif downloader_type == "websocket":
        return "url" in config
    elif downloader_type == "http":
        return "url" in config
    
    return False