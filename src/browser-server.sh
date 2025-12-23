#!/bin/bash

# Browser Debug Server Management Script

SERVER_PID_FILE="../browser-server.pid"
SERVER_LOG="../browser-server.log"
SERVER_PORT=3001

# Determine script directory
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

ensure_script_dir() {
    cd "$SCRIPT_DIR" || { echo "❌ Failed to cd into $SCRIPT_DIR"; exit 1; }
}

case "$1" in
    start)
        ensure_script_dir
        echo "🚀 Starting browser debug server..."
        
        # Check if already running
        if [ -f "$SERVER_PID_FILE" ]; then
            PID=$(cat "$SERVER_PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "❌ Server already running with PID $PID"
                exit 1
            else
                echo "🧹 Cleaning up stale PID file"
                rm -f "$SERVER_PID_FILE"
            fi
        fi
        
        # Kill any process using the port
        echo "🧹 Clearing port $SERVER_PORT..."
        lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null || true
        
        # Start the server
        echo "🌐 Starting server on port $SERVER_PORT..."
        # Use uv to run the python server
        # We assume uv is in path or we use the venv python
        if [ -f "../.venv/bin/python" ]; then
            PYTHON_CMD="../.venv/bin/python"
        else
            PYTHON_CMD="python"
        fi
        
        nohup $PYTHON_CMD browser_server.py > "$SERVER_LOG" 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > "$SERVER_PID_FILE"
        
        # Wait a moment and check if it started
        sleep 2
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            echo "✅ Server started with PID $SERVER_PID"
            echo "📋 Log file: $SERVER_LOG"
            echo "🔍 Check status with: ./browser-server.sh status"
        else
            echo "❌ Failed to start server"
            rm -f "$SERVER_PID_FILE"
            exit 1
        fi
        ;;
        
    stop)
        ensure_script_dir
        echo "🛑 Stopping browser debug server..."
        
        if [ -f "$SERVER_PID_FILE" ]; then
            PID=$(cat "$SERVER_PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                echo "✅ Server stopped (PID $PID)"
            else
                echo "⚠️  Server not running"
            fi
            rm -f "$SERVER_PID_FILE"
        else
            echo "⚠️  No PID file found"
        fi
        
        # Also kill any process using the port
        lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null || true
        ;;
        
    restart)
        ensure_script_dir
        $0 stop
        sleep 1
        $0 start
        ;;
        
    status)
        ensure_script_dir
        echo "🔍 Browser Debug Server Status:"
        echo "----------------------------------------"
        
        if [ -f "$SERVER_PID_FILE" ]; then
            PID=$(cat "$SERVER_PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "✅ Server running with PID $PID"
                
                # Test connection
                if curl -s -m 2 "http://localhost:$SERVER_PORT/status" > /dev/null; then
                    echo "✅ Server responding on port $SERVER_PORT"
                else
                    echo "❌ Server not responding on port $SERVER_PORT"
                fi
            else
                echo "❌ Server not running (stale PID file)"
                rm -f "$SERVER_PID_FILE"
            fi
        else
            echo "❌ Server not running (no PID file)"
        fi
        
        # Check if port is in use
        PORT_USER=$(lsof -ti:$SERVER_PORT 2>/dev/null)
        if [ ! -z "$PORT_USER" ]; then
            echo "⚠️  Port $SERVER_PORT in use by PID: $PORT_USER"
        fi
        
        # Show recent log entries
        if [ -f "$SERVER_LOG" ]; then
            echo ""
            echo "📋 Recent log entries:"
            echo "----------------------------------------"
            tail -10 "$SERVER_LOG"
        fi
        ;;
        
    logs)
        ensure_script_dir
        if [ -f "$SERVER_LOG" ]; then
            tail -f "$SERVER_LOG"
        else
            echo "❌ No log file found: $SERVER_LOG"
        fi
        ;;
        
    test)
        ensure_script_dir
        echo "🧪 Testing server connection..."
        if curl -s -m 5 "http://localhost:$SERVER_PORT/status"; then
            echo ""
            echo "✅ Server connection test passed"
        else
            echo "❌ Server connection test failed"
            exit 1
        fi
        ;;
        
    *)
        echo "Browser Debug Server Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the debug server in background"
        echo "  stop     - Stop the debug server"
        echo "  restart  - Restart the debug server"
        echo "  status   - Show server status and recent logs"
        echo "  logs     - Show live server logs (Ctrl+C to exit)"
        echo "  test     - Test server connection"
        echo ""
        echo "Examples:"
        echo "  $0 start     # Start server"
        echo "  $0 status    # Check if running"
        echo "  $0 test      # Test connection"
        echo "  $0 stop      # Stop server"
        exit 1
        ;;
esac
