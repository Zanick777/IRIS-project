# IRIS Dashboard - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-01-11

### Changed - Rebranded to IRIS

#### Rebrand from Z.A.N.I.C.K. to I.R.I.S.
- Complete rebrand from **Z.A.N.I.C.K. Executive Intelligence System** to **I.R.I.S. - Intelligent Reasoning and Interface System**
- Updated all references throughout the codebase
- Changed system name in dashboard header
- Updated console log messages
- Renamed startup script from `start_zanick.sh` to `start_iris.sh`
- Updated all documentation files
- Maintained all existing themes, colors, and functionality
- Version bumped to 4.0.0 to reflect major rebrand

## [3.0.0] - 2026-01-11

### Changed - Claude Design System Update

### Design System Overhaul
- Complete visual redesign inspired by Claude AI's homepage aesthetic
- Transformed from futuristic cyberpunk theme to warm, minimalist design

#### Color Palette
- **Background**: Warm beige (#f5f1eb) replacing dark blue (#0a0e27)
- **Cards**: Clean white (#ffffff) with subtle shadows
- **Accent Color**: Warm orange (#ae5630) replacing cyan/teal gradients
- **Borders**: Subtle tan (#e0d8cc) for refined separation
- **Text**: Dark charcoal (#2d2d2d) for primary content
- **Secondary Text**: Medium gray (#6b6b6b) for labels and metadata

#### Typography
- **Primary Font**: Crimson Pro (serif) - elegant, readable for headings and large numbers
- **Secondary Font**: Inter (sans-serif) - clean, modern for body text and labels
- Removed tech-style Orbitron font
- Improved letter-spacing and line-height for readability
- Reduced uppercase usage for more approachable feel

#### Visual Design
- **Removed Effects**:
  - All glowing effects and text shadows
  - Animated gradients and background patterns
  - Pulsing animations on status indicators
  - Complex hover transformations and sweeps
  - Backdrop filters and blur effects
- **Simplified Elements**:
  - Clean borders with minimal shadows
  - Subtle hover states with background color shifts
  - Reduced border radius for refined appearance
  - Gentle rotation on refresh button (90° vs 180°)

#### Component Updates
- Cards now use white backgrounds with subtle elevation
- Status indicators simplified to solid dots without glow
- News items with left border accent instead of full card backgrounds
- Weather cards with clean layouts and improved spacing
- Stat boxes with understated backgrounds
- Refresh button with clean, minimal styling

### User Experience
- More approachable and trustworthy design language
- Easier on eyes for extended viewing sessions
- Professional aesthetic suitable for executive dashboard
- Improved readability with serif typography
- Clean, uncluttered interface

### Technical Changes
- Updated Google Fonts import to Crimson Pro and Inter
- Simplified CSS with removal of complex animations
- Reduced JavaScript console styling
- Updated inline color styles in dynamic content
- Maintained all functionality while improving visual design

## [2.0.0] - 2026-01-10

### Added - Intelligence News Feed
- Integrated Google News RSS feed aggregation
- Four curated categories:
  - **US Politics**: Latest political developments and policy changes
  - **Economics**: US economic indicators and analysis
  - **Finance**: Market movements and financial sector news
  - **Cryptocurrency**: Bitcoin, blockchain, and digital asset news
- RSS-style presentation with clickable article titles
- Category tags for easy identification
- "Time ago" timestamps (e.g., "2h ago", "1d ago")
- Automatic updates every 5 minutes
- Top 15 most recent articles displayed
- Links open in new tab for seamless reading

### Changed - Branding Update
- Renamed from JARVIS to **IRIS**
- Personalized greeting: "Good Morning/Afternoon/Evening, Zack"
- Updated all console messages and system names
- Renamed startup script to `start_zanick.sh`

### Technical
- Added `fetch_news_data()` method in backend
- RSS feed parsing without external XML libraries
- Concurrent news fetching for all categories
- News data caching for reliability
- Enhanced error handling for news sources

### UI
- New "Intelligence Feed" card with full-width display
- Hover effects on news items
- Category badges with color coding
- Responsive news feed layout
- Clean, scannable article presentation

## [1.0.0] - 2026-01-09

### Added
- Real-time XRP cryptocurrency tracking
- Weather monitoring for Irving and Lewisville, TX
- WebSocket-based live updates
- Futuristic cyberpunk UI theme
- Personalized greeting system
- Auto-refresh every 5 minutes
- Manual refresh button
- Connection status indicators

### Technologies
- Python backend with aiohttp
- Socket.IO for real-time communication
- CoinGecko API for crypto data
- Open-Meteo API for weather data
- Pure HTML/CSS/JavaScript frontend
- No external dependencies for frontend

---

## Semantic Versioning Guide

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Incompatible API changes or major redesigns
- **MINOR** version (0.X.0): New features in a backwards compatible manner
- **PATCH** version (0.0.X): Backwards compatible bug fixes

[4.0.0]: https://github.com/username/iris-dashboard/compare/v3.0.0...v4.0.0
[3.0.0]: https://github.com/username/iris-dashboard/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/username/iris-dashboard/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/username/iris-dashboard/releases/tag/v1.0.0
