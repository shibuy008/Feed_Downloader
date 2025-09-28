#!/usr/bin/env python3
"""
Startup script for Feed Downloader web applications.
Provides options to start FastAPI or Streamlit dashboard.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def start_fastapi(host="0.0.0.0", port=8000, reload=True):
    """Start FastAPI application."""
    print("🚀 Starting FastAPI Dashboard...")
    print(f"📍 URL: http://{host}:{port}")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "fastapi_app:app",
            "--host", host,
            "--port", str(port),
            "--reload" if reload else "--no-reload"
        ]
        subprocess.run(cmd, cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def start_streamlit(host="localhost", port=8501):
    """Start Streamlit application."""
    print("🚀 Starting Streamlit Dashboard...")
    print(f"📍 URL: http://{host}:{port}")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app.py",
            "--server.address", host,
            "--server.port", str(port),
            "--server.headless", "true"
        ]
        subprocess.run(cmd, cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n🛑 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "jinja2": "Jinja2",
        "streamlit": "Streamlit",
        "plotly": "Plotly",
        "pandas": "Pandas"
    }
    
    missing_packages = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install fastapi uvicorn jinja2 streamlit plotly pandas")
        return False
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start Feed Downloader web applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_web_apps.py fastapi                    # Start FastAPI on default port 8000
  python start_web_apps.py fastapi --port 8080       # Start FastAPI on port 8080
  python start_web_apps.py streamlit                 # Start Streamlit on default port 8501
  python start_web_apps.py streamlit --port 8502     # Start Streamlit on port 8502
  python start_web_apps.py both                      # Start both applications
        """
    )
    
    parser.add_argument(
        "app",
        choices=["fastapi", "streamlit", "both"],
        help="Application to start"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--fastapi-port",
        type=int,
        default=8000,
        help="FastAPI port (default: 8000)"
    )
    parser.add_argument(
        "--streamlit-port",
        type=int,
        default=8501,
        help="Streamlit port (default: 8501)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for FastAPI"
    )
    
    args = parser.parse_args()
    
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies found")
    
    if args.app == "fastapi":
        start_fastapi(args.host, args.fastapi_port, not args.no_reload)
    
    elif args.app == "streamlit":
        start_streamlit(args.host, args.streamlit_port)
    
    elif args.app == "both":
        print("🚀 Starting both applications...")
        print(f"📍 FastAPI: http://{args.host}:{args.fastapi_port}")
        print(f"📍 Streamlit: http://{args.host}:{args.streamlit_port}")
        print("🛑 Press Ctrl+C to stop both servers")
        
        try:
            import threading
            import time
            
            # Start FastAPI in a thread
            fastapi_thread = threading.Thread(
                target=start_fastapi,
                args=(args.host, args.fastapi_port, not args.no_reload),
                daemon=True
            )
            
            # Start Streamlit in a thread
            streamlit_thread = threading.Thread(
                target=start_streamlit,
                args=(args.host, args.streamlit_port),
                daemon=True
            )
            
            fastapi_thread.start()
            time.sleep(2)  # Give FastAPI time to start
            streamlit_thread.start()
            
            # Wait for both threads
            fastapi_thread.join()
            streamlit_thread.join()
            
        except KeyboardInterrupt:
            print("\n🛑 Both servers stopped")
        except Exception as e:
            print(f"❌ Error starting applications: {e}")

if __name__ == "__main__":
    main()