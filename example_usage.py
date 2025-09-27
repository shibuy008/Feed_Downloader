#!/usr/bin/env python3
"""
Example usage of the Feed Downloader.
This script demonstrates how to use the downloader programmatically.
"""

import sys
import os
import yaml
import tempfile

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

from downloader_factory import get_downloader
from parsers.parser_factory import parse_file
from utils.decompressor import decompress


def example_rest_api_download():
    """Example: Download data from a REST API."""
    print("Example 1: REST API Download")
    print("-" * 30)
    
    # Configuration for a public API (CoinDesk Bitcoin price)
    config = {
        "name": "bitcoin_price",
        "type": "rest_api",
        "endpoint": "https://api.coindesk.com/v1/bpi/currentprice.json",
        "headers": {
            "User-Agent": "Feed-Downloader-Example/1.0"
        },
        "local_path": "./downloads/bitcoin_price.json",
        "format": "json"
    }
    
    try:
        # Create downloader
        downloader = get_downloader(config)
        
        # Download data
        print("Downloading Bitcoin price data...")
        local_file = downloader.download()
        print(f"Downloaded to: {local_file}")
        
        # Parse the JSON data
        print("Parsing JSON data...")
        df = parse_file(local_file, "json")
        print(f"Parsed data shape: {df.shape}")
        print("Sample data:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_http_download():
    """Example: Download a CSV file from HTTP."""
    print("\nExample 2: HTTP File Download")
    print("-" * 30)
    
    # Configuration for downloading a sample CSV file
    config = {
        "name": "sample_csv",
        "type": "http",
        "url": "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv",
        "headers": {
            "User-Agent": "Feed-Downloader-Example/1.0"
        },
        "local_path": "./downloads/covid_data.csv",
        "format": "csv"
    }
    
    try:
        # Create downloader
        downloader = get_downloader(config)
        
        # Download data
        print("Downloading COVID-19 data...")
        local_file = downloader.download()
        print(f"Downloaded to: {local_file}")
        
        # Parse the CSV data
        print("Parsing CSV data...")
        df = parse_file(local_file, "csv")
        print(f"Parsed data shape: {df.shape}")
        print("Sample data:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_websocket_download():
    """Example: Download data from WebSocket (using a test endpoint)."""
    print("\nExample 3: WebSocket Download")
    print("-" * 30)
    
    # Configuration for a test WebSocket endpoint
    config = {
        "name": "test_websocket",
        "type": "websocket",
        "url": "wss://ws.postman-echo.com/raw",
        "subscription_message": "Hello WebSocket Test",
        "local_path": "./downloads/websocket_test.json",
        "format": "json",
        "duration": 5,  # Collect for 5 seconds
        "max_messages": 10
    }
    
    try:
        # Create downloader
        downloader = get_downloader(config)
        
        # Download data
        print("Connecting to WebSocket and collecting data...")
        local_file = downloader.download()
        print(f"Data saved to: {local_file}")
        
        # Parse the JSON data
        print("Parsing WebSocket data...")
        df = parse_file(local_file, "json")
        print(f"Parsed data shape: {df.shape}")
        print("Sample data:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def example_compression():
    """Example: Handle compressed files."""
    print("\nExample 4: File Compression")
    print("-" * 30)
    
    # Create a temporary ZIP file for demonstration
    import zipfile
    import tempfile
    
    # Create a sample CSV content
    csv_content = """name,age,city
John,25,New York
Jane,30,Los Angeles
Bob,35,Chicago"""
    
    # Create a temporary ZIP file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        with zipfile.ZipFile(temp_zip.name, 'w') as zf:
            zf.writestr('sample.csv', csv_content)
        
        zip_path = temp_zip.name
    
    try:
        print(f"Created temporary ZIP file: {zip_path}")
        
        # Decompress the file
        print("Decompressing ZIP file...")
        extracted_files = decompress(zip_path, "zip")
        print(f"Extracted files: {extracted_files}")
        
        # Parse the extracted CSV
        if extracted_files:
            print("Parsing extracted CSV...")
            df = parse_file(extracted_files[0], "csv")
            print(f"Parsed data shape: {df.shape}")
            print("Sample data:")
            print(df.head())
        
        # Clean up
        os.unlink(zip_path)
        for file_path in extracted_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all examples."""
    print("Feed Downloader Examples")
    print("=" * 50)
    
    # Create downloads directory
    os.makedirs("./downloads", exist_ok=True)
    
    examples = [
        example_rest_api_download,
        example_http_download,
        example_websocket_download,
        example_compression
    ]
    
    successful = 0
    total = len(examples)
    
    for example in examples:
        try:
            if example():
                successful += 1
        except Exception as e:
            print(f"Example failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Examples completed: {successful}/{total} successful")
    
    if successful > 0:
        print("\nCheck the ./downloads/ directory for downloaded files!")
    
    return 0 if successful == total else 1


if __name__ == "__main__":
    sys.exit(main())