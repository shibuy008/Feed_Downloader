"""
Streamlit web application for Feed Downloader dashboard.
Provides interactive dashboard for monitoring download activities.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from reporting.reporter import DownloadReporter

# Page configuration
st.set_page_config(
    page_title="Feed Downloader Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .success-card {
        border-left-color: #28a745;
    }
    
    .danger-card {
        border-left-color: #dc3545;
    }
    
    .warning-card {
        border-left-color: #ffc107;
    }
    
    .info-card {
        border-left-color: #17a2b8;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'reporter' not in st.session_state:
    st.session_state.reporter = DownloadReporter()

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_system_overview():
    """Get system overview with caching."""
    try:
        return st.session_state.reporter.get_system_overview()
    except Exception as e:
        st.error(f"Error fetching system overview: {e}")
        return {}

@st.cache_data(ttl=30)
def get_vendor_stats():
    """Get vendor statistics with caching."""
    try:
        return st.session_state.reporter.get_vendor_summary()
    except Exception as e:
        st.error(f"Error fetching vendor stats: {e}")
        return []

@st.cache_data(ttl=30)
def get_recent_activity(limit=20):
    """Get recent activity with caching."""
    try:
        return st.session_state.reporter.get_recent_activity(limit)
    except Exception as e:
        st.error(f"Error fetching recent activity: {e}")
        return []

@st.cache_data(ttl=30)
def get_daily_stats(days=7):
    """Get daily statistics with caching."""
    try:
        return st.session_state.reporter.get_daily_stats(days)
    except Exception as e:
        st.error(f"Error fetching daily stats: {e}")
        return []

@st.cache_data(ttl=30)
def get_failure_analysis(limit=20):
    """Get failure analysis with caching."""
    try:
        return st.session_state.reporter.get_failure_analysis(limit)
    except Exception as e:
        st.error(f"Error fetching failure analysis: {e}")
        return []

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a metric card."""
    if delta:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )
    else:
        st.metric(label=title, value=value)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Feed Downloader Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.markdown(f"**Last Updated:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        
        if auto_refresh:
            time.sleep(30)
            st.cache_data.clear()
            st.rerun()
        
        # Filters
        st.header("🔍 Filters")
        
        # Vendor filter
        vendor_stats = get_vendor_stats()
        vendor_names = [v['vendor_name'] for v in vendor_stats]
        selected_vendors = st.multiselect(
            "Select Vendors",
            options=vendor_names,
            default=vendor_names
        )
        
        # Time range filter
        time_range = st.selectbox(
            "Time Range",
            options=["Last 24 hours", "Last 7 days", "Last 30 days", "All time"],
            index=1
        )
        
        # Status filter
        status_filter = st.multiselect(
            "Status Filter",
            options=["completed", "failed", "in_progress", "pending"],
            default=["completed", "failed"]
        )
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏢 Vendors", "📋 Activity", "⚠️ Failures"])
    
    with tab1:
        st.header("System Overview")
        
        # Get system overview
        overview = get_system_overview()
        
        if overview and "error" not in overview:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card(
                    "Total Downloads",
                    overview.get("total_downloads", 0),
                    delta_color="normal"
                )
            
            with col2:
                create_metric_card(
                    "Success Rate",
                    overview.get("success_rate", "0%"),
                    delta_color="normal"
                )
            
            with col3:
                create_metric_card(
                    "Active Vendors",
                    overview.get("active_vendors", 0),
                    delta_color="normal"
                )
            
            with col4:
                create_metric_card(
                    "Uptime",
                    overview.get("uptime_hours", "0h"),
                    delta_color="normal"
                )
            
            # Additional metrics
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                create_metric_card(
                    "Successful Downloads",
                    overview.get("successful_downloads", 0),
                    delta_color="normal"
                )
            
            with col6:
                create_metric_card(
                    "Failed Downloads",
                    overview.get("failed_downloads", 0),
                    delta_color="normal"
                )
            
            with col7:
                create_metric_card(
                    "Total Data Size",
                    overview.get("total_data_size", "0 B"),
                    delta_color="normal"
                )
            
            with col8:
                create_metric_card(
                    "Average Duration",
                    overview.get("avg_duration", "0s"),
                    delta_color="normal"
                )
            
            # Charts
            st.header("📊 Trends")
            
            # Daily statistics chart
            daily_stats = get_daily_stats(7)
            if daily_stats:
                df_daily = pd.DataFrame(daily_stats)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Line chart for downloads over time
                    fig_line = px.line(
                        df_daily,
                        x='date',
                        y=['total_downloads', 'successful', 'failed'],
                        title='Downloads Over Time',
                        labels={'value': 'Count', 'date': 'Date'}
                    )
                    fig_line.update_layout(height=400)
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with col2:
                    # Pie chart for success vs failure
                    total_successful = sum(d['successful'] for d in daily_stats)
                    total_failed = sum(d['failed'] for d in daily_stats)
                    
                    if total_successful > 0 or total_failed > 0:
                        fig_pie = px.pie(
                            values=[total_successful, total_failed],
                            names=['Successful', 'Failed'],
                            title='Success vs Failure Distribution',
                            color_discrete_map={'Successful': '#28a745', 'Failed': '#dc3545'}
                        )
                        fig_pie.update_layout(height=400)
                        st.plotly_chart(fig_pie, use_container_width=True)
                    else:
                        st.info("No data available for pie chart")
            
        else:
            st.error("Unable to load system overview data")
    
    with tab2:
        st.header("Vendor Performance")
        
        vendor_stats = get_vendor_stats()
        
        if vendor_stats:
            # Filter vendors based on selection
            filtered_vendors = [v for v in vendor_stats if v['vendor_name'] in selected_vendors]
            
            if filtered_vendors:
                df_vendors = pd.DataFrame(filtered_vendors)
                
                # Vendor metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Success rate by vendor
                    fig_success = px.bar(
                        df_vendors,
                        x='vendor_name',
                        y='success_rate',
                        title='Success Rate by Vendor',
                        labels={'success_rate': 'Success Rate (%)', 'vendor_name': 'Vendor'}
                    )
                    fig_success.update_layout(height=400)
                    st.plotly_chart(fig_success, use_container_width=True)
                
                with col2:
                    # Total downloads by vendor
                    fig_total = px.bar(
                        df_vendors,
                        x='vendor_name',
                        y='total_downloads',
                        title='Total Downloads by Vendor',
                        labels={'total_downloads': 'Total Downloads', 'vendor_name': 'Vendor'}
                    )
                    fig_total.update_layout(height=400)
                    st.plotly_chart(fig_total, use_container_width=True)
                
                # Vendor table
                st.header("📋 Vendor Details")
                
                # Display vendor statistics table
                display_columns = [
                    'vendor_name', 'total_downloads', 'successful', 'failed',
                    'success_rate', 'avg_duration', 'total_size', 'last_download'
                ]
                
                st.dataframe(
                    df_vendors[display_columns],
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                st.info("No vendors selected or available")
        else:
            st.error("Unable to load vendor statistics")
    
    with tab3:
        st.header("Recent Activity")
        
        recent_activity = get_recent_activity(50)
        
        if recent_activity:
            df_activity = pd.DataFrame(recent_activity)
            
            # Filter by status if specified
            if status_filter:
                df_activity = df_activity[df_activity['status'].isin(status_filter)]
            
            # Activity timeline
            if not df_activity.empty:
                # Convert start_time to datetime for better plotting
                df_activity['start_time_dt'] = pd.to_datetime(df_activity['start_time'])
                
                # Activity over time
                fig_timeline = px.scatter(
                    df_activity,
                    x='start_time_dt',
                    y='vendor',
                    color='status',
                    title='Activity Timeline',
                    labels={'start_time_dt': 'Time', 'vendor': 'Vendor'},
                    color_discrete_map={
                        'completed': '#28a745',
                        'failed': '#dc3545',
                        'in_progress': '#ffc107',
                        'pending': '#17a2b8'
                    }
                )
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Activity table
                st.header("📋 Recent Downloads")
                
                # Select columns to display
                display_columns = [
                    'id', 'vendor', 'type', 'source', 'status',
                    'start_time', 'duration', 'file_size'
                ]
                
                st.dataframe(
                    df_activity[display_columns],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No activity matching the selected filters")
        else:
            st.error("Unable to load recent activity data")
    
    with tab4:
        st.header("Failure Analysis")
        
        failures = get_failure_analysis(50)
        
        if failures:
            df_failures = pd.DataFrame(failures)
            
            # Failure statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Failures by vendor
                failure_counts = df_failures['vendor'].value_counts()
                if not failure_counts.empty:
                    fig_vendor_failures = px.bar(
                        x=failure_counts.index,
                        y=failure_counts.values,
                        title='Failures by Vendor',
                        labels={'x': 'Vendor', 'y': 'Failure Count'}
                    )
                    fig_vendor_failures.update_layout(height=400)
                    st.plotly_chart(fig_vendor_failures, use_container_width=True)
            
            with col2:
                # Failures by source type
                source_counts = df_failures['source_type'].value_counts()
                if not source_counts.empty:
                    fig_source_failures = px.pie(
                        values=source_counts.values,
                        names=source_counts.index,
                        title='Failures by Source Type'
                    )
                    fig_source_failures.update_layout(height=400)
                    st.plotly_chart(fig_source_failures, use_container_width=True)
            
            # Failure table
            st.header("⚠️ Recent Failures")
            
            st.dataframe(
                df_failures,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("No recent failures found")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Feed Downloader Dashboard | Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()