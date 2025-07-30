#!/usr/bin/env python3
"""
Confluence Report Dashboard Startup Script
Launches both the API server and web server for the dashboard
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import dash
        import plotly
        import pandas
        import openpyxl
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_data_file():
    """Check if the data file exists"""
    data_file = Path("data/report_confluence.json")
    if data_file.exists():
        print(f"✅ Data file found: {data_file}")
        return True
    else:
        print(f"❌ Data file not found: {data_file}")
        print("Please ensure your Confluence data file is in the data/ directory")
        return False

def start_api_server():
    """Start the API server in a separate process"""
    print("🚀 Starting API Server...")
    try:
        process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_web_server():
    """Start the web server in a separate process"""
    print("🌐 Starting Web Server...")
    try:
        process = subprocess.Popen([
            sys.executable, "web_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        return None

def monitor_processes(api_process, web_process):
    """Monitor the running processes"""
    try:
        while True:
            # Check if processes are still running
            if api_process and api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            if web_process and web_process.poll() is not None:
                print("❌ Web server stopped unexpectedly")
                break
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        if api_process:
            api_process.terminate()
        if web_process:
            web_process.terminate()
        print("✅ Servers stopped")

def main():
    """Main startup function"""
    print("=" * 60)
    print("📊 Confluence Report Dashboard v0")
    print("=" * 60)
    
    # Check prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_data_file():
        sys.exit(1)
    
    print("\n🔧 Starting Dashboard Components...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)
    
    # Wait a moment for API server to start
    time.sleep(2)
    
    # Start web server
    web_process = start_web_server()
    if not web_process:
        api_process.terminate()
        sys.exit(1)
    
    # Wait for servers to start
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("🎉 Dashboard is ready!")
    print("=" * 60)
    print("📊 Dashboard URL: http://localhost:8080")
    print("🔗 API Server: http://localhost:5001")
    print("📋 Alternative Dash App: http://localhost:8050")
    print("\n💡 To stop the servers, press Ctrl+C")
    print("=" * 60)
    
    try:
        # Monitor processes
        monitor_processes(api_process, web_process)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        if api_process:
            api_process.terminate()
            api_process.wait()
        if web_process:
            web_process.terminate()
            web_process.wait()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main() 