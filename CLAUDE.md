# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IRIS (Intelligent Reasoning and Interface System) is a two-component project:

1. **IRIS Dashboard** - Web-based real-time information display (crypto, weather, news) using aiohttp + Socket.IO
2. **Jarvis** - Personal AI assistant with Claude API integration, currently in Phase 1 (text REPL interface)

## Commands

### IRIS Dashboard

```bash
# Install dependencies
pip3 install --user aiohttp python-socketio python-dotenv

# Start server
./start_iris.sh
# or: python3 dashboard_server.py

# Health check
curl http://localhost:8080/health
```

### Jarvis

```bash
# Install dependencies
cd jarvis && pip install -r requirements.txt

# Run all tests
pytest jarvis/tests/ -v

# Run specific test file
pytest jarvis/tests/test_daemon.py -v

# Run single test
pytest jarvis/tests/test_daemon.py::test_jarvis_initializes -v

# Start REPL (requires ANTHROPIC_API_KEY env var)
python -m jarvis.jarvis_daemon

# View logs
tail -f ~/.jarvis/logs/jarvis.log
```

### CI

GitHub Actions runs pylint on push for Python 3.8/3.9/3.10:
```bash
pylint $(git ls-files '*.py')
```

## Architecture

### Jarvis Component Architecture

```
Jarvis (jarvis_daemon.py)
├── Config (config.py) - YAML config with env var substitution (~/.jarvis/config.yaml)
├── ClaudeClient (claude_client.py) - Async Anthropic API with tool registration
├── SkillRegistry (skills/base.py) - Plugin system for tools
│   └── Skills register Tool objects with handlers
└── Logger (utils/logger.py) - File logging to ~/.jarvis/logs/
```

**Message Flow:**
1. User input → `Jarvis.process()`
2. → `ClaudeClient.chat()` with registered tools
3. → Claude may return tool_calls
4. → `SkillRegistry.execute()` runs handler
5. → `ClaudeClient.submit_tool_result()` sends result back
6. → Loop until no more tool calls
7. → Return final response text

### Adding New Skills

1. Create skill class in `jarvis/skills/<category>/`:
```python
from jarvis.skills.base import Skill
from jarvis.claude_client import Tool

class MySkill(Skill):
    name = "my_skill"
    description = "Description"

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="tool_name",
                description="What it does",
                parameters={"type": "object", "properties": {...}},
                handler=self.handler_method,
            )
        ]
```

2. Register in `jarvis_daemon.py` `_register_default_skills()`
3. Write tests in `jarvis/tests/test_<skill>.py`

### IRIS Dashboard Architecture

- `dashboard_server.py` - aiohttp backend with async data fetching
- `Dashboard.html` - Frontend with Socket.IO client
- Data sources: CoinGecko (crypto), Open-Meteo (weather), Google News RSS
- Updates every 5 minutes via WebSocket

## Key Patterns

- **Async-first**: All I/O uses asyncio (`async def`, `await`)
- **Tool calling**: Claude API tool_use pattern with handlers indexed in SkillRegistry
- **Config substitution**: YAML values like `"${ENV_VAR}"` replaced from environment
- **Test mocking**: Use `@patch()` for external dependencies (Claude API, file I/O)

## Configuration

- **IRIS**: Environment variables in `.env` (copy from `.env.example`)
- **Jarvis**: YAML config at `~/.jarvis/config.yaml`, requires `ANTHROPIC_API_KEY` env var

## Current Development State

Jarvis is in **Phase 1** (Foundation) - text REPL interface working. Future phases:
- Phase 2: GTK command bar UI
- Phase 3: Voice (wake word, STT, TTS)
- Phase 4: Skills expansion
- Phase 5: System integration

See `jarvis/docs/plans/` for design documents.
