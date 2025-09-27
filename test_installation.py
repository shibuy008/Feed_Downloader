#!/usr/bin/env python3
"""
Test script to verify Feed Downloader installation and basic functionality.
"""

import sys
import os

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test core imports
        from downloader_factory import get_downloader, get_supported_types
        from parsers.parser_factory import parse_file, get_supported_formats
        from utils.decompressor import decompress
        
        print("✓ Core modules imported successfully")
        
        # Test downloader imports
        from downloaders import (
            BaseDownloader, 
            SFTPDownloader, 
            RESTAPIDownloader, 
            WebSocketDownloader, 
            HTTPDownloader
        )
        print("✓ Downloader modules imported successfully")
        
        # Test parser imports
        from parsers import (
            parse_csv, parse_json, parse_xml, parse_excel
        )
        print("✓ Parser modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_supported_types():
    """Test that supported types are returned correctly."""
    print("\nTesting supported types...")
    
    try:
        from downloader_factory import get_supported_types
        from parsers.parser_factory import get_supported_formats
        
        downloader_types = get_supported_types()
        parser_formats = get_supported_formats()
        
        print(f"✓ Supported downloader types: {downloader_types}")
        print(f"✓ Supported parser formats: {parser_formats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error getting supported types: {e}")
        return False

def test_config_validation():
    """Test configuration validation."""
    print("\nTesting configuration validation...")
    
    try:
        from downloader_factory import validate_config
        
        # Test valid SFTP config
        sftp_config = {
            "name": "test_sftp",
            "type": "sftp",
            "host": "test.com",
            "username": "user",
            "password": "pass",
            "remote_path": "/test.csv",
            "local_path": "./test.csv"
        }
        
        if validate_config(sftp_config):
            print("✓ SFTP configuration validation works")
        else:
            print("✗ SFTP configuration validation failed")
            return False
        
        # Test valid REST API config
        api_config = {
            "name": "test_api",
            "type": "rest_api",
            "endpoint": "https://api.test.com/data",
            "local_path": "./test.json"
        }
        
        if validate_config(api_config):
            print("✓ REST API configuration validation works")
        else:
            print("✗ REST API configuration validation failed")
            return False
        
        # Test invalid config
        invalid_config = {
            "name": "test_invalid",
            "type": "unknown_type",
            "local_path": "./test.csv"
        }
        
        if not validate_config(invalid_config):
            print("✓ Invalid configuration correctly rejected")
        else:
            print("✗ Invalid configuration incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation error: {e}")
        return False

def test_downloader_creation():
    """Test downloader creation from factory."""
    print("\nTesting downloader creation...")
    
    try:
        from downloader_factory import get_downloader
        
        # Test SFTP downloader creation
        sftp_config = {
            "name": "test_sftp",
            "type": "sftp",
            "host": "test.com",
            "username": "user",
            "password": "pass",
            "remote_path": "/test.csv",
            "local_path": "./test.csv"
        }
        
        sftp_downloader = get_downloader(sftp_config)
        print(f"✓ SFTP downloader created: {type(sftp_downloader).__name__}")
        
        # Test REST API downloader creation
        api_config = {
            "name": "test_api",
            "type": "rest_api",
            "endpoint": "https://api.test.com/data",
            "local_path": "./test.json"
        }
        
        api_downloader = get_downloader(api_config)
        print(f"✓ REST API downloader created: {type(api_downloader).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Downloader creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("Feed Downloader Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_supported_types,
        test_config_validation,
        test_downloader_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Feed Downloader is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())