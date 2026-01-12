#!/bin/bash

echo "============================================================"
echo "  IRIS - Intelligent Reasoning and Interface System - Startup Script"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import aiohttp, socketio" 2>/dev/null; then
    echo "Installing required dependencies..."
    pip3 install --user -r requirements.txt
    echo "Dependencies installed successfully."
else
    echo "All dependencies already installed."
fi
echo ""

echo ""
echo "============================================================"
echo "  Starting IRIS Backend Server"
echo "============================================================"
echo ""
echo "The dashboard will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "============================================================"
echo ""

# Start the server
python3 dashboard_server.py
