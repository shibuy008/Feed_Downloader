#!/usr/bin/env python3
"""
Demo script to show the Feed Downloader web dashboards.
This script demonstrates both FastAPI and Streamlit web applications.
"""
import os
import sys
import time
import webbrowser
from datetime import datetime

# Add the data_downloader directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_downloader'))

def create_demo_data():
    """Create some demo data for the dashboard."""
    print("📊 Creating demo data for web dashboards...")
    
    try:
        from database import get_db_context
        from downloader_factory import get_downloader
        
        # Initialize database
        db_context = get_db_context("demo_feed_downloader.db")
        
        # Create demo vendors with different scenarios
        demo_vendors = [
            {
                "name": "demo_http",
                "type": "http",
                "url": "https://httpbin.org/json",
                "local_path": "./downloads/demo_http.json",
                "format": "json"
            },
            {
                "name": "demo_api",
                "type": "rest_api",
                "endpoint": "https://api.github.com/repos/microsoft/vscode",
                "headers": {"User-Agent": "Feed-Downloader-Demo/1.0"},
                "local_path": "./downloads/demo_api.json",
                "format": "json"
            }
        ]
        
        # Create downloads directory
        os.makedirs("./downloads", exist_ok=True)
        
        # Simulate some downloads
        for i, vendor in enumerate(demo_vendors):
            try:
                print(f"  Downloading from {vendor['name']}...")
                downloader = get_downloader(vendor)
                result = downloader.download(download_type="on_demand")
                
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"    ✓ Downloaded: {result} ({file_size} bytes)")
                else:
                    print(f"    ✗ Download failed: {result}")
                    
            except Exception as e:
                print(f"    ⚠ Download error: {e}")
        
        # Simulate some failures
        print("  Simulating some failed downloads...")
        try:
            failed_vendor = {
                "name": "demo_failed",
                "type": "http",
                "url": "https://httpbin.org/status/404",
                "local_path": "./downloads/demo_failed.json",
                "format": "json"
            }
            downloader = get_downloader(failed_vendor)
            downloader.download(download_type="on_demand")
        except:
            print("    ✓ Simulated failure recorded")
        
        print("✅ Demo data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        return False

def show_dashboard_info():
    """Show information about the web dashboards."""
    print("\n🌐 Feed Downloader Web Dashboards")
    print("=" * 50)
    
    print("\n📊 Available Dashboards:")
    print("1. FastAPI Dashboard (Port 8000)")
    print("   - REST API endpoints")
    print("   - Interactive web interface")
    print("   - Real-time data updates")
    print("   - Bootstrap-based UI")
    
    print("\n2. Streamlit Dashboard (Port 8501)")
    print("   - Interactive Python-based UI")
    print("   - Plotly charts and graphs")
    print("   - Real-time filtering")
    print("   - Multi-tab interface")
    
    print("\n🚀 Starting Applications:")
    print("FastAPI:  http://localhost:8000")
    print("Streamlit: http://localhost:8501")
    
    print("\n📋 Features:")
    print("• System overview with key metrics")
    print("• Vendor performance analytics")
    print("• Recent activity monitoring")
    print("• Failure analysis and debugging")
    print("• Daily statistics and trends")
    print("• Interactive charts and graphs")
    print("• Real-time data updates")
    print("• Export capabilities")

def start_fastapi_demo():
    """Start FastAPI dashboard demo."""
    print("\n🚀 Starting FastAPI Dashboard...")
    
    try:
        import subprocess
        import threading
        
        # Start FastAPI in background
        def run_fastapi():
            os.chdir("data_downloader/web")
            subprocess.run([
                sys.executable, "start_web_apps.py", "fastapi", "--fastapi-port", "8000"
            ])
        
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening FastAPI dashboard in browser...")
        webbrowser.open("http://localhost:8000")
        
        print("✅ FastAPI dashboard started!")
        print("📍 URL: http://localhost:8000")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 FastAPI demo stopped")
            
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def start_streamlit_demo():
    """Start Streamlit dashboard demo."""
    print("\n🚀 Starting Streamlit Dashboard...")
    
    try:
        import subprocess
        import threading
        
        # Start Streamlit in background
        def run_streamlit():
            os.chdir("data_downloader/web")
            subprocess.run([
                sys.executable, "start_web_apps.py", "streamlit", "--streamlit-port", "8501"
            ])
        
        streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
        streamlit_thread.start()
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Open browser
        print("🌐 Opening Streamlit dashboard in browser...")
        webbrowser.open("http://localhost:8501")
        
        print("✅ Streamlit dashboard started!")
        print("📍 URL: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Streamlit demo stopped")
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def main():
    """Main demo function."""
    print("🎭 Feed Downloader Web Dashboard Demo")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create demo data
    if not create_demo_data():
        print("❌ Could not create demo data. Exiting.")
        return 1
    
    # Show dashboard information
    show_dashboard_info()
    
    # Ask user which dashboard to start
    print("\n🎯 Which dashboard would you like to see?")
    print("1. FastAPI Dashboard (Port 8000)")
    print("2. Streamlit Dashboard (Port 8501)")
    print("3. Both (Ports 8000 and 8501)")
    print("4. Show information only")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            start_fastapi_demo()
        elif choice == "2":
            start_streamlit_demo()
        elif choice == "3":
            print("\n🚀 Starting both dashboards...")
            print("FastAPI: http://localhost:8000")
            print("Streamlit: http://localhost:8501")
            print("🛑 Press Ctrl+C to stop both")
            
            import subprocess
            import threading
            
            # Start both applications
            def run_both():
                os.chdir("data_downloader/web")
                subprocess.run([
                    sys.executable, "start_web_apps.py", "both",
                    "--fastapi-port", "8000", "--streamlit-port", "8501"
                ])
            
            both_thread = threading.Thread(target=run_both, daemon=True)
            both_thread.start()
            
            # Wait and open browsers
            time.sleep(3)
            webbrowser.open("http://localhost:8000")
            time.sleep(2)
            webbrowser.open("http://localhost:8501")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Both dashboards stopped")
        elif choice == "4":
            print("\n📋 Dashboard Information Displayed")
            print("To start the dashboards manually:")
            print("  cd data_downloader/web")
            print("  python start_web_apps.py fastapi    # For FastAPI")
            print("  python start_web_apps.py streamlit  # For Streamlit")
            print("  python start_web_apps.py both       # For both")
        else:
            print("❌ Invalid choice. Please run the script again.")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1
    
    print("\n✅ Demo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())