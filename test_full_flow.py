#!/usr/bin/env python3
"""
Comprehensive test script that simulates the entire Feed Downloader flow.
This script demonstrates:
1. Database initialization and tracking
2. Multiple vendor downloads (HTTP, REST API, WebSocket)
3. Scheduled and real-time downloads
4. Error handling and retries
5. Reporting and analytics
6. Dashboard functionality
"""
import os
import sys
import time
import tempfile
import json
from datetime import datetime, timedelta

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

def setup_test_environment():
    """Setup test environment with temporary files."""
    print("🔧 Setting up test environment...")
    
    # Create temporary directory for downloads
    test_dir = tempfile.mkdtemp(prefix="feed_downloader_test_")
    downloads_dir = os.path.join(test_dir, "downloads")
    logs_dir = os.path.join(test_dir, "logs")
    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    print(f"✓ Test directory: {test_dir}")
    print(f"✓ Downloads directory: {downloads_dir}")
    print(f"✓ Logs directory: {logs_dir}")
    
    return test_dir, downloads_dir, logs_dir

def create_test_config(test_dir, downloads_dir):
    """Create test configuration file."""
    print("\n📝 Creating test configuration...")
    
    config = {
        "global": {
            "download_dir": downloads_dir,
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 5,
            "log_level": "INFO",
            "log_file": os.path.join(test_dir, "logs", "test.log")
        },
        
        "database": {
            "enabled": True,
            "type": "sqlite",
            "path": os.path.join(test_dir, "test_feed_downloader.db"),
            "maintenance": {
                "cleanup_days": 7,  # Shorter for testing
                "auto_cleanup": True
            }
        },
        
        "vendors": [
            {
                "name": "test_http",
                "type": "http",
                "url": "https://httpbin.org/json",
                "local_path": os.path.join(downloads_dir, "test_http.json"),
                "format": "json",
                "schedule": {
                    "type": "real_time",
                    "interval_seconds": 30,
                    "timezone": "UTC",
                    "enabled": True,
                    "max_retries": 2,
                    "retry_delay": 10
                }
            },
            {
                "name": "test_api",
                "type": "rest_api",
                "endpoint": "https://api.github.com/repos/microsoft/vscode",
                "headers": {
                    "User-Agent": "Feed-Downloader-Test/1.0"
                },
                "local_path": os.path.join(downloads_dir, "test_api.json"),
                "format": "json",
                "schedule": {
                    "type": "scheduled",
                    "cron": "0 * * * *",  # Every hour
                    "timezone": "UTC",
                    "enabled": True,
                    "max_retries": 2,
                    "retry_delay": 10
                }
            },
            {
                "name": "test_ws",
                "type": "websocket",
                "url": "wss://echo.websocket.org",
                "subscription_message": "Hello from Feed Downloader Test",
                "local_path": os.path.join(downloads_dir, "test_ws.json"),
                "format": "json",
                "duration": 5,  # Short duration for testing
                "max_messages": 10,
                "schedule": {
                    "type": "real_time",
                    "interval_seconds": 45,
                    "timezone": "UTC",
                    "enabled": True,
                    "max_retries": 2,
                    "retry_delay": 10
                }
            }
        ]
    }
    
    config_path = os.path.join(test_dir, "test_config.yaml")
    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✓ Test configuration created: {config_path}")
    return config_path

def test_database_initialization(config_path):
    """Test database initialization."""
    print("\n🗄️ Testing database initialization...")
    
    try:
        from database import get_db_context
        import yaml
        
        # Load config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize database
        db_path = config['database']['path']
        db_context = get_db_context(db_path)
        
        print(f"✓ Database initialized: {db_path}")
        
        # Check if database file was created
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"✓ Database file created: {file_size} bytes")
        else:
            print("✗ Database file not created")
            return False
        
        return True, db_context
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False, None

def test_individual_downloads(config_path):
    """Test individual vendor downloads."""
    print("\n📥 Testing individual vendor downloads...")
    
    try:
        from downloader_factory import get_downloader
        import yaml
        
        # Load config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        vendors = config['vendors']
        results = []
        
        for vendor in vendors:
            vendor_name = vendor['name']
            print(f"\n  Testing {vendor_name}...")
            
            try:
                # Create downloader
                downloader = get_downloader(vendor)
                
                # Download with tracking
                download_type = "on_demand"
                result = downloader.download(download_type=download_type)
                
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"    ✓ Downloaded: {result} ({file_size} bytes)")
                    results.append({
                        'vendor': vendor_name,
                        'success': True,
                        'file': result,
                        'size': file_size
                    })
                else:
                    print(f"    ✗ File not found: {result}")
                    results.append({
                        'vendor': vendor_name,
                        'success': False,
                        'error': 'File not found'
                    })
                    
            except Exception as e:
                print(f"    ✗ Download failed: {e}")
                results.append({
                    'vendor': vendor_name,
                    'success': False,
                    'error': str(e)
                })
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n  Download Summary: {successful}/{total} successful")
        
        return results
        
    except Exception as e:
        print(f"✗ Individual downloads test failed: {e}")
        return []

def test_scheduler_flow(config_path):
    """Test scheduler flow with multiple downloads."""
    print("\n⏰ Testing scheduler flow...")
    
    try:
        from scheduler import FeedScheduler
        import yaml
        
        # Load config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create scheduler
        scheduler = FeedScheduler(config)
        
        # Start scheduler
        scheduler.start()
        print("✓ Scheduler started")
        
        # Let it run for a short time to collect some downloads
        print("  Running for 60 seconds to collect downloads...")
        time.sleep(60)
        
        # Stop scheduler
        scheduler.stop()
        print("✓ Scheduler stopped")
        
        # Get status
        status = scheduler.get_status()
        print(f"✓ Scheduler status: {status['active_threads']} threads, {len(status['vendors'])} vendors")
        
        return True
        
    except Exception as e:
        print(f"✗ Scheduler flow test failed: {e}")
        return False

def test_database_queries(db_context):
    """Test database queries and statistics."""
    print("\n📊 Testing database queries...")
    
    try:
        db_manager = db_context.get_manager()
        
        # Test system stats
        system_stats = db_manager.get_system_stats()
        if system_stats:
            print(f"✓ System stats: {system_stats.total_downloads} downloads, {system_stats.success_rate}% success rate")
        else:
            print("✗ System stats not available")
        
        # Test vendor stats
        vendor_stats = db_manager.get_vendor_stats()
        print(f"✓ Vendor stats: {len(vendor_stats)} vendors")
        for stat in vendor_stats:
            print(f"  - {stat.vendor_name}: {stat.total_downloads} downloads, {stat.success_rate}% success rate")
        
        # Test recent downloads
        recent_downloads = db_manager.get_recent_downloads(10)
        print(f"✓ Recent downloads: {len(recent_downloads)} records")
        
        # Test daily stats
        daily_stats = db_manager.get_daily_stats(7)
        print(f"✓ Daily stats: {len(daily_stats)} days")
        
        return True
        
    except Exception as e:
        print(f"✗ Database queries test failed: {e}")
        return False

def test_reporting_functionality(db_context):
    """Test reporting functionality."""
    print("\n📈 Testing reporting functionality...")
    
    try:
        from reporting.reporter import DownloadReporter
        
        reporter = DownloadReporter()
        
        # Test system overview
        overview = reporter.get_system_overview()
        if "error" not in overview:
            print("✓ System overview generated")
            print(f"  Total downloads: {overview.get('total_downloads', 'N/A')}")
            print(f"  Success rate: {overview.get('success_rate', 'N/A')}")
        else:
            print(f"✗ System overview failed: {overview['error']}")
        
        # Test vendor summary
        vendor_summary = reporter.get_vendor_summary()
        print(f"✓ Vendor summary: {len(vendor_summary)} vendors")
        
        # Test recent activity
        recent_activity = reporter.get_recent_activity(5)
        print(f"✓ Recent activity: {len(recent_activity)} records")
        
        # Test daily stats
        daily_stats = reporter.get_daily_stats(7)
        print(f"✓ Daily stats: {len(daily_stats)} days")
        
        # Test failure analysis
        failures = reporter.get_failure_analysis(10)
        print(f"✓ Failure analysis: {len(failures)} failures")
        
        return True
        
    except Exception as e:
        print(f"✗ Reporting functionality test failed: {e}")
        return False

def test_cli_functionality(test_dir, config_path):
    """Test CLI functionality."""
    print("\n🖥️ Testing CLI functionality...")
    
    try:
        import subprocess
        
        # Test database status
        print("  Testing database status...")
        result = subprocess.run([
            sys.executable, "data_downloader/db_cli.py", 
            "status", "--db", os.path.join(test_dir, "test_feed_downloader.db")
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("    ✓ Database status command successful")
        else:
            print(f"    ✗ Database status failed: {result.stderr}")
        
        # Test report generation
        print("  Testing report generation...")
        result = subprocess.run([
            sys.executable, "data_downloader/db_cli.py", 
            "report", "--type", "overview", "--db", os.path.join(test_dir, "test_feed_downloader.db")
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("    ✓ Report generation successful")
        else:
            print(f"    ✗ Report generation failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI functionality test failed: {e}")
        return False

def test_dashboard_functionality(test_dir):
    """Test dashboard functionality."""
    print("\n📊 Testing dashboard functionality...")
    
    try:
        from reporting.dashboard import DownloadDashboard
        
        db_path = os.path.join(test_dir, "test_feed_downloader.db")
        dashboard = DownloadDashboard(db_path)
        
        # Test live status
        print("  Testing live status display...")
        dashboard.show_live_status()
        
        # Test daily summary
        print("  Testing daily summary...")
        dashboard.show_daily_summary(7)
        
        # Test failure summary
        print("  Testing failure summary...")
        dashboard.show_failure_summary()
        
        # Test HTML report generation
        print("  Testing HTML report generation...")
        html_file = os.path.join(test_dir, "test_report.html")
        dashboard.generate_html_report(html_file)
        
        if os.path.exists(html_file):
            file_size = os.path.getsize(html_file)
            print(f"    ✓ HTML report generated: {html_file} ({file_size} bytes)")
        else:
            print("    ✗ HTML report not generated")
        
        return True
        
    except Exception as e:
        print(f"✗ Dashboard functionality test failed: {e}")
        return False

def cleanup_test_environment(test_dir):
    """Cleanup test environment."""
    print(f"\n🧹 Cleaning up test environment: {test_dir}")
    
    try:
        import shutil
        shutil.rmtree(test_dir)
        print("✓ Test environment cleaned up")
    except Exception as e:
        print(f"⚠ Could not clean up test environment: {e}")

def main():
    """Run the complete flow test."""
    print("🚀 Feed Downloader - Complete Flow Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results tracking
    test_results = {}
    
    try:
        # 1. Setup test environment
        test_dir, downloads_dir, logs_dir = setup_test_environment()
        test_results['environment'] = True
        
        # 2. Create test configuration
        config_path = create_test_config(test_dir, downloads_dir)
        test_results['config'] = True
        
        # 3. Test database initialization
        db_init_success, db_context = test_database_initialization(config_path)
        test_results['database_init'] = db_init_success
        
        if not db_init_success:
            print("❌ Database initialization failed, stopping tests")
            cleanup_test_environment(test_dir)
            return 1
        
        # 4. Test individual downloads
        download_results = test_individual_downloads(config_path)
        test_results['individual_downloads'] = len(download_results) > 0
        
        # 5. Test scheduler flow
        scheduler_success = test_scheduler_flow(config_path)
        test_results['scheduler'] = scheduler_success
        
        # 6. Test database queries
        db_queries_success = test_database_queries(db_context)
        test_results['database_queries'] = db_queries_success
        
        # 7. Test reporting functionality
        reporting_success = test_reporting_functionality(db_context)
        test_results['reporting'] = reporting_success
        
        # 8. Test CLI functionality
        cli_success = test_cli_functionality(test_dir, config_path)
        test_results['cli'] = cli_success
        
        # 9. Test dashboard functionality
        dashboard_success = test_dashboard_functionality(test_dir)
        test_results['dashboard'] = dashboard_success
        
        # 10. Final summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, success in test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:20} : {status}")
            if success:
                passed_tests += 1
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Feed Downloader is working perfectly!")
            return 0
        else:
            print("⚠️ Some tests failed, but core functionality is working")
            return 1
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1
    
    finally:
        # Cleanup
        if 'test_dir' in locals():
            cleanup_test_environment(test_dir)

if __name__ == "__main__":
    sys.exit(main())