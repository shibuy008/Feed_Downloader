"""
Database models for download activity tracking.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class DownloadStatus(Enum):
    """Download status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadType(Enum):
    """Download type enumeration."""
    SCHEDULED = "scheduled"
    REAL_TIME = "real_time"
    ON_DEMAND = "on_demand"


@dataclass
class DownloadRecord:
    """Record for a single download activity."""
    id: Optional[int] = None
    vendor_name: str = ""
    download_type: str = ""
    source_type: str = ""
    source_url: str = ""
    local_path: str = ""
    file_size: Optional[int] = None
    status: str = DownloadStatus.PENDING.value
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    schedule_config: Optional[str] = None  # JSON string of schedule config
    metadata: Optional[str] = None  # JSON string of additional metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations."""
        data = asdict(self)
        # Convert datetime objects to strings for JSON serialization
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadRecord':
        """Create from dictionary."""
        # Convert datetime strings back to datetime objects
        for key in ['start_time', 'end_time', 'created_at', 'updated_at']:
            if key in data and data[key]:
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)


@dataclass
class VendorStats:
    """Statistics for a vendor."""
    vendor_name: str
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    success_rate: float
    avg_duration: float
    total_data_size: int
    last_download: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


@dataclass
class SystemStats:
    """Overall system statistics."""
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    success_rate: float
    total_data_size: int
    avg_duration: float
    uptime_hours: float
    active_vendors: int


class DatabaseSchema:
    """Database schema definitions."""
    
    DOWNLOADS_TABLE = """
    CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT NOT NULL,
        download_type TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_url TEXT,
        local_path TEXT NOT NULL,
        file_size INTEGER,
        status TEXT NOT NULL DEFAULT 'pending',
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds REAL,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0,
        schedule_config TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_downloads_vendor ON downloads(vendor_name)",
        "CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status)",
        "CREATE INDEX IF NOT EXISTS idx_downloads_start_time ON downloads(start_time)",
        "CREATE INDEX IF NOT EXISTS idx_downloads_type ON downloads(download_type)",
        "CREATE INDEX IF NOT EXISTS idx_downloads_source_type ON downloads(source_type)",
    ]
    
    VENDOR_STATS_VIEW = """
    CREATE VIEW IF NOT EXISTS vendor_stats AS
    SELECT 
        vendor_name,
        COUNT(*) as total_downloads,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_downloads,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_downloads,
        ROUND(
            CAST(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / 
            COUNT(*) * 100, 2
        ) as success_rate,
        ROUND(AVG(duration_seconds), 2) as avg_duration,
        SUM(COALESCE(file_size, 0)) as total_data_size,
        MAX(start_time) as last_download,
        MAX(CASE WHEN status = 'completed' THEN start_time END) as last_success,
        MAX(CASE WHEN status = 'failed' THEN start_time END) as last_failure
    FROM downloads
    GROUP BY vendor_name
    """
    
    DAILY_STATS_VIEW = """
    CREATE VIEW IF NOT EXISTS daily_stats AS
    SELECT 
        DATE(start_time) as download_date,
        COUNT(*) as total_downloads,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_downloads,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_downloads,
        ROUND(
            CAST(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / 
            COUNT(*) * 100, 2
        ) as success_rate,
        ROUND(AVG(duration_seconds), 2) as avg_duration,
        SUM(COALESCE(file_size, 0)) as total_data_size
    FROM downloads
    WHERE start_time IS NOT NULL
    GROUP BY DATE(start_time)
    ORDER BY download_date DESC
    """
    
    RECENT_FAILURES_VIEW = """
    CREATE VIEW IF NOT EXISTS recent_failures AS
    SELECT 
        vendor_name,
        source_type,
        error_message,
        start_time,
        retry_count
    FROM downloads
    WHERE status = 'failed'
    ORDER BY start_time DESC
    LIMIT 100
    """