#!/usr/bin/env python3
"""
IRIS - Intelligent Reasoning and Interface System - Backend Server
Provides real-time data updates for the dashboard via WebSocket
"""

import asyncio
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import aiohttp
from aiohttp import web
import socketio

# Load environment variables from .env file if it exists
try:
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables or defaults.")
except Exception as e:
    print(f"Could not load .env file: {e}")

# Configuration from environment variables with defaults
USER_NAME = os.getenv('USER_NAME', 'Zack')
PRIMARY_CITY = os.getenv('PRIMARY_CITY', 'Irving')
PRIMARY_LATITUDE = float(os.getenv('PRIMARY_LATITUDE', '32.8140'))
PRIMARY_LONGITUDE = float(os.getenv('PRIMARY_LONGITUDE', '-96.9489'))
SECONDARY_CITY = os.getenv('SECONDARY_CITY', 'Lewisville')
SECONDARY_LATITUDE = float(os.getenv('SECONDARY_LATITUDE', '33.0462'))
SECONDARY_LONGITUDE = float(os.getenv('SECONDARY_LONGITUDE', '-96.9942'))
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='aiohttp',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25
)
app = web.Application()
sio.attach(app)

# Store active sessions
active_sessions = set()


class DashboardDataService:
    """Service to fetch and manage dashboard data"""

    def __init__(self):
        self.session = None
        self.xrp_cache = None
        self.weather_cache = {}
        self.news_cache = None
        self.tech_news_cache = None

    async def initialize(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def fetch_xrp_data(self, force: bool = False) -> Dict:  # pylint: disable=unused-argument
        """Fetch XRP cryptocurrency data from CoinGecko API

        The `force` flag is accepted but currently acts as a placeholder
        to allow future caching behavior. On error, returns the last
        successful cached result if available.
        """
        try:
            # Fetch current price data
            current_url = (
                'https://api.coingecko.com/api/v3/simple/price'
                '?ids=ripple&vs_currencies=usd'
                '&include_24hr_change=true&include_market_cap=true'
            )
            async with self.session.get(current_url) as response:
                current_data = await response.json()

            # Fetch 7-day historical data
            historical_url = (
                'https://api.coingecko.com/api/v3/coins/ripple/market_chart'
                '?vs_currency=usd&days=7'
            )
            async with self.session.get(historical_url) as response:
                historical_data = await response.json()

            # Calculate daily averages
            daily_averages = self._calculate_daily_averages(historical_data['prices'])

            result = {
                'current_price': current_data['ripple']['usd'],
                'change_24h': current_data['ripple']['usd_24h_change'],
                'market_cap': current_data['ripple']['usd_market_cap'],
                'daily_averages': daily_averages,
                'timestamp': datetime.now().isoformat()
            }

            self.xrp_cache = result
            return result

        except Exception as e:
            print(f"Error fetching XRP data: {e}")
            return self.xrp_cache if self.xrp_cache else None

    def _calculate_daily_averages(self, prices: List) -> List[Dict]:
        """Calculate daily average prices from hourly data"""
        daily_data = {}

        for timestamp, price in prices:
            date = datetime.fromtimestamp(timestamp / 1000)
            date_key = date.strftime('%b %d')

            if date_key not in daily_data:
                daily_data[date_key] = {'sum': 0, 'count': 0, 'date': date_key}

            daily_data[date_key]['sum'] += price
            daily_data[date_key]['count'] += 1

        averages = [
            {
                'date': day['date'],
                'avgPrice': day['sum'] / day['count']
            }
            for day in daily_data.values()
        ]

        # Return last 7 days in reverse chronological order
        return sorted(averages, key=lambda x: x['date'], reverse=True)[:7]

    async def fetch_weather_data(self, latitude: float, longitude: float, city: str) -> Dict:
        """Fetch weather data from Open-Meteo API"""
        try:
            url = (
                f'https://api.open-meteo.com/v1/forecast?'
                f'latitude={latitude}&longitude={longitude}&'
                f'current=temperature_2m,relative_humidity_2m,apparent_temperature,'
                f'precipitation,weather_code,wind_speed_10m&'
                f'daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&'
                f'temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&'
                f'timezone=America/Chicago&forecast_days=7'
            )

            async with self.session.get(url) as response:
                data = await response.json()

            result = {
                'city': city,
                'current': data['current'],
                'daily': data['daily'],
                'timestamp': datetime.now().isoformat()
            }

            self.weather_cache[city] = result
            return result

        except (aiohttp.ClientError, KeyError) as e:
            print(f"Error fetching weather data for {city}: {e}")
            return self.weather_cache.get(city)

    async def fetch_news_data(self) -> List[Dict]:
        """Fetch news from multiple RSS feeds.

        Focus on US politics, economics, finance, and crypto.
        """
        try:
            news_articles = []

            # Direct RSS feeds from major news sources (more reliable than Google News)
            news_sources = [
                # Politics
                ('US Politics', 'https://feeds.npr.org/1001/rss.xml'),  # NPR Politics
                ('US Politics', 'https://www.politico.com/rss/politics08.xml'),  # Politico

                # Economics & Finance
                ('Economics', 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'),  # WSJ Business
                ('Finance', 'https://feeds.bloomberg.com/markets/news.rss'),  # Bloomberg Markets
                # CNBC Economy
                ('Economics', 'https://www.cnbc.com/id/100003114/device/rss/rss.html'),

                # Cryptocurrency
                ('Cryptocurrency', 'https://cointelegraph.com/rss'),  # Cointelegraph
                ('Cryptocurrency', 'https://www.coindesk.com/arc/outboundfeeds/rss/'),  # CoinDesk
            ]

            # Fetch from each source
            for category, url in news_sources:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    async with self.session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            articles = self._parse_rss_feed(text, category)
                            news_articles.extend(articles[:3])  # Take top 3 from each source
                            print(f"Fetched {len(articles)} articles from {category} source")
                        else:
                            print(f"Failed to fetch {category}: HTTP {response.status}")
                except asyncio.TimeoutError:
                    print(f"Timeout fetching news for {category}")
                    continue
                except Exception as e:
                    print(f"Error fetching news for {category}: {e}")
                    continue

            if news_articles:
                # Sort by published date and limit to 15 articles
                news_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
                result = news_articles[:15]
                self.news_cache = result
                print(f"Successfully aggregated {len(result)} news articles")
                return result
            else:
                print("No news articles fetched, returning cache or empty list")
                return self.news_cache if self.news_cache else []

        except Exception as e:
            print(f"Error fetching news data: {e}")
            return self.news_cache if self.news_cache else []

    def _get_source_name_from_url(self, url: str) -> str:
        """Extract a clean source name from URL"""
        # Common source mappings
        source_map = {
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge',
            'arstechnica.com': 'Ars Technica',
            'wired.com': 'Wired',
            'redhat.com': 'Red Hat',
            'fedoramagazine.org': 'Fedora Magazine',
            'linux.com': 'Linux.com',
            'cloud.google.com': 'Google Cloud',
            'blog.google': 'Google',
            'github.blog': 'GitHub',
            'stackoverflow.blog': 'Stack Overflow',
            'venturebeat.com': 'VentureBeat',
            'artificialintelligence-news.com': 'AI News',
            'cointelegraph.com': 'Cointelegraph',
            'coindesk.com': 'CoinDesk',
            'cnbc.com': 'CNBC',
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'Wall Street Journal',
            'politico.com': 'Politico',
            'npr.org': 'NPR',
        }

        # Check if URL contains any known source
        for domain, name in source_map.items():
            if domain in url.lower():
                return name

        return None

    def _parse_rss_feed(self, rss_text: str, category: str) -> List[Dict]:  # pylint: disable=too-many-locals
        """Parse RSS feed XML and extract article information"""
        articles = []

        # Simple regex-based RSS parsing (avoiding external XML libraries)
        item_pattern = r'<item>(.*?)</item>'
        items = re.findall(item_pattern, rss_text, re.DOTALL)

        # If no items found, try <entry> tags (Atom format)
        if not items:
            item_pattern = r'<entry>(.*?)</entry>'
            items = re.findall(item_pattern, rss_text, re.DOTALL)

        for item in items[:5]:  # Limit to 5 per source
            try:
                # Try different title formats
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)

                # Try different link formats
                link_match = re.search(r'<link>(.*?)</link>', item)
                if not link_match:
                    link_match = re.search(r'<link[^>]*href="([^"]+)"', item)
                if not link_match:
                    link_match = re.search(r'<guid[^>]*>(.*?)</guid>', item)

                # Try different date formats
                pub_date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if not pub_date_match:
                    pub_date_match = re.search(r'<published>(.*?)</published>', item)
                if not pub_date_match:
                    pub_date_match = re.search(r'<updated>(.*?)</updated>', item)
                if not pub_date_match:
                    pub_date_match = re.search(r'<dc:date>(.*?)</dc:date>', item)

                # Try different description formats
                desc_cdata = r'<description><!\[CDATA\[(.*?)\]\]></description>'
                description_match = re.search(desc_cdata, item, re.DOTALL)
                if not description_match:
                    desc_pattern = r'<description>(.*?)</description>'
                    description_match = re.search(desc_pattern, item, re.DOTALL)
                if not description_match:
                    description_match = re.search(r'<summary>(.*?)</summary>', item, re.DOTALL)
                if not description_match:
                    description_match = re.search(r'<content[^>]*>(.*?)</content>', item, re.DOTALL)

                # Extract source
                source_match = re.search(r'<source[^>]*>(.*?)</source>', item)
                if not source_match:
                    source_match = re.search(r'<dc:creator>(.*?)</dc:creator>', item)

                if title_match and link_match:
                    # Parse publication date
                    pub_date_str = pub_date_match.group(1) if pub_date_match else None
                    pub_date = datetime.now().isoformat()

                    if pub_date_str:
                        try:
                            pub_date = parsedate_to_datetime(pub_date_str).isoformat()
                        except Exception:
                            try:
                                # Try ISO format
                                from dateutil import parser
                                pub_date = parser.parse(pub_date_str).isoformat()
                            except:
                                pass

                    # Extract description and remove HTML tags
                    description = ''
                    if description_match:
                        desc_text = description_match.group(1)
                        desc_text = re.sub(r'<[^>]+>', '', desc_text)  # Remove HTML tags
                        desc_text = unescape(desc_text)  # Unescape HTML entities
                        desc_text = desc_text.strip()
                        description = desc_text[:200] + '...' if len(desc_text) > 200 else desc_text

                    # Extract title and clean it
                    title = title_match.group(1)
                    title = re.sub(r'<[^>]+>', '', title)
                    title = unescape(title).strip()

                    # Extract URL and clean it
                    url = link_match.group(1).strip()

                    # Determine source name - try URL first, then RSS metadata, then category
                    source = self._get_source_name_from_url(url)

                    if not source and source_match:
                        source = source_match.group(1)
                        source = re.sub(r'<[^>]+>', '', source)
                        source = unescape(source).strip()

                    if not source or source.lower() in ['news', 'unknown', '']:
                        source = category if category else 'News'

                    if title and url:
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': source,
                            'category': category,
                            'description': description,
                            'publishedAt': pub_date
                        })
            except Exception as e:
                print(f"Error parsing RSS item: {e}")
                continue

        return articles

    async def fetch_tech_news_data(self) -> List[Dict]:
        """Fetch technology news from multiple RSS feeds.

        Focused on AI, tech companies, and industry trends.
        """
        try:
            tech_articles = []

            # Tech-focused RSS feeds
            tech_sources = [
                # AI and Machine Learning
                ('AI News', 'https://feeds.feedburner.com/venturebeat/SZYF'),  # VentureBeat AI
                ('AI', 'https://www.artificialintelligence-news.com/feed/'),  # AI News

                # General Tech News
                ('Technology', 'https://techcrunch.com/feed/'),  # TechCrunch
                ('Technology', 'https://www.theverge.com/rss/index.xml'),  # The Verge
                ('Technology', 'https://www.wired.com/feed/rss'),  # Wired
                ('Technology', 'https://arstechnica.com/feed/'),  # Ars Technica

                # Linux and Open Source
                ('Open Source', 'https://www.redhat.com/en/rss/blog'),  # Red Hat Blog
                ('Linux', 'https://fedoramagazine.org/feed/'),  # Fedora Magazine
                ('Open Source', 'https://www.linux.com/feed/'),  # Linux.com

                # Cloud and Enterprise Tech
                ('Cloud', 'https://cloud.google.com/blog/rss'),  # Google Cloud Blog
                ('Technology', 'https://blog.google/rss/'),  # Google Blog

                # Developer News
                ('Developer', 'https://github.blog/feed/'),  # GitHub Blog
                ('Developer', 'https://stackoverflow.blog/feed/'),  # Stack Overflow Blog
            ]

            # Fetch from each source
            for category, url in tech_sources:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    async with self.session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            articles = self._parse_rss_feed(text, category)
                            tech_articles.extend(articles[:5])  # Take top 5 from each source
                            print(f"Fetched {len(articles)} tech articles from {category} source")
                        else:
                            print(f"Failed to fetch {category} tech news: HTTP {response.status}")
                except asyncio.TimeoutError:
                    print(f"Timeout fetching tech news for {category}")
                    continue
                except Exception as e:
                    print(f"Error fetching tech news for {category}: {e}")
                    continue

            if tech_articles:
                # Sort by published date and limit to 30 articles
                tech_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
                result = tech_articles[:30]
                self.tech_news_cache = result
                print(f"Successfully aggregated {len(result)} tech news articles")
                return result
            else:
                print("No tech news articles fetched, returning cache or empty list")
                return self.tech_news_cache if self.tech_news_cache else []

        except Exception as e:
            print(f"Error fetching tech news data: {e}")
            return self.tech_news_cache if self.tech_news_cache else []

    async def fetch_all_data(self, force: bool = False) -> Dict:
        """Fetch all dashboard data concurrently"""
        try:
            # Fetch all data in parallel
            xrp_task = self.fetch_xrp_data(force=force)
            primary_task = self.fetch_weather_data(
                PRIMARY_LATITUDE, PRIMARY_LONGITUDE, PRIMARY_CITY
            )
            secondary_task = self.fetch_weather_data(
                SECONDARY_LATITUDE, SECONDARY_LONGITUDE, SECONDARY_CITY
            )
            news_task = self.fetch_news_data()

            xrp_data, primary_weather, secondary_weather, news_data = await asyncio.gather(
                xrp_task, primary_task, secondary_task, news_task
            )

            return {
                'xrp': xrp_data,
                'weather': {
                    # Keep keys for frontend compatibility
                    'irving': primary_weather,
                    'lewisville': secondary_weather
                },
                'news': news_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching all data: {e}")
            return None


# Initialize data service
data_service = DashboardDataService()


@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f'Client connected: {sid}')
    active_sessions.add(sid)

    # Send initial data immediately
    data = await data_service.fetch_all_data()
    if data:
        await sio.emit('dashboard_update', data, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f'Client disconnected: {sid}')
    active_sessions.discard(sid)


@sio.event
async def request_refresh(sid, payload=None):
    """Handle manual refresh request from client

    Accepts optional payload like {"force": true} to force-refresh XRP data.
    """
    force = False
    if isinstance(payload, dict):
        force = bool(payload.get('force', False))

    print(f'Refresh requested by: {sid} (force={force})')

    data = await data_service.fetch_all_data(force=force)
    if data:
        await sio.emit('dashboard_update', data, room=sid)


@sio.event
async def request_tech_news(sid):
    """Handle tech news page connection and send initial data"""
    print(f'Tech news requested by: {sid}')

    tech_news = await data_service.fetch_tech_news_data()
    if tech_news:
        await sio.emit('tech_news_update', tech_news, room=sid)


@sio.event
async def request_tech_news_refresh(sid):
    """Handle manual tech news refresh request"""
    print(f'Tech news refresh requested by: {sid}')

    tech_news = await data_service.fetch_tech_news_data()
    if tech_news:
        await sio.emit('tech_news_update', tech_news, room=sid)


async def periodic_update():
    """Periodically fetch and broadcast updates to all connected clients"""
    await asyncio.sleep(5)  # Wait for server to fully start

    while True:
        try:
            if active_sessions:
                print(f'Fetching data for {len(active_sessions)} active clients...')
                data = await data_service.fetch_all_data()

                if data:
                    # Broadcast to all connected clients
                    await sio.emit('dashboard_update', data)
                    print(f'Data broadcast complete at {datetime.now().strftime("%H:%M:%S")}')

            # Wait 5 minutes before next update
            await asyncio.sleep(UPDATE_INTERVAL)

        except Exception as e:
            print(f'Error in periodic update: {e}')
            await asyncio.sleep(60)  # Wait 1 minute before retry on error


async def start_background_tasks(application):
    """Start background tasks"""
    await data_service.initialize()
    application['periodic_update_task'] = asyncio.create_task(periodic_update())


async def cleanup_background_tasks(application):
    """Cleanup background tasks"""
    application['periodic_update_task'].cancel()
    await data_service.close()


# Setup routes for serving static files
routes = web.RouteTableDef()

@routes.get('/')
async def index(_request):
    """Serve the dashboard HTML"""
    try:
        # Resolve the dashboard file relative to this script's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Try common filename variants in the project root
        candidates = [
            os.path.join(base_dir, 'Dashboard.html'),
            os.path.join(base_dir, 'dashboard.html')
        ]

        for path in candidates:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return web.Response(text=f.read(), content_type='text/html')

        # If none found, return 404 with helpful message
        return web.Response(text='Dashboard HTML file not found', status=404)
    except (OSError, IOError) as e:
        print(f'Error serving dashboard HTML: {e}')
        return web.Response(text='Internal server error', status=500)

@routes.get('/tech-news')
async def tech_news_page(_request):
    """Serve the tech news page"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        candidates = [
            os.path.join(base_dir, 'TechNews.html'),
            os.path.join(base_dir, 'technews.html')
        ]

        for path in candidates:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return web.Response(text=f.read(), content_type='text/html')

        return web.Response(text='Tech News page not found', status=404)
    except (OSError, IOError) as e:
        print(f'Error serving tech news page: {e}')
        return web.Response(text='Internal server error', status=500)

@routes.get('/config')
async def config(_request):
    """Provide client configuration"""
    return web.json_response({
        'userName': USER_NAME,
        'primaryCity': PRIMARY_CITY,
        'secondaryCity': SECONDARY_CITY
    })

@routes.get('/health')
async def health(_request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'online',
        'active_clients': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })

app.router.add_routes(routes)

# Register startup and cleanup
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)


if __name__ == '__main__':
    print('=' * 60)
    print('IRIS - Intelligent Reasoning and Interface System - Server Starting')
    print('=' * 60)
    print('Configuration:')
    print(f'  User: {USER_NAME}')
    print(f'  Primary Location: {PRIMARY_CITY}')
    print(f'  Secondary Location: {SECONDARY_CITY}')
    print(f'  Update Interval: {UPDATE_INTERVAL}s')
    print('=' * 60)
    print(f'Server will be available at: http://localhost:{SERVER_PORT}')
    print(f'Dashboard URL: http://localhost:{SERVER_PORT}/')
    print(f'Health Check: http://localhost:{SERVER_PORT}/health')
    print('=' * 60)
    print('Press Ctrl+C to stop the server')
    print('=' * 60)

    web.run_app(app, host=SERVER_HOST, port=SERVER_PORT)
