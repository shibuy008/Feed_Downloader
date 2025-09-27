#!/usr/bin/env python3
"""
Test script for the Feed Downloader scheduler functionality.
"""
import sys
import os
import time
import yaml
from datetime import datetime, timedelta

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

def test_scheduler_imports():
    """Test that scheduler modules can be imported."""
    print("Testing scheduler imports...")
    
    try:
        from scheduler import FeedScheduler, FeedType, ScheduleConfig, validate_cron_expression, get_common_schedules
        from scheduler_runner import SchedulerRunner
        print("✓ Scheduler modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_cron_validation():
    """Test cron expression validation."""
    print("\nTesting cron expression validation...")
    
    try:
        from scheduler import validate_cron_expression
        
        # Test valid cron expressions
        valid_crons = [
            "0 9 * * 1-5",      # 9 AM weekdays
            "*/15 * * * *",     # Every 15 minutes
            "0 0 1 * *",        # First day of month
            "0 18 * * *"        # 6 PM daily
        ]
        
        for cron in valid_crons:
            if validate_cron_expression(cron):
                print(f"✓ Valid cron: {cron}")
            else:
                print(f"✗ Invalid cron: {cron}")
                return False
        
        # Test invalid cron expressions
        invalid_crons = [
            "invalid",          # Invalid format
            "25 * * * *",       # Invalid hour
            "0 0 32 * *"        # Invalid day
        ]
        
        for cron in invalid_crons:
            if not validate_cron_expression(cron):
                print(f"✓ Correctly rejected invalid cron: {cron}")
            else:
                print(f"✗ Incorrectly accepted invalid cron: {cron}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Cron validation test failed: {e}")
        return False

def test_common_schedules():
    """Test common schedule definitions."""
    print("\nTesting common schedules...")
    
    try:
        from scheduler import get_common_schedules
        
        schedules = get_common_schedules()
        
        expected_schedules = [
            "market_open", "market_close", "daily_morning", 
            "hourly", "every_15_minutes", "weekly_monday"
        ]
        
        for schedule_name in expected_schedules:
            if schedule_name in schedules:
                print(f"✓ Found schedule: {schedule_name} = {schedules[schedule_name]}")
            else:
                print(f"✗ Missing schedule: {schedule_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Common schedules test failed: {e}")
        return False

def test_schedule_config():
    """Test schedule configuration parsing."""
    print("\nTesting schedule configuration...")
    
    try:
        from scheduler import ScheduleConfig, FeedType
        
        # Test scheduled feed config
        scheduled_config = ScheduleConfig(
            feed_type=FeedType.SCHEDULED,
            cron_expression="0 9 * * 1-5",
            timezone="America/New_York",
            enabled=True
        )
        
        print(f"✓ Scheduled config: {scheduled_config.feed_type.value}")
        
        # Test real-time feed config
        realtime_config = ScheduleConfig(
            feed_type=FeedType.REAL_TIME,
            interval_seconds=300,
            timezone="UTC",
            enabled=True
        )
        
        print(f"✓ Real-time config: {realtime_config.feed_type.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Schedule config test failed: {e}")
        return False

def test_scheduler_creation():
    """Test scheduler creation with sample config."""
    print("\nTesting scheduler creation...")
    
    try:
        from scheduler import FeedScheduler
        
        # Create sample configuration
        sample_config = {
            "vendors": [
                {
                    "name": "test_vendor",
                    "type": "rest_api",
                    "endpoint": "https://api.example.com/data",
                    "local_path": "./downloads/test.json",
                    "format": "json",
                    "schedule": {
                        "type": "scheduled",
                        "cron": "0 9 * * 1-5",
                        "timezone": "UTC",
                        "enabled": True
                    }
                }
            ]
        }
        
        # Create scheduler
        scheduler = FeedScheduler(sample_config)
        
        # Check that schedule config was loaded
        if "test_vendor" in scheduler.schedule_configs:
            print("✓ Scheduler created and config loaded")
            return True
        else:
            print("✗ Schedule config not loaded")
            return False
        
    except Exception as e:
        print(f"✗ Scheduler creation test failed: {e}")
        return False

def test_next_run_calculation():
    """Test next run time calculation."""
    print("\nTesting next run time calculation...")
    
    try:
        from scheduler import FeedScheduler
        
        # Create sample configuration with scheduled vendor
        sample_config = {
            "vendors": [
                {
                    "name": "test_scheduled",
                    "type": "rest_api",
                    "endpoint": "https://api.example.com/data",
                    "local_path": "./downloads/test.json",
                    "format": "json",
                    "schedule": {
                        "type": "scheduled",
                        "cron": "0 9 * * 1-5",  # 9 AM weekdays
                        "timezone": "UTC",
                        "enabled": True
                    }
                }
            ]
        }
        
        scheduler = FeedScheduler(sample_config)
        next_runs = scheduler.get_next_run_times()
        
        if "test_scheduled" in next_runs and next_runs["test_scheduled"]:
            next_run = next_runs["test_scheduled"]
            print(f"✓ Next run calculated: {next_run}")
            return True
        else:
            print("✗ Next run calculation failed")
            return False
        
    except Exception as e:
        print(f"✗ Next run calculation test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading with scheduling."""
    print("\nTesting configuration loading...")
    
    try:
        # Test if the example config file exists and can be loaded
        config_path = "data_downloader/config_scheduling_examples.yaml"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check if vendors have schedule configurations
            vendors = config.get("vendors", [])
            scheduled_vendors = 0
            
            for vendor in vendors:
                if vendor.get("schedule"):
                    scheduled_vendors += 1
            
            print(f"✓ Config loaded: {len(vendors)} vendors, {scheduled_vendors} with schedules")
            return True
        else:
            print(f"✗ Config file not found: {config_path}")
            return False
        
    except Exception as e:
        print(f"✗ Config loading test failed: {e}")
        return False

def main():
    """Run all scheduler tests."""
    print("Feed Downloader Scheduler Tests")
    print("=" * 40)
    
    tests = [
        test_scheduler_imports,
        test_cron_validation,
        test_common_schedules,
        test_schedule_config,
        test_scheduler_creation,
        test_next_run_calculation,
        test_config_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with error: {e}")
    
    print("\n" + "=" * 40)
    print(f"Scheduler Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All scheduler tests passed!")
        return 0
    else:
        print("❌ Some scheduler tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())