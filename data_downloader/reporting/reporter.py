"""
Reporting and monitoring utilities for download activities.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from tabulate import tabulate

from database import get_db_context, VendorStats, SystemStats


class DownloadReporter:
    """
    Reporter for download activities and statistics.
    """
    
    def __init__(self):
        """Initialize the reporter."""
        self.db_manager = get_db_context().get_manager()
        self.logger = logging.getLogger("reporting.reporter")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get overall system overview.
        
        Returns:
            Dict containing system statistics
        """
        try:
            system_stats = self.db_manager.get_system_stats()
            
            if system_stats:
                return {
                    "total_downloads": system_stats.total_downloads,
                    "successful_downloads": system_stats.successful_downloads,
                    "failed_downloads": system_stats.failed_downloads,
                    "success_rate": f"{system_stats.success_rate}%",
                    "total_data_size": self._format_bytes(system_stats.total_data_size),
                    "avg_duration": f"{system_stats.avg_duration}s",
                    "uptime_hours": f"{system_stats.uptime_hours}h",
                    "active_vendors": system_stats.active_vendors
                }
            else:
                return {"error": "No data available"}
                
        except Exception as e:
            self.logger.error(f"Failed to get system overview: {e}")
            return {"error": str(e)}
    
    def get_vendor_summary(self, vendor_name: str = None) -> List[Dict[str, Any]]:
        """
        Get vendor summary statistics.
        
        Args:
            vendor_name: Specific vendor name (None for all vendors)
            
        Returns:
            List of vendor statistics
        """
        try:
            vendor_stats = self.db_manager.get_vendor_stats(vendor_name)
            
            summary = []
            for stats in vendor_stats:
                summary.append({
                    "vendor_name": stats.vendor_name,
                    "total_downloads": stats.total_downloads,
                    "successful": stats.successful_downloads,
                    "failed": stats.failed_downloads,
                    "success_rate": f"{stats.success_rate}%",
                    "avg_duration": f"{stats.avg_duration}s",
                    "total_size": self._format_bytes(stats.total_data_size),
                    "last_download": stats.last_download.strftime("%Y-%m-%d %H:%M:%S") if stats.last_download else "Never",
                    "last_success": stats.last_success.strftime("%Y-%m-%d %H:%M:%S") if stats.last_success else "Never",
                    "last_failure": stats.last_failure.strftime("%Y-%m-%d %H:%M:%S") if stats.last_failure else "Never"
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get vendor summary: {e}")
            return []
    
    def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent download activity.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent download records
        """
        try:
            downloads = self.db_manager.get_recent_downloads(limit)
            
            activity = []
            for download in downloads:
                activity.append({
                    "id": download.id,
                    "vendor": download.vendor_name,
                    "type": download.download_type,
                    "source": download.source_type,
                    "status": download.status,
                    "start_time": download.start_time.strftime("%Y-%m-%d %H:%M:%S") if download.start_time else "N/A",
                    "duration": f"{download.duration_seconds:.2f}s" if download.duration_seconds else "N/A",
                    "file_size": self._format_bytes(download.file_size) if download.file_size else "N/A",
                    "error": download.error_message[:50] + "..." if download.error_message and len(download.error_message) > 50 else download.error_message or ""
                })
            
            return activity
            
        except Exception as e:
            self.logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily statistics
        """
        try:
            daily_stats = self.db_manager.get_daily_stats(days)
            
            stats = []
            for day in daily_stats:
                stats.append({
                    "date": day["download_date"],
                    "total_downloads": day["total_downloads"],
                    "successful": day["successful_downloads"],
                    "failed": day["failed_downloads"],
                    "success_rate": f"{day['success_rate']}%",
                    "avg_duration": f"{day['avg_duration']}s",
                    "total_size": self._format_bytes(day["total_data_size"])
                })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get daily stats: {e}")
            return []
    
    def get_failure_analysis(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get failure analysis.
        
        Args:
            limit: Maximum number of failure records to return
            
        Returns:
            List of failure records
        """
        try:
            failures = self.db_manager.get_recent_failures(limit)
            
            analysis = []
            for failure in failures:
                analysis.append({
                    "vendor": failure["vendor_name"],
                    "source_type": failure["source_type"],
                    "error": failure["error_message"][:100] + "..." if len(failure["error_message"]) > 100 else failure["error_message"],
                    "time": failure["start_time"],
                    "retry_count": failure["retry_count"]
                })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get failure analysis: {e}")
            return []
    
    def print_system_overview(self):
        """Print system overview in a formatted table."""
        overview = self.get_system_overview()
        
        if "error" in overview:
            print(f"Error: {overview['error']}")
            return
        
        print("=" * 60)
        print("SYSTEM OVERVIEW")
        print("=" * 60)
        
        table_data = [
            ["Total Downloads", overview["total_downloads"]],
            ["Successful Downloads", overview["successful_downloads"]],
            ["Failed Downloads", overview["failed_downloads"]],
            ["Success Rate", overview["success_rate"]],
            ["Total Data Size", overview["total_data_size"]],
            ["Average Duration", overview["avg_duration"]],
            ["Uptime", overview["uptime_hours"]],
            ["Active Vendors", overview["active_vendors"]]
        ]
        
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
        print()
    
    def print_vendor_summary(self, vendor_name: str = None):
        """Print vendor summary in a formatted table."""
        summary = self.get_vendor_summary(vendor_name)
        
        if not summary:
            print("No vendor data available")
            return
        
        print("=" * 120)
        print("VENDOR SUMMARY")
        print("=" * 120)
        
        headers = ["Vendor", "Total", "Success", "Failed", "Rate", "Avg Duration", "Size", "Last Download", "Last Success"]
        table_data = []
        
        for vendor in summary:
            table_data.append([
                vendor["vendor_name"],
                vendor["total_downloads"],
                vendor["successful"],
                vendor["failed"],
                vendor["success_rate"],
                vendor["avg_duration"],
                vendor["total_size"],
                vendor["last_download"],
                vendor["last_success"]
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def print_recent_activity(self, limit: int = 20):
        """Print recent activity in a formatted table."""
        activity = self.get_recent_activity(limit)
        
        if not activity:
            print("No recent activity available")
            return
        
        print("=" * 140)
        print(f"RECENT ACTIVITY (Last {limit} downloads)")
        print("=" * 140)
        
        headers = ["ID", "Vendor", "Type", "Source", "Status", "Start Time", "Duration", "Size", "Error"]
        table_data = []
        
        for record in activity:
            table_data.append([
                record["id"],
                record["vendor"],
                record["type"],
                record["source"],
                record["status"],
                record["start_time"],
                record["duration"],
                record["file_size"],
                record["error"]
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def print_daily_stats(self, days: int = 7):
        """Print daily statistics in a formatted table."""
        stats = self.get_daily_stats(days)
        
        if not stats:
            print("No daily statistics available")
            return
        
        print("=" * 100)
        print(f"DAILY STATISTICS (Last {days} days)")
        print("=" * 100)
        
        headers = ["Date", "Total", "Success", "Failed", "Rate", "Avg Duration", "Size"]
        table_data = []
        
        for day in stats:
            table_data.append([
                day["date"],
                day["total_downloads"],
                day["successful"],
                day["failed"],
                day["success_rate"],
                day["avg_duration"],
                day["total_size"]
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def print_failure_analysis(self, limit: int = 20):
        """Print failure analysis in a formatted table."""
        failures = self.get_failure_analysis(limit)
        
        if not failures:
            print("No failures found")
            return
        
        print("=" * 120)
        print(f"FAILURE ANALYSIS (Last {limit} failures)")
        print("=" * 120)
        
        headers = ["Vendor", "Source Type", "Error", "Time", "Retries"]
        table_data = []
        
        for failure in failures:
            table_data.append([
                failure["vendor"],
                failure["source_type"],
                failure["error"],
                failure["time"],
                failure["retry_count"]
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    
    def print_complete_report(self):
        """Print a complete report with all sections."""
        print("\n" + "=" * 80)
        print("FEED DOWNLOADER - COMPLETE REPORT")
        print("=" * 80)
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.print_system_overview()
        self.print_vendor_summary()
        self.print_recent_activity(10)
        self.print_daily_stats(7)
        self.print_failure_analysis(10)
    
    def export_to_csv(self, filename: str = None) -> str:
        """
        Export recent activity to CSV file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            str: Path to the exported file
        """
        import csv
        from datetime import datetime
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"download_report_{timestamp}.csv"
        
        try:
            activity = self.get_recent_activity(1000)  # Get more records for export
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if activity:
                    fieldnames = activity[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(activity)
            
            self.logger.info(f"Exported {len(activity)} records to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            raise
    
    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes into human readable format.
        
        Args:
            bytes_value: Bytes value
            
        Returns:
            str: Formatted string
        """
        if bytes_value is None:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"