"""
Simple dashboard for download activity monitoring.
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from .reporter import DownloadReporter


class DownloadDashboard:
    """
    Simple dashboard for download monitoring.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize dashboard.
        
        Args:
            db_path: Database path (optional)
        """
        self.db_context = get_db_context(db_path)
        self.reporter = DownloadReporter()
    
    def show_live_status(self):
        """Show live status of the downloader."""
        print("=" * 60)
        print("FEED DOWNLOADER - LIVE STATUS")
        print("=" * 60)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System overview
        overview = self.reporter.get_system_overview()
        if "error" not in overview:
            print("SYSTEM STATUS:")
            print(f"  Total Downloads: {overview['total_downloads']}")
            print(f"  Success Rate: {overview['success_rate']}")
            print(f"  Active Vendors: {overview['active_vendors']}")
            print(f"  Uptime: {overview['uptime_hours']}")
            print(f"  Total Data: {overview['total_data_size']}")
            print()
        
        # Recent activity
        print("RECENT ACTIVITY:")
        activity = self.reporter.get_recent_activity(5)
        if activity:
            for record in activity:
                status_symbol = "✓" if record['status'] == "completed" else "✗" if record['status'] == "failed" else "?"
                print(f"  {status_symbol} {record['vendor']} - {record['status']} - {record['start_time']}")
        else:
            print("  No recent activity")
        print()
        
        # Top vendors
        print("TOP VENDORS:")
        vendors = self.reporter.get_vendor_summary()
        if vendors:
            for vendor in vendors[:3]:  # Top 3
                print(f"  {vendor['vendor_name']}: {vendor['total_downloads']} downloads ({vendor['success_rate']} success)")
        else:
            print("  No vendor data available")
        print()
    
    def show_daily_summary(self, days: int = 7):
        """Show daily summary for the last N days."""
        print("=" * 60)
        print(f"DAILY SUMMARY - LAST {days} DAYS")
        print("=" * 60)
        
        daily_stats = self.reporter.get_daily_stats(days)
        if daily_stats:
            for day in daily_stats:
                print(f"{day['date']}: {day['total_downloads']} downloads, {day['success_rate']} success rate")
        else:
            print("No daily data available")
        print()
    
    def show_failure_summary(self):
        """Show failure summary."""
        print("=" * 60)
        print("FAILURE SUMMARY")
        print("=" * 60)
        
        failures = self.reporter.get_failure_analysis(10)
        if failures:
            for failure in failures:
                print(f"✗ {failure['vendor']} ({failure['source_type']}): {failure['error'][:50]}...")
        else:
            print("No recent failures")
        print()
    
    def generate_html_report(self, output_file: str = None):
        """
        Generate HTML report.
        
        Args:
            output_file: Output HTML file path
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"download_report_{timestamp}.html"
        
        # Get data
        overview = self.reporter.get_system_overview()
        vendors = self.reporter.get_vendor_summary()
        activity = self.reporter.get_recent_activity(20)
        daily_stats = self.reporter.get_daily_stats(7)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Feed Downloader Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .pending {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Feed Downloader Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>System Overview</h2>
        <div class="metric">Total Downloads: {overview.get('total_downloads', 'N/A')}</div>
        <div class="metric">Success Rate: {overview.get('success_rate', 'N/A')}</div>
        <div class="metric">Active Vendors: {overview.get('active_vendors', 'N/A')}</div>
        <div class="metric">Uptime: {overview.get('uptime_hours', 'N/A')}</div>
        <div class="metric">Total Data: {overview.get('total_data_size', 'N/A')}</div>
    </div>
    
    <div class="section">
        <h2>Vendor Summary</h2>
        <table>
            <tr><th>Vendor</th><th>Total</th><th>Success</th><th>Failed</th><th>Success Rate</th><th>Last Download</th></tr>
        """
        
        for vendor in vendors:
            html += f"""
            <tr>
                <td>{vendor['vendor_name']}</td>
                <td>{vendor['total_downloads']}</td>
                <td>{vendor['successful']}</td>
                <td>{vendor['failed']}</td>
                <td>{vendor['success_rate']}</td>
                <td>{vendor['last_download']}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Recent Activity</h2>
        <table>
            <tr><th>Vendor</th><th>Type</th><th>Status</th><th>Start Time</th><th>Duration</th><th>Size</th></tr>
        """
        
        for record in activity:
            status_class = "success" if record['status'] == "completed" else "failure" if record['status'] == "failed" else "pending"
            html += f"""
            <tr>
                <td>{record['vendor']}</td>
                <td>{record['type']}</td>
                <td class="{status_class}">{record['status']}</td>
                <td>{record['start_time']}</td>
                <td>{record['duration']}</td>
                <td>{record['file_size']}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Daily Statistics (Last 7 Days)</h2>
        <table>
            <tr><th>Date</th><th>Total</th><th>Success</th><th>Failed</th><th>Success Rate</th><th>Avg Duration</th></tr>
        """
        
        for day in daily_stats:
            html += f"""
            <tr>
                <td>{day['date']}</td>
                <td>{day['total_downloads']}</td>
                <td>{day['successful']}</td>
                <td>{day['failed']}</td>
                <td>{day['success_rate']}</td>
                <td>{day['avg_duration']}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
</body>
</html>
        """
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML report generated: {output_file}")
        return output_file


def main():
    """Main dashboard entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Feed Downloader Dashboard")
    parser.add_argument("--db", default="feed_downloader.db", help="Database file path")
    parser.add_argument("--html", help="Generate HTML report to specified file")
    parser.add_argument("--days", type=int, default=7, help="Days for daily summary")
    
    args = parser.parse_args()
    
    dashboard = DownloadDashboard(args.db)
    
    if args.html:
        dashboard.generate_html_report(args.html)
    else:
        dashboard.show_live_status()
        dashboard.show_daily_summary(args.days)
        dashboard.show_failure_summary()


if __name__ == "__main__":
    main()