# Feed Downloader Web Dashboards

The Feed Downloader now includes **two powerful web-based dashboards** for monitoring download activities through your browser:

## 🌐 Available Dashboards

### 1. **FastAPI Dashboard** (Port 8000)
- **REST API endpoints** for programmatic access
- **Interactive web interface** with Bootstrap styling
- **Real-time data updates** with auto-refresh
- **Chart.js visualizations** for trends and analytics
- **Responsive design** for mobile and desktop

### 2. **Streamlit Dashboard** (Port 8501)
- **Interactive Python-based UI** with native components
- **Plotly charts** for advanced visualizations
- **Real-time filtering** and data exploration
- **Multi-tab interface** for organized views
- **Caching** for optimal performance

## 🚀 Quick Start

### Install Dependencies
```bash
pip install fastapi uvicorn jinja2 streamlit plotly
```

### Start Dashboards

**Option 1: Use the startup script**
```bash
cd data_downloader/web

# Start FastAPI dashboard
python start_web_apps.py fastapi

# Start Streamlit dashboard  
python start_web_apps.py streamlit

# Start both simultaneously
python start_web_apps.py both
```

**Option 2: Start individually**
```bash
# FastAPI
cd data_downloader/web
python fastapi_app.py

# Streamlit
cd data_downloader/web
streamlit run streamlit_app.py
```

**Option 3: Demo script**
```bash
python demo_web_dashboards.py
```

## 📊 Dashboard Features

### System Overview
- **Total Downloads**: Count of all download attempts
- **Success Rate**: Percentage of successful downloads
- **Active Vendors**: Number of configured vendors
- **Uptime**: System running time
- **Data Volume**: Total data downloaded
- **Average Duration**: Mean download time

### Vendor Analytics
- **Per-vendor performance** metrics
- **Success/failure rates** by vendor
- **Download volume** and frequency
- **Last download timestamps**
- **Trend analysis** over time

### Activity Monitoring
- **Real-time activity** feed
- **Status tracking** (completed, failed, in-progress)
- **Duration and file size** metrics
- **Error message** capture
- **Download type** classification

### Failure Analysis
- **Error categorization** and frequency
- **Retry patterns** and success rates
- **Vendor-specific** failure analysis
- **Time-based** failure trends
- **Debugging information**

### Data Visualization
- **Line charts** for trends over time
- **Bar charts** for vendor comparisons
- **Pie charts** for status distribution
- **Scatter plots** for activity timelines
- **Interactive filtering** and exploration

## 🎨 FastAPI Dashboard Features

### Web Interface
- **Modern Bootstrap 5** design
- **Responsive layout** for all devices
- **Color-coded status** indicators
- **Interactive charts** with Chart.js
- **Auto-refresh** every 30 seconds
- **Loading indicators** and error handling

### REST API Endpoints
```bash
GET  /                    # Main dashboard page
GET  /api/overview        # System overview data
GET  /api/vendors         # Vendor statistics
GET  /api/activity        # Recent activity
GET  /api/daily          # Daily statistics
GET  /api/failures       # Failure analysis
GET  /api/status         # System status
POST /api/refresh        # Force data refresh
GET  /health            # Health check
```

### Example API Usage
```python
import requests

# Get system overview
response = requests.get("http://localhost:8000/api/overview")
overview = response.json()

# Get recent activity
response = requests.get("http://localhost:8000/api/activity?limit=10")
activity = response.json()

# Force refresh
requests.post("http://localhost:8000/api/refresh")
```

## 📈 Streamlit Dashboard Features

### Interactive Interface
- **Multi-tab layout** for organized views
- **Real-time filtering** and search
- **Interactive charts** with Plotly
- **Data export** capabilities
- **Auto-refresh** with caching
- **Responsive design**

### Tabs Overview
1. **📈 Overview**: System metrics and trends
2. **🏢 Vendors**: Vendor performance analytics
3. **📋 Activity**: Recent download activity
4. **⚠️ Failures**: Failure analysis and debugging

### Interactive Features
- **Sidebar filters** for data exploration
- **Time range selection** for historical analysis
- **Vendor selection** for focused views
- **Status filtering** for specific conditions
- **Auto-refresh toggle** for live monitoring

## 🔧 Configuration

### FastAPI Configuration
```python
# Customize in fastapi_app.py
app = FastAPI(
    title="Feed Downloader Dashboard",
    description="Web dashboard for monitoring feed download activities",
    version="1.0.0"
)

# Server settings
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### Streamlit Configuration
```python
# Customize in streamlit_app.py
st.set_page_config(
    page_title="Feed Downloader Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Startup Script Options
```bash
python start_web_apps.py fastapi --host 0.0.0.0 --fastapi-port 8080
python start_web_apps.py streamlit --host 0.0.0.0 --streamlit-port 8502
python start_web_apps.py both --fastapi-port 8000 --streamlit-port 8501
```

## 📱 Mobile Support

Both dashboards are **fully responsive** and work on:
- **Desktop browsers** (Chrome, Firefox, Safari, Edge)
- **Tablets** (iPad, Android tablets)
- **Mobile devices** (iPhone, Android phones)
- **Touch interfaces** with optimized interactions

## 🔒 Security Considerations

### Production Deployment
- **Authentication**: Add user authentication for production
- **HTTPS**: Use SSL certificates for secure connections
- **Firewall**: Restrict access to authorized networks
- **Rate limiting**: Implement API rate limiting
- **Input validation**: Validate all user inputs

### Example with Authentication
```python
# Add to FastAPI app
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return credentials.username

@app.get("/api/overview")
async def get_overview(username: str = Depends(verify_credentials)):
    # Protected endpoint
    pass
```

## 🚀 Performance Optimization

### Caching
- **Streamlit**: Built-in caching with `@st.cache_data`
- **FastAPI**: Add Redis or in-memory caching
- **Database**: Optimize queries with indexes

### Scaling
- **Load balancing**: Use nginx or similar for multiple instances
- **Database**: Consider PostgreSQL for high-volume deployments
- **Monitoring**: Add Prometheus/Grafana for production monitoring

## 🐛 Troubleshooting

### Common Issues

**Port already in use**
```bash
# Find process using port
lsof -i :8000
lsof -i :8501

# Kill process
kill -9 <PID>
```

**Dependencies missing**
```bash
pip install fastapi uvicorn jinja2 streamlit plotly pandas
```

**Database connection errors**
```bash
# Check database file exists
ls -la feed_downloader.db

# Recreate database
rm feed_downloader.db
python main.py --dry-run
```

**Charts not loading**
- Check browser console for JavaScript errors
- Ensure internet connection for CDN resources
- Try refreshing the page

## 📚 API Documentation

### FastAPI Auto-Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Example API Responses

**System Overview**
```json
{
  "total_downloads": 150,
  "successful_downloads": 142,
  "failed_downloads": 8,
  "success_rate": "94.7%",
  "total_data_size": "2.5 MB",
  "avg_duration": "3.2s",
  "uptime_hours": "24.5h",
  "active_vendors": 5
}
```

**Vendor Statistics**
```json
[
  {
    "vendor_name": "vendor_api",
    "total_downloads": 45,
    "successful": 43,
    "failed": 2,
    "success_rate": "95.6%",
    "avg_duration": "2.1s",
    "total_size": "850 KB",
    "last_download": "2025-09-28 10:30:15",
    "last_success": "2025-09-28 10:30:15",
    "last_failure": "2025-09-28 09:15:22"
  }
]
```

## 🎯 Use Cases

### Operations Teams
- **Real-time monitoring** of download health
- **Alert setup** for failure thresholds
- **Performance tracking** and optimization
- **Capacity planning** based on trends

### Development Teams
- **Debugging** failed downloads
- **Performance analysis** and optimization
- **API testing** with REST endpoints
- **Integration** with monitoring tools

### Management
- **Executive dashboards** with key metrics
- **SLA monitoring** and reporting
- **Cost analysis** based on data volume
- **Vendor performance** comparisons

## 🔮 Future Enhancements

### Planned Features
- **Real-time notifications** (email, Slack, SMS)
- **Advanced analytics** with machine learning
- **Custom dashboards** with drag-and-drop
- **Data export** in multiple formats
- **Integration** with external monitoring tools
- **Multi-tenant** support for multiple organizations

### Extensibility
- **Custom widgets** for specific use cases
- **Plugin system** for additional data sources
- **API extensions** for third-party integrations
- **Theming** and branding customization

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check README.md for setup instructions
- **Examples**: See demo scripts and example configurations
- **Community**: Join discussions and share use cases

---

**Feed Downloader Web Dashboards** provide enterprise-grade monitoring and analytics for your download operations, accessible from any modern web browser! 🌐📊