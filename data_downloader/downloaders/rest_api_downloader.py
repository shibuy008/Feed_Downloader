"""
REST API downloader for fetching data from REST endpoints.
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from .base import BaseDownloader


class RESTAPIDownloader(BaseDownloader):
    """
    Downloads data from REST API endpoints using requests.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.required_fields = ["endpoint"]
        self.validate_config(self.required_fields)
    
    def _do_download(self) -> str:
        """
        Download data from REST API endpoint.
        
        Returns:
            str: Path to the downloaded file
        """
        endpoint = self.config["endpoint"]
        headers = self.config.get("headers", {})
        params = self.config.get("params", {})
        local_path = self.get_local_path()
        timeout = self.config.get("timeout", 30)
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.logger.info(f"Making request to {endpoint}")
            
            # Make HTTP request
            response = requests.get(
                endpoint, 
                headers=headers, 
                params=params, 
                timeout=timeout
            )
            response.raise_for_status()
            
            # Determine content type and save accordingly
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type or endpoint.endswith('.json'):
                # Save as JSON
                with open(local_path, "w", encoding='utf-8') as f:
                    json.dump(response.json(), f, indent=2, ensure_ascii=False)
            else:
                # Save as raw content
                with open(local_path, "wb") as f:
                    f.write(response.content)
            
            self.logger.info(f"Successfully downloaded from {endpoint} → {local_path}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"REST API request failed: {str(e)}")
            raise Exception(f"REST API request failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"REST API download failed: {str(e)}")
            raise Exception(f"REST API download failed: {str(e)}")
    
    def download_with_auth(self, auth_type: str = "bearer", token: str = None) -> str:
        """
        Download with authentication.
        
        Args:
            auth_type: Type of authentication ('bearer', 'basic', 'api_key')
            token: Authentication token/key
            
        Returns:
            str: Path to the downloaded file
        """
        if auth_type == "bearer" and token:
            self.config["headers"]["Authorization"] = f"Bearer {token}"
        elif auth_type == "api_key" and token:
            api_key_header = self.config.get("api_key_header", "X-API-Key")
            self.config["headers"][api_key_header] = token
        elif auth_type == "basic" and token:
            # token should be base64 encoded username:password
            self.config["headers"]["Authorization"] = f"Basic {token}"
        
        return self._do_download()
    
    def post_download(self, data: Dict[str, Any] = None) -> str:
        """
        Download data using POST request.
        
        Args:
            data: POST data to send
            
        Returns:
            str: Path to the downloaded file
        """
        endpoint = self.config["endpoint"]
        headers = self.config.get("headers", {})
        local_path = self.get_local_path()
        timeout = self.config.get("timeout", 30)
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.logger.info(f"Making POST request to {endpoint}")
            
            # Make HTTP POST request
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Save response
            with open(local_path, "w", encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successfully downloaded from {endpoint} → {local_path}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"REST API POST request failed: {str(e)}")
            raise Exception(f"REST API POST request failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"REST API POST download failed: {str(e)}")
            raise Exception(f"REST API POST download failed: {str(e)}")