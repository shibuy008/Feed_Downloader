#!/bin/bash

# Feed Downloader Dashboard Control Script
# This script manages the FastAPI and Streamlit dashboards

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
FASTAPI_PID_FILE="/tmp/fastapi_dashboard.pid"
STREAMLIT_PID_FILE="/tmp/streamlit_dashboard.pid"
VENV_PATH="../../bin/activate"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                print_warning "$service_name didn't stop gracefully, force killing..."
                kill -9 $pid
            fi
            print_success "$service_name stopped successfully"
        else
            print_warning "$service_name process not found (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        print_warning "No PID file found for $service_name"
    fi
}

# Function to start FastAPI
start_fastapi() {
    print_status "Starting FastAPI Dashboard..."
    
    if check_port $FASTAPI_PORT; then
        print_warning "Port $FASTAPI_PORT is already in use"
        return 1
    fi
    
    # Activate virtual environment and start FastAPI
    source $VENV_PATH
    nohup python -m uvicorn fastapi_app:app --host 0.0.0.0 --port $FASTAPI_PORT > /tmp/fastapi_dashboard.log 2>&1 &
    local pid=$!
    echo $pid > $FASTAPI_PID_FILE
    
    sleep 3
    
    if ps -p $pid > /dev/null 2>&1; then
        print_success "FastAPI Dashboard started successfully!"
        print_status "FastAPI URL: http://localhost:$FASTAPI_PORT"
        print_status "API Docs: http://localhost:$FASTAPI_PORT/docs"
        return 0
    else
        print_error "Failed to start FastAPI Dashboard"
        rm -f $FASTAPI_PID_FILE
        return 1
    fi
}

# Function to start Streamlit
start_streamlit() {
    print_status "Starting Streamlit Dashboard..."
    
    if check_port $STREAMLIT_PORT; then
        print_warning "Port $STREAMLIT_PORT is already in use"
        return 1
    fi
    
    # Activate virtual environment and start Streamlit
    source $VENV_PATH
    nohup streamlit run streamlit_app.py --server.port $STREAMLIT_PORT --server.headless true > /tmp/streamlit_dashboard.log 2>&1 &
    local pid=$!
    echo $pid > $STREAMLIT_PID_FILE
    
    sleep 5
    
    if ps -p $pid > /dev/null 2>&1; then
        print_success "Streamlit Dashboard started successfully!"
        print_status "Streamlit URL: http://localhost:$STREAMLIT_PORT"
        return 0
    else
        print_error "Failed to start Streamlit Dashboard"
        rm -f $STREAMLIT_PID_FILE
        return 1
    fi
}

# Function to stop FastAPI
stop_fastapi() {
    print_status "Stopping FastAPI Dashboard..."
    kill_by_pid_file $FASTAPI_PID_FILE "FastAPI Dashboard"
}

# Function to stop Streamlit
stop_streamlit() {
    print_status "Stopping Streamlit Dashboard..."
    kill_by_pid_file $STREAMLIT_PID_FILE "Streamlit Dashboard"
}

# Function to show status
show_status() {
    echo -e "${BLUE}=== Dashboard Status ===${NC}"
    echo
    
    # Check FastAPI
    if [ -f "$FASTAPI_PID_FILE" ]; then
        local pid=$(cat "$FASTAPI_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_success "FastAPI Dashboard: Running (PID: $pid)"
            print_status "  URL: http://localhost:$FASTAPI_PORT"
            print_status "  API Docs: http://localhost:$FASTAPI_PORT/docs"
        else
            print_error "FastAPI Dashboard: Not running (stale PID file)"
        fi
    else
        print_warning "FastAPI Dashboard: Not running"
    fi
    echo
    
    # Check Streamlit
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local pid=$(cat "$STREAMLIT_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_success "Streamlit Dashboard: Running (PID: $pid)"
            print_status "  URL: http://localhost:$STREAMLIT_PORT"
        else
            print_error "Streamlit Dashboard: Not running (stale PID file)"
        fi
    else
        print_warning "Streamlit Dashboard: Not running"
    fi
    echo
    
    # Check ports
    if check_port $FASTAPI_PORT; then
        print_status "Port $FASTAPI_PORT: In use"
    else
        print_warning "Port $FASTAPI_PORT: Free"
    fi
    
    if check_port $STREAMLIT_PORT; then
        print_status "Port $STREAMLIT_PORT: In use"
    else
        print_warning "Port $STREAMLIT_PORT: Free"
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "fastapi")
            if [ -f "/tmp/fastapi_dashboard.log" ]; then
                print_status "FastAPI Dashboard Logs:"
                echo "----------------------------------------"
                tail -20 /tmp/fastapi_dashboard.log
            else
                print_warning "No FastAPI logs found"
            fi
            ;;
        "streamlit")
            if [ -f "/tmp/streamlit_dashboard.log" ]; then
                print_status "Streamlit Dashboard Logs:"
                echo "----------------------------------------"
                tail -20 /tmp/streamlit_dashboard.log
            else
                print_warning "No Streamlit logs found"
            fi
            ;;
        *)
            print_error "Usage: $0 logs [fastapi|streamlit]"
            ;;
    esac
}

# Function to show help
show_help() {
    echo -e "${BLUE}Feed Downloader Dashboard Control Script${NC}"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start both FastAPI and Streamlit dashboards"
    echo "  stop        Stop both dashboards"
    echo "  restart     Restart both dashboards"
    echo "  status      Show status of both dashboards"
    echo "  fastapi     Start/stop FastAPI dashboard only"
    echo "  streamlit   Start/stop Streamlit dashboard only"
    echo "  logs        Show logs for a specific service"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                    # Start both dashboards"
    echo "  $0 stop                     # Stop both dashboards"
    echo "  $0 status                   # Show status"
    echo "  $0 logs fastapi             # Show FastAPI logs"
    echo "  $0 logs streamlit           # Show Streamlit logs"
    echo
    echo "Dashboard URLs:"
    echo "  FastAPI:     http://localhost:$FASTAPI_PORT"
    echo "  Streamlit:   http://localhost:$STREAMLIT_PORT"
    echo "  API Docs:    http://localhost:$FASTAPI_PORT/docs"
}

# Main script logic
case "$1" in
    "start")
        echo -e "${GREEN}🚀 Starting Feed Downloader Dashboards...${NC}"
        echo
        start_fastapi
        start_streamlit
        echo
        show_status
        ;;
    "stop")
        echo -e "${RED}🛑 Stopping Feed Downloader Dashboards...${NC}"
        echo
        stop_fastapi
        stop_streamlit
        echo
        print_success "All dashboards stopped"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting Feed Downloader Dashboards...${NC}"
        echo
        stop_fastapi
        stop_streamlit
        sleep 2
        start_fastapi
        start_streamlit
        echo
        show_status
        ;;
    "status")
        show_status
        ;;
    "fastapi")
        case "$2" in
            "start")
                start_fastapi
                ;;
            "stop")
                stop_fastapi
                ;;
            *)
                print_error "Usage: $0 fastapi [start|stop]"
                ;;
        esac
        ;;
    "streamlit")
        case "$2" in
            "start")
                start_streamlit
                ;;
            "stop")
                stop_streamlit
                ;;
            *)
                print_error "Usage: $0 streamlit [start|stop]"
                ;;
        esac
        ;;
    "logs")
        show_logs "$2"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac