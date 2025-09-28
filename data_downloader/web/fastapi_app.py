"""
FastAPI web application for Feed Downloader dashboard.
Provides REST API endpoints and web interface for monitoring download activities.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from reporting.reporter import DownloadReporter


# Pydantic models for API responses
class SystemOverview(BaseModel):
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    success_rate: str
    total_data_size: str
    avg_duration: str
    uptime_hours: str
    active_vendors: int


class DownloadRecord(BaseModel):
    id: int
    vendor: str
    type: str
    source: str
    status: str
    start_time: str
    duration: str
    file_size: str
    error: str


class VendorStats(BaseModel):
    vendor_name: str
    total_downloads: int
    successful: int
    failed: int
    success_rate: str
    avg_duration: str
    total_size: str
    last_download: str
    last_success: str
    last_failure: str


class DailyStats(BaseModel):
    date: str
    total_downloads: int
    successful: int
    failed: int
    success_rate: str
    avg_duration: str
    total_size: str


# Initialize FastAPI app
app = FastAPI(
    title="Feed Downloader Dashboard",
    description="Web dashboard for monitoring feed download activities",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Global reporter instance
reporter = None


def get_reporter():
    """Get or create reporter instance."""
    global reporter
    if reporter is None:
        reporter = DownloadReporter()
    return reporter


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global reporter
    reporter = get_reporter()


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/overview", response_model=SystemOverview)
async def get_system_overview():
    """Get system overview statistics."""
    try:
        reporter = get_reporter()
        overview = reporter.get_system_overview()
        
        if "error" in overview:
            raise HTTPException(status_code=500, detail=overview["error"])
        
        return SystemOverview(
            total_downloads=overview.get("total_downloads", 0),
            successful_downloads=overview.get("successful_downloads", 0),
            failed_downloads=overview.get("failed_downloads", 0),
            success_rate=overview.get("success_rate", "0%"),
            total_data_size=overview.get("total_data_size", "0 B"),
            avg_duration=overview.get("avg_duration", "0s"),
            uptime_hours=overview.get("uptime_hours", "0h"),
            active_vendors=overview.get("active_vendors", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vendors", response_model=List[VendorStats])
async def get_vendor_stats():
    """Get vendor statistics."""
    try:
        reporter = get_reporter()
        vendor_summary = reporter.get_vendor_summary()
        
        return [
            VendorStats(
                vendor_name=v["vendor_name"],
                total_downloads=v["total_downloads"],
                successful=v["successful"],
                failed=v["failed"],
                success_rate=v["success_rate"],
                avg_duration=v["avg_duration"],
                total_size=v["total_size"],
                last_download=v["last_download"],
                last_success=v["last_success"],
                last_failure=v["last_failure"]
            )
            for v in vendor_summary
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/activity", response_model=List[DownloadRecord])
async def get_recent_activity(limit: int = 20):
    """Get recent download activity."""
    try:
        reporter = get_reporter()
        activity = reporter.get_recent_activity(limit)
        
        return [
            DownloadRecord(
                id=record["id"],
                vendor=record["vendor"],
                type=record["type"],
                source=record["source"],
                status=record["status"],
                start_time=record["start_time"],
                duration=record["duration"],
                file_size=record["file_size"],
                error=record["error"]
            )
            for record in activity
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/daily", response_model=List[DailyStats])
async def get_daily_stats(days: int = 7):
    """Get daily statistics."""
    try:
        reporter = get_reporter()
        daily_stats = reporter.get_daily_stats(days)
        
        return [
            DailyStats(
                date=d["date"],
                total_downloads=d["total_downloads"],
                successful=d["successful"],
                failed=d["failed"],
                success_rate=d["success_rate"],
                avg_duration=d["avg_duration"],
                total_size=d["total_size"]
            )
            for d in daily_stats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/failures")
async def get_recent_failures(limit: int = 20):
    """Get recent failures."""
    try:
        reporter = get_reporter()
        failures = reporter.get_failure_analysis(limit)
        return {"failures": failures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_system_status():
    """Get current system status."""
    try:
        reporter = get_reporter()
        overview = reporter.get_system_overview()
        activity = reporter.get_recent_activity(5)
        
        return {
            "status": "healthy" if "error" not in overview else "error",
            "last_updated": datetime.now().isoformat(),
            "overview": overview,
            "recent_activity": activity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh")
async def refresh_data():
    """Force refresh of dashboard data."""
    try:
        # Force recreation of reporter to refresh data
        global reporter
        reporter = None
        reporter = get_reporter()
        
        return {"message": "Data refreshed successfully", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)