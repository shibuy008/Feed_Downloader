"""
HTTP file downloader for downloading files from HTTP/HTTPS URLs.
"""
import os
import time
import requests
from typing import Dict, Any
from .base import BaseDownloader


class HTTPDownloader(BaseDownloader):
    """
    Downloads files from HTTP/HTTPS URLs using requests.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.required_fields = ["url"]
        self.validate_config(self.required_fields)
    
    def download(self) -> str:
        """
        Download file from HTTP/HTTPS URL.
        
        Returns:
            str: Path to the downloaded file
        """
        url = self.config["url"]
        headers = self.config.get("headers", {})
        local_path = self.get_local_path()
        timeout = self.config.get("timeout", 30)
        chunk_size = self.config.get("chunk_size", 8192)
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.logger.info(f"Downloading from {url}")
            
            # Make HTTP request with streaming
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Get file size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # Download file in chunks
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if downloaded_size % (chunk_size * 100) == 0:  # Log every 100 chunks
                                self.logger.info(f"Download progress: {progress:.1f}%")
            
            self.logger.info(f"Successfully downloaded {url} → {local_path}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP download failed: {str(e)}")
            raise Exception(f"HTTP download failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"HTTP download failed: {str(e)}")
            raise Exception(f"HTTP download failed: {str(e)}")
    
    def download_with_auth(self, username: str = None, password: str = None) -> str:
        """
        Download file with HTTP Basic Authentication.
        
        Args:
            username: HTTP Basic Auth username
            password: HTTP Basic Auth password
            
        Returns:
            str: Path to the downloaded file
        """
        if username and password:
            self.config["auth"] = (username, password)
        
        return self.download()
    
    def download_with_retry(self, max_retries: int = 3, retry_delay: int = 5) -> str:
        """
        Download file with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
            
        Returns:
            str: Path to the downloaded file
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retry attempt {attempt}/{max_retries}")
                    time.sleep(retry_delay)
                
                return self.download()
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Download attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries:
                    self.logger.error(f"All {max_retries + 1} download attempts failed")
                    raise Exception(f"Download failed after {max_retries + 1} attempts: {str(last_exception)}")
        
        raise Exception(f"Download failed: {str(last_exception)}")
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the file without downloading it.
        
        Returns:
            Dict: File information including size, content-type, etc.
        """
        url = self.config["url"]
        headers = self.config.get("headers", {})
        timeout = self.config.get("timeout", 30)
        
        try:
            # Make HEAD request to get file info
            response = requests.head(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            file_info = {
                "url": url,
                "content_length": response.headers.get('content-length'),
                "content_type": response.headers.get('content-type'),
                "last_modified": response.headers.get('last-modified'),
                "etag": response.headers.get('etag'),
                "status_code": response.status_code
            }
            
            return file_info
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get file info: {str(e)}")
            raise Exception(f"Failed to get file info: {str(e)}")