# Jarvis - Personal AI Assistant Design

**Date**: 2025-01-14
**Status**: Approved
**Branch**: feature/jarvis

## Overview

Jarvis is a personal AI assistant for Fedora Linux that provides hybrid voice and text interaction. Unlike the IRIS dashboard (which displays information passively), Jarvis is an active assistant that can control your system, answer questions, and help with productivity tasks.

## Goals

- **Hybrid interaction**: Voice commands ("Hey Jarvis") and keyboard (hotkey command bar)
- **Information awareness**: Weather, news, crypto prices, system status
- **System control**: Launch apps, manage files, run scripts, control media
- **Productivity assistance**: Help with coding, research, drafting, task management
- **Native integration**: Feels like part of Fedora/GNOME, runs as a background service

## Non-Goals

- Smart home / IoT integration
- Replacing IRIS dashboard (they remain separate)
- Mobile or cross-platform support

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS SYSTEM                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Voice     │  │  Command    │  │   System    │     │
│  │   Module    │  │    Bar      │  │   Tray      │     │
│  │  (Whisper)  │  │   (GTK)     │  │   Icon      │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          ▼                              │
│                 ┌─────────────────┐                     │
│                 │   Core Daemon   │                     │
│                 │  (Event Loop)   │                     │
│                 └────────┬────────┘                     │
│                          │                              │
│         ┌────────────────┼────────────────┐             │
│         ▼                ▼                ▼             │
│  ┌────────────┐  ┌─────────────┐  ┌────────────┐       │
│  │   Claude   │  │   Skills    │  │   Tools    │       │
│  │    API     │  │  Registry   │  │  (System)  │       │
│  └────────────┘  └─────────────┘  └────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Core Daemon

The central coordinator that runs as a background service.

**Responsibilities**:
- Maintains persistent asyncio event loop
- Listens for input signals (voice wake word, hotkey, system events)
- Manages conversation context
- Routes requests to Claude API
- Dispatches tool calls
- Sends responses to appropriate output

**Files**:
```
jarvis/
├── jarvis_daemon.py      # Main entry point, event loop
├── config.py             # Settings, API keys, preferences
├── context.py            # Conversation memory management
├── claude_client.py      # Claude API wrapper with tool definitions
└── utils/
    └── logger.py         # Logging to ~/.jarvis/logs/
```

### 2. Voice Module

Handles wake word detection, speech-to-text, and text-to-speech.

**Technology Stack**:
| Function | Technology | Rationale |
|----------|------------|-----------|
| Wake word | OpenWakeWord | Low CPU, customizable, open source |
| Speech-to-text | faster-whisper | Accurate, runs locally, no cloud dependency |
| Text-to-speech | Piper TTS | Natural voices, fast, fully local |

**Flow**:
```
[Microphone]
     │
     ▼
[Wake Word Detector] ──(not detected)──► (keep listening)
     │
   (detected)
     ▼
[Audio Capture] ──► Records until silence detected
     │
     ▼
[Whisper STT] ──► Converts speech to text
     │
     ▼
[Core Daemon] ──► Processes with Claude
     │
     ▼
[Piper TTS] ──► Converts response to audio
     │
     ▼
[Speaker]
```

**Files**:
```
jarvis/voice/
├── listener.py       # Microphone capture, wake word detection
├── transcriber.py    # Whisper speech-to-text
├── speaker.py        # Piper text-to-speech
└── audio_utils.py    # Audio device handling
```

### 3. Command Bar

A keyboard-first quick access popup, similar to Spotlight or Albert.

**Behavior**:
- Press `Super+J` → command bar appears center-screen
- Type request → press Enter
- Jarvis responds inline or takes action
- Press `Escape` → dismisses

**Visual Design**:
```
┌──────────────────────────────────────────────────────┐
│  Jarvis                                         ─ ✕  │
├──────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  │
│  │ What's the weather today?                    ⏎ │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Currently 45°F and cloudy in Lewisville.            │
│  High of 52°F expected, with a chance of rain        │
│  this evening.                                       │
│                                                      │
│  ─────────────────────────────────────────────────   │
│  Type a message    Voice    Settings                 │
└──────────────────────────────────────────────────────┘
```

**Technology**: GTK 4 with Python bindings (PyGObject)

**Files**:
```
jarvis/ui/
├── command_bar.py    # Main GTK window
├── styles.css        # Theming
└── widgets.py        # Custom input/output components
```

### 4. Skills & Tools

Skills define what Jarvis can do. Claude uses tool calling to invoke them.

**Categories**:
| Category | Examples |
|----------|----------|
| Information | Weather, time, news, XRP price, system stats |
| System Control | Launch apps, open files, adjust volume, control media |
| Productivity | Draft text, summarize, help with code, manage tasks |

**Files**:
```
jarvis/skills/
├── __init__.py          # Skill registry
├── information/
│   ├── weather.py       # Weather via Open-Meteo API
│   ├── crypto.py        # Crypto prices via CoinGecko
│   ├── news.py          # Headlines
│   └── system_stats.py  # CPU, RAM, disk, battery
├── system/
│   ├── apps.py          # Launch/close applications
│   ├── files.py         # Open, search, manage files
│   ├── media.py         # Play/pause, volume, next/prev
│   └── shell.py         # Run terminal commands
└── productivity/
    ├── clipboard.py     # Read/write clipboard
    ├── notes.py         # Quick notes
    └── search.py        # Search files, web
```

## Configuration

**Directory Structure**:
```
~/.jarvis/
├── config.yaml          # Main configuration
├── jarvis.log           # Runtime logs
├── context.json         # Conversation memory
├── skills/              # Custom user skills
└── voices/              # Piper voice models
```

**config.yaml**:
```yaml
# Personal
user_name: "Zack"
wake_word: "jarvis"

# Claude API
anthropic_api_key: "${ANTHROPIC_API_KEY}"
model: "claude-sonnet-4-20250514"

# Hotkeys
command_bar_hotkey: "<Super>j"

# Voice
voice_enabled: true
voice_model: "en_US-ryan-high"
listen_timeout: 5

# Locations (for weather)
locations:
  - name: "Lewisville"      # Primary
    lat: 33.046
    lon: -96.994
  - name: "Irving"          # Secondary
    lat: 32.814
    lon: -96.949

# Behavior
confirmation_for_commands: true
max_context_messages: 20
```

## System Integration

**Systemd User Service** (`~/.config/systemd/user/jarvis.service`):
```ini
[Unit]
Description=Jarvis Personal Assistant
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/zanick/IRIS-project/jarvis/jarvis_daemon.py
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
```

**Commands**:
```bash
systemctl --user start jarvis    # Start
systemctl --user enable jarvis   # Auto-start on login
systemctl --user status jarvis   # Check status
journalctl --user -u jarvis -f   # View logs
```

**Desktop Integration**:
- Notifications via libnotify
- Global hotkey via GTK/keybinder
- Optional system tray icon

## Security

- Shell commands require confirmation by default
- API key from environment variable or encrypted keyring
- Conversation context stored locally only
- No data sent anywhere except Claude API

## Dependencies

**Python Packages**:
- `anthropic` - Claude API client
- `faster-whisper` - Speech-to-text
- `piper-tts` - Text-to-speech
- `openwakeword` - Wake word detection
- `PyGObject` - GTK bindings
- `aiohttp` - Async HTTP (for API calls)
- `python-dotenv` - Environment configuration

**System Packages** (Fedora):
```bash
sudo dnf install python3-gobject gtk4 libnotify portaudio
```

## Implementation Plan

1. **Phase 1: Foundation**
   - Core daemon with event loop
   - Claude API integration with basic tool calling
   - Simple terminal-based interaction (no GUI yet)

2. **Phase 2: Command Bar**
   - GTK command bar UI
   - Global hotkey registration
   - Basic skills (weather, app launching)

3. **Phase 3: Voice**
   - Wake word detection
   - Speech-to-text with Whisper
   - Text-to-speech with Piper

4. **Phase 4: Skills Expansion**
   - System control skills
   - Productivity skills
   - File management

5. **Phase 5: Polish**
   - System tray integration
   - Notifications
   - Installer script
   - Documentation

## Open Questions

- Should Jarvis have a personality/persona defined in its system prompt?
- How much conversation history should be retained between sessions?
- Should there be a web UI option in addition to the command bar?
