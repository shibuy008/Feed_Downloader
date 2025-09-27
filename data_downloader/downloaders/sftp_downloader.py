"""
SFTP downloader for fetching files from SFTP servers.
"""
import os
import paramiko
from typing import Dict, Any
from .base import BaseDownloader


class SFTPDownloader(BaseDownloader):
    """
    Downloads files from SFTP servers using paramiko.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.required_fields = ["host", "username", "password", "remote_path"]
        self.validate_config(self.required_fields)
    
    def download(self) -> str:
        """
        Download file from SFTP server.
        
        Returns:
            str: Path to the downloaded file
        """
        host = self.config["host"]
        port = self.config.get("port", 22)
        username = self.config["username"]
        password = self.config["password"]
        remote_path = self.config["remote_path"]
        local_path = self.get_local_path()
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.logger.info(f"Connecting to SFTP server {host}:{port}")
            
            # Create transport and connect
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            
            # Create SFTP client
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            # Download file
            self.logger.info(f"Downloading {remote_path} to {local_path}")
            sftp.get(remote_path, local_path)
            
            # Close connections
            sftp.close()
            transport.close()
            
            self.logger.info(f"Successfully downloaded {remote_path} → {local_path}")
            return local_path
            
        except Exception as e:
            self.logger.error(f"SFTP download failed: {str(e)}")
            raise Exception(f"SFTP download failed: {str(e)}")
    
    def list_remote_files(self, remote_dir: str = None) -> list:
        """
        List files in remote directory (useful for debugging).
        
        Args:
            remote_dir: Remote directory path (uses remote_path parent if not provided)
            
        Returns:
            list: List of remote file names
        """
        if remote_dir is None:
            remote_dir = os.path.dirname(self.config["remote_path"])
        
        host = self.config["host"]
        port = self.config.get("port", 22)
        username = self.config["username"]
        password = self.config["password"]
        
        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            files = sftp.listdir(remote_dir)
            
            sftp.close()
            transport.close()
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list remote files: {str(e)}")
            raise Exception(f"Failed to list remote files: {str(e)}")