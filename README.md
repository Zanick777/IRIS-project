# IRIS - Intelligent Reasoning and Interface System

A personalized AI-powered dashboard with real-time market analytics, environmental monitoring, and curated news intelligence.

## Features

### Real-time XRP Cryptocurrency Tracking
- Current price with live updates
- 24-hour price change percentage
- Market capitalization
- 7-day historical daily averages

### Weather Monitoring
- Real-time weather for Irving, TX
- Real-time weather for Lewisville, TX
- Current conditions (temperature, humidity, wind, precipitation)
- 7-day forecast for both locations

### Intelligence News Feed
- **US Politics** - Latest political developments and policy news
- **Economics** - US economic indicators and market analysis
- **Finance** - Market movements and financial news
- **Cryptocurrency** - Bitcoin, blockchain, and crypto market updates
- RSS-style feed with clickable article links
- Categorized and timestamped articles
- Updates automatically every 5 minutes

### Live WebSocket Updates
- Automatic data refresh every 5 minutes
- Real-time connection status indicators
- Manual refresh capability
- Persistent connection with auto-reconnect

### Personalized Experience
- Personalized greeting: "Good Morning/Afternoon/Evening, Zack"
- Futuristic dark theme with cyan and neon green accents
- Military time display (24-hour format)
- System status indicators

## Configuration

### Environment Variables

IRIS uses environment variables for personalization and security. All sensitive and personal information is stored in a `.env` file that is **never committed to version control**.

**Required Configuration:**

| Variable | Description | Example |
|----------|-------------|---------|
| `USER_NAME` | Your name for personalized greetings | `John` |
| `PRIMARY_CITY` | Your primary location name | `Dallas` |
| `PRIMARY_LATITUDE` | Latitude of primary location | `32.7767` |
| `PRIMARY_LONGITUDE` | Longitude of primary location | `-96.7970` |
| `SECONDARY_CITY` | Your secondary location name | `Austin` |
| `SECONDARY_LATITUDE` | Latitude of secondary location | `30.2672` |
| `SECONDARY_LONGITUDE` | Longitude of secondary location | `-97.7431` |

**Optional Configuration:**

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVER_HOST` | Server bind address | `0.0.0.0` |
| `SERVER_PORT` | Server port number | `8080` |
| `UPDATE_INTERVAL` | Data refresh interval (seconds) | `300` |
| `DEBUG_MODE` | Enable debug logging | `false` |

### Setting Up Your Local Environment

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your personal settings
3. Never commit `.env` to version control (it's already in `.gitignore`)

### API Keys

**Current Status:** IRIS uses **100% free, public APIs** that require no authentication:
- ✅ CoinGecko API (XRP prices) - Free, no key required
- ✅ Open-Meteo API (weather) - Free, no key required
- ✅ RSS Feeds (news) - Free, no key required

If you add premium services in the future, add their API keys to `.env`:
```bash
# Example future API keys
COINGECKO_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

## Architecture

### Backend (Python)
- **Technology**: aiohttp + Socket.IO
- **Data Sources**:
  - CoinGecko API for cryptocurrency data
  - Open-Meteo API for weather data
  - Google News RSS for news aggregation
- **Update Frequency**: Every 5 minutes (configurable)
- **Port**: 8080

### Frontend (HTML/JavaScript)
- **Technology**: Pure HTML5, CSS3, JavaScript with Socket.IO client
- **Theme**: Cyberpunk/IRIS-inspired dark theme
- **Fonts**: Orbitron (tech), Roboto (body)
- **Real-time Updates**: WebSocket connection to backend

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/iris-dashboard.git
   cd iris-dashboard
   ```

2. **Set Up Environment Variables**

   Copy the example environment file and customize it:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your preferred settings:
   ```bash
   nano .env  # or use your preferred editor
   ```

   **Important Settings to Customize:**
   - `USER_NAME` - Your name for personalized greetings
   - `PRIMARY_CITY` - Your primary location name
   - `PRIMARY_LATITUDE` - Latitude of your primary location
   - `PRIMARY_LONGITUDE` - Longitude of your primary location
   - `SECONDARY_CITY` - Your secondary location (optional)
   - `SECONDARY_LATITUDE` - Latitude of secondary location
   - `SECONDARY_LONGITUDE` - Longitude of secondary location

   **Finding Your Coordinates:**
   - Use [LatLong.net](https://www.latlong.net/) to find coordinates for your city
   - Or Google Maps: Right-click on a location → Click the coordinates to copy

3. **Install Dependencies**
   ```bash
   pip3 install --user aiohttp python-socketio python-dotenv
   ```

4. **Start the Server**
   ```bash
   ./start_iris.sh
   ```

   Or manually:
   ```bash
   python3 dashboard_server.py
   ```

4. **Access the Dashboard**
   - Open your browser to: `http://localhost:8080`
   - The dashboard will automatically connect to the backend
   - Data will begin streaming immediately

## Usage

### Running in the Background

To run the IRIS server as a background process:

```bash
cd /home/zanick/JarvisProject

# Using nohup
nohup python3 dashboard_server.py > iris.log 2>&1 &

# Or using screen
screen -dmS iris python3 dashboard_server.py

# Or using tmux
tmux new-session -d -s iris 'python3 dashboard_server.py'
```

### Accessing from Other Devices

If you want to access the dashboard from other devices on your network:

1. Find your machine's IP address:
   ```bash
   hostname -I
   ```

2. The server listens on `0.0.0.0:8080`, so you can access it from other devices:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

### Systemd Service (Run on Startup)

To run IRIS automatically on system startup:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/iris.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=IRIS - Intelligent Reasoning and Interface System
   After=network.target

   [Service]
   Type=simple
   User=zanick
   WorkingDirectory=/home/zanick/JarvisProject
   ExecStart=/usr/bin/python3 /home/zanick/JarvisProject/dashboard_server.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable iris
   sudo systemctl start iris
   ```

4. Check status:
   ```bash
   sudo systemctl status iris
   ```

## Configuration

### Update Frequency

To change the data refresh interval, edit `dashboard_server.py`:

```python
# Line ~290 in periodic_update() function
await asyncio.sleep(300)  # Change 300 (5 minutes) to your desired interval in seconds
```

### Weather Locations

To change weather monitoring locations, edit `dashboard_server.py`:

```python
# In fetch_all_data() method, update coordinates:
irving_task = self.fetch_weather_data(YOUR_LAT, YOUR_LON, 'City Name')
```

### News Categories

To customize news topics, edit `dashboard_server.py`:

```python
# In fetch_news_data() method:
topics = {
    'Category Name': 'search+query+terms',
    # Add your own categories
}
```

### Port

To change the server port, edit the last line of `dashboard_server.py`:

```python
web.run_app(app, host='0.0.0.0', port=YOUR_PORT)
```

## Project Structure

```
/home/zanick/JarvisProject/
├── dashboard_server.py      # Python backend server
├── dashboard.html           # Frontend dashboard
├── requirements.txt         # Python dependencies
├── start_iris.sh          # Startup script
├── README.md                # This file
├── QUICKSTART.md            # Quick reference guide
└── CHANGELOG.md             # Version history
```

## API Endpoints

- `GET /` - Serves the dashboard HTML
- `GET /health` - Health check endpoint (returns JSON status)
- WebSocket `/socket.io/` - Real-time data streaming

## Troubleshooting

### Dashboard shows "Connecting..." but never connects

1. Check if the Python server is running:
   ```bash
   curl http://localhost:8080/health
   ```

2. Check the server logs for errors

3. Ensure port 8080 is not blocked by firewall:
   ```bash
   sudo ufw allow 8080
   ```

### Data not updating

1. Check internet connectivity
2. Verify API endpoints are accessible:
   ```bash
   curl https://api.coingecko.com/api/v3/ping
   curl https://api.open-meteo.com/v1/forecast?latitude=32.8140&longitude=-96.9489
   ```

### News feed not loading

Google News RSS feeds are free but may be rate-limited. If news doesn't load:
- Wait a few minutes and refresh
- Check server logs for specific errors
- The news cache will retain the last successful fetch

### High CPU usage

- The server uses asyncio for efficient concurrent requests
- If CPU is high, increase the update interval (default 5 minutes)

## Technologies Used

### Backend
- **aiohttp**: Async HTTP client/server
- **python-socketio**: WebSocket implementation
- **asyncio**: Asynchronous I/O

### Frontend
- **Socket.IO**: Real-time bidirectional communication
- **HTML5**: Modern web markup
- **CSS3**: Animations, gradients, glassmorphism
- **JavaScript ES6+**: Modern JavaScript features

### APIs
- **CoinGecko API**: Cryptocurrency market data (free, no API key required)
- **Open-Meteo API**: Weather forecasting (free, no API key required)
- **Google News RSS**: News aggregation (free, no API key required)

## Customization

### Change Name
Edit `dashboard.html` line ~400:
```javascript
document.getElementById('greeting').textContent = `${greeting}, YOUR_NAME`;
```

### Change Theme Colors
Edit the CSS variables in `dashboard.html`:
```css
/* Primary: #00b7ff (cyan) */
/* Secondary: #00ff9d (neon green) */
/* Background: #0a0e27 (dark navy) */
```

### Add More Data Sources
1. Add fetch function in `dashboard_server.py`
2. Add to `fetch_all_data()` method
3. Update frontend to display new data

## What's New in v4.0

- **Rebranded to IRIS**: Changed from Z.A.N.I.C.K. Executive Intelligence System to I.R.I.S. - Intelligent Reasoning and Interface System
- **News Intelligence Feed**: Aggregates news from US politics, economics, finance, and cryptocurrency
- **Enhanced UI**: News cards with clickable titles linking to source articles
- **Category Tags**: Visual categorization of news articles
- **Time-Aware Updates**: "X minutes/hours ago" timestamps

## License

Personal project - Feel free to modify and use for your own purposes.

## Credits

Created for Zack - 29-year-old executive with a passion for technology and automation.

Powered by:
- CoinGecko API (Cryptocurrency Data)
- Open-Meteo Weather API
- Google News RSS
- Socket.IO
- aiohttp
