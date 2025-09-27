"""
WebSocket downloader for real-time data streams.
"""
import os
import json
import time
import websocket
from typing import Dict, Any, Optional, Callable
from .base import BaseDownloader


class WebSocketDownloader(BaseDownloader):
    """
    Downloads real-time data from WebSocket connections.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.required_fields = ["url"]
        self.validate_config(self.required_fields)
        self.ws = None
        self.messages = []
    
    def _do_download(self, duration: int = 10, max_messages: int = 100) -> str:
        """
        Download data from WebSocket stream.
        
        Args:
            duration: How long to listen for messages (seconds)
            max_messages: Maximum number of messages to collect
            
        Returns:
            str: Path to the downloaded file
        """
        url = self.config["url"]
        subscription_message = self.config.get("subscription_message")
        local_path = self.get_local_path()
        
        # Ensure local directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            self.logger.info(f"Connecting to WebSocket: {url}")
            
            # Create WebSocket connection
            self.ws = websocket.WebSocket()
            self.ws.connect(url)
            
            # Send subscription message if provided
            if subscription_message:
                self.logger.info(f"Sending subscription: {subscription_message}")
                self.ws.send(subscription_message)
            
            # Collect messages for specified duration
            start_time = time.time()
            message_count = 0
            
            while (time.time() - start_time) < duration and message_count < max_messages:
                try:
                    # Set timeout for receiving messages
                    self.ws.settimeout(1.0)
                    message = self.ws.recv()
                    
                    # Try to parse as JSON, fallback to raw text
                    try:
                        parsed_message = json.loads(message)
                        self.messages.append(parsed_message)
                    except json.JSONDecodeError:
                        self.messages.append({"raw_message": message, "timestamp": time.time()})
                    
                    message_count += 1
                    self.logger.debug(f"Received message {message_count}")
                    
                except websocket.WebSocketTimeoutException:
                    # No message received within timeout, continue
                    continue
                except websocket.WebSocketConnectionClosedException:
                    self.logger.warning("WebSocket connection closed")
                    break
            
            # Close connection
            self.ws.close()
            
            # Save collected messages
            with open(local_path, "w", encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successfully collected {len(self.messages)} messages → {local_path}")
            return local_path
            
        except Exception as e:
            self.logger.error(f"WebSocket download failed: {str(e)}")
            if self.ws:
                self.ws.close()
            raise Exception(f"WebSocket download failed: {str(e)}")
    
    def stream_with_callback(self, callback: Callable, duration: int = 60) -> None:
        """
        Stream data with a custom callback function.
        
        Args:
            callback: Function to call for each received message
            duration: How long to stream (seconds)
        """
        url = self.config["url"]
        subscription_message = self.config.get("subscription_message")
        
        def on_message(ws, message):
            try:
                parsed_message = json.loads(message)
                callback(parsed_message)
            except json.JSONDecodeError:
                callback({"raw_message": message, "timestamp": time.time()})
        
        def on_error(ws, error):
            self.logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.logger.info("WebSocket connection closed")
        
        def on_open(ws):
            self.logger.info("WebSocket connection opened")
            if subscription_message:
                ws.send(subscription_message)
        
        try:
            self.logger.info(f"Starting WebSocket stream: {url}")
            
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run for specified duration
            ws.run_forever()
            
        except Exception as e:
            self.logger.error(f"WebSocket streaming failed: {str(e)}")
            raise Exception(f"WebSocket streaming failed: {str(e)}")
    
    def get_latest_message(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent message from the stream.
        
        Returns:
            Dict or None: Latest message if available
        """
        if self.messages:
            return self.messages[-1]
        return None