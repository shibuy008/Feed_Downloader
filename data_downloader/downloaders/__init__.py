"""
Downloader modules for different data sources.
"""

from .base import BaseDownloader
from .sftp_downloader import SFTPDownloader
from .rest_api_downloader import RESTAPIDownloader
from .websocket_downloader import WebSocketDownloader
from .http_downloader import HTTPDownloader

__all__ = [
    'BaseDownloader',
    'SFTPDownloader', 
    'RESTAPIDownloader',
    'WebSocketDownloader',
    'HTTPDownloader'
]