# IRIS Dashboard - Quick Start Guide

## The Problem You Encountered

You got `ModuleNotFoundError: No module named 'aiohttp'` because the Python packages weren't installed yet.

## Solution - This is now FIXED!

The required packages have been installed:
- ✅ aiohttp
- ✅ python-socketio

## How to Start the Dashboard

### Option 1: Using the Startup Script (Recommended)
```bash
./start_iris.sh
```

### Option 2: Manual Start
```bash
python3 dashboard_server.py
```

### Option 3: Background Process (keeps running after you close terminal)
```bash
nohup python3 dashboard_server.py > iris.log 2>&1 &
```

To stop it later:
```bash
pkill -f dashboard_server.py
```

## Access Your Dashboard

Once the server is running:
1. Open your browser
2. Go to: **http://localhost:8080**
3. The dashboard will connect automatically and start receiving live data!

## What You Should See

1. **Terminal Output:**
   ```
   ============================================================
   IRIS - Intelligent Reasoning and Interface System - Server Starting
   ============================================================
   Server will be available at: http://localhost:8080
   Dashboard URL: http://localhost:8080/
   Health Check: http://localhost:8080/health
   ============================================================
   Press Ctrl+C to stop the server
   ============================================================
   ======== Running on http://0.0.0.0:8080 ========
   (Press CTRL+C to quit)
   ```

2. **Dashboard Status Indicators:**
   - "All Systems Online" - Green
   - "Live Data Stream Active" - Green (when connected)
   - "Real-time Updates" - Green

3. **Data Updates:**
   - Initial data loads immediately upon opening the dashboard
   - Automatic updates every 5 minutes
   - Manual refresh button available (bottom right)

## Troubleshooting

### If you still get module errors:
```bash
pip3 install --user aiohttp python-socketio
```

### Check if server is running:
```bash
curl http://localhost:8080/health
```

Should return:
```json
{"status": "online", "active_clients": 0, "timestamp": "..."}
```

### View server logs (if running in background):
```bash
tail -f iris.log
```

### Kill the server:
```bash
pkill -f dashboard_server.py
```

## Package Installation Explained

The packages are now installed in your user directory (`~/.local/lib/python3.14/site-packages/`), which means:
- ✅ No sudo/root access needed
- ✅ Won't conflict with system packages
- ✅ Persists across reboots
- ✅ Works immediately

## Next Steps

1. Start the server using one of the methods above
2. Open http://localhost:8080 in your browser
3. Enjoy your personalized IRIS dashboard!

For more advanced configuration (systemd service, custom ports, etc.), see the full README.md
