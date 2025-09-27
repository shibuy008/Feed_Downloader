#!/usr/bin/env python3
"""
Test script for database integration.
"""
import sys
import os
import tempfile
import time
from datetime import datetime

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

def test_database_imports():
    """Test that database modules can be imported."""
    print("Testing database imports...")
    
    try:
        from database import (
            DownloadRecord, DownloadStatus, DownloadType, 
            VendorStats, SystemStats, DatabaseManager, 
            DownloadTracker, DatabaseContext
        )
        print("✓ Database modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database_creation():
    """Test database creation and schema initialization."""
    print("\nTesting database creation...")
    
    try:
        from database import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Create database manager
        db_manager = DatabaseManager(db_path)
        
        # Check if database file was created
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"✓ Database created: {db_path} ({file_size} bytes)")
            
            # Clean up
            os.unlink(db_path)
            return True
        else:
            print("✗ Database file not created")
            return False
            
    except Exception as e:
        print(f"✗ Database creation test failed: {e}")
        return False

def test_download_tracking():
    """Test download tracking functionality."""
    print("\nTesting download tracking...")
    
    try:
        from database import DatabaseManager, DownloadTracker
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Create database manager and tracker
        db_manager = DatabaseManager(db_path)
        tracker = DownloadTracker(db_manager)
        
        # Test download tracking
        vendor_name = "test_vendor"
        download_type = "on_demand"
        source_type = "rest_api"
        source_url = "https://api.example.com/data"
        local_path = "/tmp/test_file.json"
        
        # Start tracking
        download_id = db_manager.start_download(
            vendor_name=vendor_name,
            download_type=download_type,
            source_type=source_type,
            source_url=source_url,
            local_path=local_path
        )
        
        print(f"✓ Started download tracking: ID {download_id}")
        
        # Complete tracking
        db_manager.complete_download(
            download_id=download_id,
            file_size=1024
        )
        
        print(f"✓ Completed download tracking: ID {download_id}")
        
        # Test failed download
        download_id2 = db_manager.start_download(
            vendor_name=vendor_name,
            download_type=download_type,
            source_type=source_type,
            source_url=source_url,
            local_path="/tmp/test_file2.json"
        )
        
        db_manager.fail_download(
            download_id=download_id2,
            error_message="Test error"
        )
        
        print(f"✓ Failed download tracking: ID {download_id2}")
        
        # Clean up
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"✗ Download tracking test failed: {e}")
        return False

def test_statistics():
    """Test statistics generation."""
    print("\nTesting statistics generation...")
    
    try:
        from database import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        db_manager = DatabaseManager(db_path)
        
        # Create some test data
        test_downloads = [
            ("vendor1", "scheduled", "sftp", "sftp://test.com/file1.csv", "/tmp/file1.csv"),
            ("vendor1", "scheduled", "sftp", "sftp://test.com/file2.csv", "/tmp/file2.csv"),
            ("vendor2", "real_time", "rest_api", "https://api.test.com/data", "/tmp/data.json"),
        ]
        
        for vendor, dtype, stype, url, path in test_downloads:
            download_id = db_manager.start_download(vendor, dtype, stype, url, path)
            
            # Simulate some successful, some failed
            if "file1" in path:
                db_manager.complete_download(download_id, file_size=2048)
            elif "file2" in path:
                db_manager.fail_download(download_id, "Network error")
            else:
                db_manager.complete_download(download_id, file_size=512)
        
        # Test system stats
        system_stats = db_manager.get_system_stats()
        if system_stats:
            print(f"✓ System stats: {system_stats.total_downloads} downloads, {system_stats.success_rate}% success rate")
        else:
            print("✗ System stats not generated")
            return False
        
        # Test vendor stats
        vendor_stats = db_manager.get_vendor_stats()
        if vendor_stats:
            print(f"✓ Vendor stats: {len(vendor_stats)} vendors")
            for stat in vendor_stats:
                print(f"  - {stat.vendor_name}: {stat.total_downloads} downloads, {stat.success_rate}% success rate")
        else:
            print("✗ Vendor stats not generated")
            return False
        
        # Clean up
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False

def test_reporting():
    """Test reporting functionality."""
    print("\nTesting reporting functionality...")
    
    try:
        from database import DatabaseManager
        from reporting.reporter import DownloadReporter
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        db_manager = DatabaseManager(db_path)
        
        # Create test data
        download_id = db_manager.start_download(
            "test_vendor", "on_demand", "rest_api", 
            "https://api.test.com/data", "/tmp/test.json"
        )
        db_manager.complete_download(download_id, file_size=1024)
        
        # Test reporter
        reporter = DownloadReporter()
        
        # Test system overview
        overview = reporter.get_system_overview()
        if "error" not in overview:
            print(f"✓ System overview: {overview['total_downloads']} downloads")
        else:
            print(f"✗ System overview failed: {overview['error']}")
            return False
        
        # Test vendor summary
        summary = reporter.get_vendor_summary()
        if summary:
            print(f"✓ Vendor summary: {len(summary)} vendors")
        else:
            print("✗ Vendor summary failed")
            return False
        
        # Test recent activity
        activity = reporter.get_recent_activity(5)
        if activity:
            print(f"✓ Recent activity: {len(activity)} records")
        else:
            print("✗ Recent activity failed")
            return False
        
        # Clean up
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"✗ Reporting test failed: {e}")
        return False

def test_downloader_integration():
    """Test downloader integration with database."""
    print("\nTesting downloader integration...")
    
    try:
        from database import DatabaseManager
        from downloaders.base import BaseDownloader
        from downloaders.http_downloader import HTTPDownloader
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        db_manager = DatabaseManager(db_path)
        
        # Create test config
        config = {
            "name": "test_http",
            "type": "http",
            "url": "https://httpbin.org/json",
            "local_path": "/tmp/test_integration.json"
        }
        
        # Create downloader
        downloader = HTTPDownloader(config)
        
        # Test download with tracking (this will fail if URL is not accessible, but that's OK for testing)
        try:
            result = downloader.download(download_type="on_demand")
            print(f"✓ Downloader integration successful: {result}")
        except Exception as download_error:
            print(f"⚠ Download failed (expected): {download_error}")
            print("✓ Downloader integration structure working")
        
        # Check if download was tracked in database
        recent_downloads = db_manager.get_recent_downloads(1)
        if recent_downloads:
            print(f"✓ Download tracked in database: {recent_downloads[0].vendor_name}")
        else:
            print("✗ Download not tracked in database")
            return False
        
        # Clean up
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"✗ Downloader integration test failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("Feed Downloader Database Integration Tests")
    print("=" * 50)
    
    tests = [
        test_database_imports,
        test_database_creation,
        test_download_tracking,
        test_statistics,
        test_reporting,
        test_downloader_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Database Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed!")
        return 0
    else:
        print("❌ Some database tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())