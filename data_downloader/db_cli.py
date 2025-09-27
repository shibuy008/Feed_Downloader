"""
Command-line interface for database operations and reporting.
"""
import argparse
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_context
from reporting.reporter import DownloadReporter


def setup_logging():
    """Setup basic logging for CLI."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cmd_status(args):
    """Show database status and system overview."""
    print("Database Status:")
    print(f"Database file: {args.db}")
    print(f"Database exists: {os.path.exists(args.db)}")
    
    if os.path.exists(args.db):
        file_size = os.path.getsize(args.db)
        print(f"Database size: {file_size:,} bytes")
        
        # Show system overview
        db_context = get_db_context(args.db)
        reporter = DownloadReporter()
        reporter.print_system_overview()


def cmd_report(args):
    """Generate reports."""
    reporter = DownloadReporter()
    
    if args.type == "overview":
        reporter.print_system_overview()
    elif args.type == "vendors":
        reporter.print_vendor_summary(args.vendor)
    elif args.type == "activity":
        reporter.print_recent_activity(args.limit)
    elif args.type == "daily":
        reporter.print_daily_stats(args.days)
    elif args.type == "failures":
        reporter.print_failure_analysis(args.limit)
    elif args.type == "complete":
        reporter.print_complete_report()
    else:
        print(f"Unknown report type: {args.type}")


def cmd_export(args):
    """Export data to CSV."""
    reporter = DownloadReporter()
    
    try:
        filename = reporter.export_to_csv(args.output)
        print(f"Exported data to: {filename}")
    except Exception as e:
        print(f"Export failed: {e}")


def cmd_cleanup(args):
    """Clean up old records."""
    db_context = get_db_context(args.db)
    db_manager = db_context.get_manager()
    
    try:
        print(f"Cleaning up records older than {args.days} days...")
        db_manager.cleanup_old_records(args.days)
        print("Cleanup completed successfully")
    except Exception as e:
        print(f"Cleanup failed: {e}")


def cmd_reset(args):
    """Reset database (WARNING: This will delete all data)."""
    if not args.force:
        confirm = input("Are you sure you want to reset the database? This will delete ALL data! (yes/no): ")
        if confirm.lower() != "yes":
            print("Database reset cancelled")
            return
    
    try:
        if os.path.exists(args.db):
            os.remove(args.db)
            print(f"Database file {args.db} removed")
        
        # Reinitialize database
        db_context = get_db_context(args.db)
        db_manager = db_context.get_manager()
        print("Database reinitialized successfully")
    except Exception as e:
        print(f"Database reset failed: {e}")


def cmd_vendor_details(args):
    """Show detailed information for a specific vendor."""
    reporter = DownloadReporter()
    
    # Get vendor summary
    vendor_summary = reporter.get_vendor_summary(args.vendor)
    
    if not vendor_summary:
        print(f"No data found for vendor: {args.vendor}")
        return
    
    vendor_data = vendor_summary[0]
    
    print(f"Vendor Details: {args.vendor}")
    print("=" * 50)
    print(f"Total Downloads: {vendor_data['total_downloads']}")
    print(f"Successful: {vendor_data['successful']}")
    print(f"Failed: {vendor_data['failed']}")
    print(f"Success Rate: {vendor_data['success_rate']}")
    print(f"Average Duration: {vendor_data['avg_duration']}")
    print(f"Total Data Size: {vendor_data['total_size']}")
    print(f"Last Download: {vendor_data['last_download']}")
    print(f"Last Success: {vendor_data['last_success']}")
    print(f"Last Failure: {vendor_data['last_failure']}")
    print()
    
    # Show recent activity for this vendor
    print("Recent Activity:")
    print("-" * 30)
    
    db_context = get_db_context(args.db)
    db_manager = db_context.get_manager()
    recent_downloads = db_manager.get_vendor_downloads(args.vendor, limit=10)
    
    if recent_downloads:
        for download in recent_downloads:
            status_symbol = "✓" if download.status == "completed" else "✗" if download.status == "failed" else "?"
            print(f"{status_symbol} {download.start_time.strftime('%Y-%m-%d %H:%M:%S') if download.start_time else 'N/A'} - {download.status} - {download.source_type}")
    else:
        print("No recent activity found")


def cmd_monitor(args):
    """Monitor real-time activity."""
    import time
    from datetime import datetime
    
    reporter = DownloadReporter()
    
    print("Real-time Monitor (Press Ctrl+C to stop)")
    print("=" * 50)
    
    try:
        while True:
            # Clear screen (works on Unix-like systems)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"Feed Downloader Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Show system overview
            overview = reporter.get_system_overview()
            if "error" not in overview:
                print(f"Total Downloads: {overview['total_downloads']}")
                print(f"Success Rate: {overview['success_rate']}")
                print(f"Active Vendors: {overview['active_vendors']}")
                print()
            
            # Show recent activity
            print("Recent Activity:")
            print("-" * 30)
            activity = reporter.get_recent_activity(5)
            
            for record in activity:
                status_symbol = "✓" if record['status'] == "completed" else "✗" if record['status'] == "failed" else "?"
                print(f"{status_symbol} {record['vendor']} - {record['status']} - {record['start_time']}")
            
            print()
            print("Refreshing in 10 seconds... (Press Ctrl+C to stop)")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nMonitor stopped")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Feed Downloader Database CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python db_cli.py status                    # Show database status
  python db_cli.py report --type overview    # Show system overview
  python db_cli.py report --type vendors     # Show vendor summary
  python db_cli.py report --type activity    # Show recent activity
  python db_cli.py report --type complete    # Show complete report
  python db_cli.py export --output report.csv # Export to CSV
  python db_cli.py vendor-details vendor_api # Show vendor details
  python db_cli.py monitor                   # Real-time monitoring
  python db_cli.py cleanup --days 90         # Clean old records
        """
    )
    
    parser.add_argument(
        "--db", 
        default="feed_downloader.db", 
        help="Database file path"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show database status")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument(
        "--type", 
        choices=["overview", "vendors", "activity", "daily", "failures", "complete"],
        default="overview",
        help="Report type"
    )
    report_parser.add_argument("--vendor", help="Specific vendor name")
    report_parser.add_argument("--limit", type=int, default=20, help="Number of records to show")
    report_parser.add_argument("--days", type=int, default=7, help="Number of days for daily stats")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument("--output", help="Output filename")
    
    # Vendor details command
    vendor_parser = subparsers.add_parser("vendor-details", help="Show vendor details")
    vendor_parser.add_argument("vendor", help="Vendor name")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Real-time monitoring")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old records")
    cleanup_parser.add_argument("--days", type=int, default=90, help="Days to keep")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset database (WARNING: deletes all data)")
    reset_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging()
    
    # Database path is handled by get_db_context() calls in individual commands
    
    try:
        # Execute command
        if args.command == "status":
            cmd_status(args)
        elif args.command == "report":
            cmd_report(args)
        elif args.command == "export":
            cmd_export(args)
        elif args.command == "vendor-details":
            cmd_vendor_details(args)
        elif args.command == "monitor":
            cmd_monitor(args)
        elif args.command == "cleanup":
            cmd_cleanup(args)
        elif args.command == "reset":
            cmd_reset(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"Command failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())