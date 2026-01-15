# Jarvis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a personal AI assistant with hybrid voice/text interaction that can control a Fedora system, provide information, and assist with productivity.

**Architecture:** Python asyncio daemon with modular components - Claude API for reasoning, GTK for UI, Whisper/Piper for voice. Skills are pluggable Python modules that register tools with Claude.

**Tech Stack:** Python 3.11+, anthropic SDK, GTK 4 (PyGObject), faster-whisper, piper-tts, openwakeword, aiohttp

---

## Phase 1: Foundation

### Task 1: Project Setup

**Files:**
- Create: `jarvis/requirements.txt`
- Create: `jarvis/__init__.py`
- Create: `jarvis/tests/__init__.py`

**Step 1: Create requirements.txt**

```
jarvis/requirements.txt
```

```txt
# Core
anthropic>=0.40.0
aiohttp>=3.9.0
pyyaml>=6.0
python-dotenv>=1.0.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0

# Voice (Phase 3)
# faster-whisper>=1.0.0
# piper-tts>=1.2.0
# openwakeword>=0.6.0

# UI (Phase 2)
# PyGObject>=3.46.0
```

**Step 2: Create package init files**

```
jarvis/__init__.py
```

```python
"""Jarvis - Personal AI Assistant."""

__version__ = "0.1.0"
```

```
jarvis/tests/__init__.py
```

```python
"""Jarvis test suite."""
```

**Step 3: Install dependencies**

Run: `cd /home/zanick/IRIS-project/jarvis && pip install -r requirements.txt`
Expected: Successfully installed anthropic, aiohttp, pyyaml, etc.

**Step 4: Verify installation**

Run: `python -c "import anthropic; print(anthropic.__version__)"`
Expected: Version number printed (e.g., "0.40.0")

**Step 5: Commit**

```bash
git add jarvis/requirements.txt jarvis/__init__.py jarvis/tests/__init__.py
git commit -m "feat(jarvis): initialize project with dependencies"
```

---

### Task 2: Logger Utility

**Files:**
- Create: `jarvis/utils/__init__.py`
- Create: `jarvis/utils/logger.py`
- Create: `jarvis/tests/test_logger.py`

**Step 1: Write the failing test**

```
jarvis/tests/test_logger.py
```

```python
"""Tests for logger utility."""

import os
import tempfile
from pathlib import Path

from jarvis.utils.logger import setup_logger, get_logger


def test_setup_logger_creates_log_directory():
    """Logger should create the log directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logger(log_dir=log_dir)
        assert log_dir.exists()


def test_get_logger_returns_named_logger():
    """get_logger should return a logger with the specified name."""
    logger = get_logger("test_module")
    assert logger.name == "jarvis.test_module"


def test_logger_writes_to_file():
    """Logger should write messages to the log file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"
        setup_logger(log_dir=log_dir)
        logger = get_logger("test")
        logger.info("test message")

        log_file = log_dir / "jarvis.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert "test message" in content
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_logger.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'jarvis.utils'"

**Step 3: Create utils package**

```
jarvis/utils/__init__.py
```

```python
"""Jarvis utilities."""

from jarvis.utils.logger import setup_logger, get_logger

__all__ = ["setup_logger", "get_logger"]
```

**Step 4: Write minimal implementation**

```
jarvis/utils/logger.py
```

```python
"""Logging configuration for Jarvis."""

import logging
import sys
from pathlib import Path
from typing import Optional

_initialized = False
_log_dir: Optional[Path] = None


def setup_logger(
    log_dir: Optional[Path] = None,
    level: int = logging.INFO,
    console: bool = True,
) -> None:
    """Initialize the Jarvis logging system.

    Args:
        log_dir: Directory for log files. Defaults to ~/.jarvis/logs/
        level: Logging level. Defaults to INFO.
        console: Whether to also log to console. Defaults to True.
    """
    global _initialized, _log_dir

    if _initialized:
        return

    if log_dir is None:
        log_dir = Path.home() / ".jarvis" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    _log_dir = log_dir

    # Configure root jarvis logger
    root_logger = logging.getLogger("jarvis")
    root_logger.setLevel(level)

    # File handler
    log_file = log_dir / "jarvis.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            "%(levelname)-8s | %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger under the jarvis namespace.

    Args:
        name: Module name for the logger.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"jarvis.{name}")
```

**Step 5: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_logger.py -v`
Expected: 3 passed

**Step 6: Commit**

```bash
git add jarvis/utils/ jarvis/tests/test_logger.py
git commit -m "feat(jarvis): add logging utility"
```

---

### Task 3: Configuration System

**Files:**
- Create: `jarvis/config.py`
- Create: `jarvis/tests/test_config.py`
- Create: `jarvis/default_config.yaml`

**Step 1: Write the failing test**

```
jarvis/tests/test_config.py
```

```python
"""Tests for configuration system."""

import os
import tempfile
from pathlib import Path

import pytest

from jarvis.config import Config, load_config


def test_config_loads_defaults():
    """Config should have sensible defaults."""
    config = Config()
    assert config.user_name == "User"
    assert config.wake_word == "jarvis"
    assert config.model == "claude-sonnet-4-20250514"


def test_config_loads_from_yaml():
    """Config should load values from YAML file."""
    yaml_content = """
user_name: "Zack"
wake_word: "computer"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()

        config = load_config(Path(f.name))
        assert config.user_name == "Zack"
        assert config.wake_word == "computer"

    os.unlink(f.name)


def test_config_env_var_substitution():
    """Config should substitute environment variables."""
    os.environ["TEST_API_KEY"] = "secret123"
    yaml_content = """
anthropic_api_key: "${TEST_API_KEY}"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()

        config = load_config(Path(f.name))
        assert config.anthropic_api_key == "secret123"

    os.unlink(f.name)
    del os.environ["TEST_API_KEY"]


def test_config_locations():
    """Config should parse location data."""
    yaml_content = """
locations:
  - name: "Lewisville"
    lat: 33.046
    lon: -96.994
  - name: "Irving"
    lat: 32.814
    lon: -96.949
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()

        config = load_config(Path(f.name))
        assert len(config.locations) == 2
        assert config.locations[0]["name"] == "Lewisville"

    os.unlink(f.name)
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'jarvis.config'"

**Step 3: Write minimal implementation**

```
jarvis/config.py
```

```python
"""Configuration management for Jarvis."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class Config:
    """Jarvis configuration."""

    # Personal
    user_name: str = "User"
    wake_word: str = "jarvis"

    # Claude API
    anthropic_api_key: str = ""
    model: str = "claude-sonnet-4-20250514"

    # Hotkeys
    command_bar_hotkey: str = "<Super>j"

    # Voice
    voice_enabled: bool = True
    voice_model: str = "en_US-ryan-high"
    listen_timeout: int = 5

    # Locations
    locations: list = field(default_factory=lambda: [
        {"name": "Lewisville", "lat": 33.046, "lon": -96.994},
        {"name": "Irving", "lat": 32.814, "lon": -96.949},
    ])

    # Behavior
    confirmation_for_commands: bool = True
    max_context_messages: int = 20

    # Paths
    config_dir: Path = field(default_factory=lambda: Path.home() / ".jarvis")


def _substitute_env_vars(value: Any) -> Any:
    """Substitute ${VAR} patterns with environment variables."""
    if isinstance(value, str):
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, value)
        for var_name in matches:
            env_value = os.environ.get(var_name, "")
            value = value.replace(f"${{{var_name}}}", env_value)
        return value
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(item) for item in value]
    return value


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to ~/.jarvis/config.yaml

    Returns:
        Loaded Config instance.
    """
    if config_path is None:
        config_path = Path.home() / ".jarvis" / "config.yaml"

    config = Config()

    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        # Substitute environment variables
        data = _substitute_env_vars(data)

        # Update config with loaded values
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

    return config


def save_default_config(config_path: Optional[Path] = None) -> None:
    """Save default configuration to file.

    Args:
        config_path: Path to save config. Defaults to ~/.jarvis/config.yaml
    """
    if config_path is None:
        config_path = Path.home() / ".jarvis" / "config.yaml"

    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_yaml = """# Jarvis Configuration

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
  - name: "Lewisville"
    lat: 33.046
    lon: -96.994
  - name: "Irving"
    lat: 32.814
    lon: -96.949

# Behavior
confirmation_for_commands: true
max_context_messages: 20
"""

    config_path.write_text(default_yaml)
```

**Step 4: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_config.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add jarvis/config.py jarvis/tests/test_config.py
git commit -m "feat(jarvis): add configuration system with env var support"
```

---

### Task 4: Claude API Client

**Files:**
- Create: `jarvis/claude_client.py`
- Create: `jarvis/tests/test_claude_client.py`

**Step 1: Write the failing test**

```
jarvis/tests/test_claude_client.py
```

```python
"""Tests for Claude API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from jarvis.claude_client import ClaudeClient, Tool


def test_tool_to_anthropic_format():
    """Tool should convert to Anthropic API format."""
    tool = Tool(
        name="get_weather",
        description="Get current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                }
            },
            "required": ["location"],
        },
    )

    result = tool.to_anthropic_format()

    assert result["name"] == "get_weather"
    assert result["description"] == "Get current weather for a location"
    assert "input_schema" in result


def test_client_registers_tools():
    """Client should register tools."""
    client = ClaudeClient(api_key="test-key")

    tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
    )

    client.register_tool(tool)

    assert "test_tool" in client.tools


@pytest.mark.asyncio
async def test_client_chat_returns_response():
    """Client chat should return assistant response."""
    with patch("jarvis.claude_client.anthropic.AsyncAnthropic") as mock_anthropic:
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Hello!")]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        client = ClaudeClient(api_key="test-key")
        response = await client.chat("Hi there")

        assert response.text == "Hello!"
        assert response.tool_calls == []
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_claude_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'jarvis.claude_client'"

**Step 3: Write minimal implementation**

```
jarvis/claude_client.py
```

```python
"""Claude API client for Jarvis."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import anthropic

from jarvis.utils.logger import get_logger

logger = get_logger("claude_client")


@dataclass
class Tool:
    """A tool that Claude can call."""

    name: str
    description: str
    parameters: dict
    handler: Optional[Callable] = None

    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic API tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class ToolCall:
    """A tool call from Claude."""

    id: str
    name: str
    arguments: dict


@dataclass
class ChatResponse:
    """Response from Claude."""

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"


SYSTEM_PROMPT = """You are Jarvis, a personal AI assistant running on a Fedora Linux system. You help your user with:

- Information: Weather, news, cryptocurrency prices, system status
- System control: Launching apps, managing files, running commands
- Productivity: Writing assistance, research, task management

You have access to tools that let you interact with the system. Use them when appropriate to fulfill requests.

Be concise and helpful. You're speaking directly to your user, so be conversational but efficient. If a task requires confirmation before executing (like running shell commands), ask first.

Your user's name is {user_name}."""


class ClaudeClient:
    """Async client for Claude API with tool support."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        user_name: str = "User",
    ):
        """Initialize the Claude client.

        Args:
            api_key: Anthropic API key.
            model: Model to use.
            user_name: User's name for personalization.
        """
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.user_name = user_name
        self.tools: dict[str, Tool] = {}
        self.conversation: list[dict] = []
        self.max_context_messages = 20

    def register_tool(self, tool: Tool) -> None:
        """Register a tool for Claude to use.

        Args:
            tool: Tool instance to register.
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation = []

    def _get_system_prompt(self) -> str:
        """Get the system prompt with user name."""
        return SYSTEM_PROMPT.format(user_name=self.user_name)

    def _get_tools_for_api(self) -> list[dict]:
        """Get tools in Anthropic API format."""
        return [tool.to_anthropic_format() for tool in self.tools.values()]

    async def chat(self, message: str) -> ChatResponse:
        """Send a message and get a response.

        Args:
            message: User message.

        Returns:
            ChatResponse with text and any tool calls.
        """
        # Add user message to conversation
        self.conversation.append({"role": "user", "content": message})

        # Trim conversation if too long
        if len(self.conversation) > self.max_context_messages:
            self.conversation = self.conversation[-self.max_context_messages:]

        # Build API request
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "system": self._get_system_prompt(),
            "messages": self.conversation,
        }

        # Add tools if any registered
        if self.tools:
            kwargs["tools"] = self._get_tools_for_api()

        # Make API call
        logger.debug(f"Sending message to Claude: {message[:50]}...")
        response = await self.client.messages.create(**kwargs)

        # Parse response
        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        result_text = "\n".join(text_parts)

        # Add assistant response to conversation
        self.conversation.append({"role": "assistant", "content": response.content})

        return ChatResponse(
            text=result_text,
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
        )

    async def submit_tool_result(self, tool_call_id: str, result: Any) -> ChatResponse:
        """Submit a tool result and get Claude's follow-up response.

        Args:
            tool_call_id: ID of the tool call.
            result: Result from executing the tool.

        Returns:
            ChatResponse with Claude's follow-up.
        """
        # Add tool result to conversation
        self.conversation.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_call_id,
                "content": str(result),
            }],
        })

        # Get follow-up response
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "system": self._get_system_prompt(),
            "messages": self.conversation,
        }

        if self.tools:
            kwargs["tools"] = self._get_tools_for_api()

        response = await self.client.messages.create(**kwargs)

        # Parse response
        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        result_text = "\n".join(text_parts)

        # Add to conversation
        self.conversation.append({"role": "assistant", "content": response.content})

        return ChatResponse(
            text=result_text,
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_claude_client.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add jarvis/claude_client.py jarvis/tests/test_claude_client.py
git commit -m "feat(jarvis): add Claude API client with tool support"
```

---

### Task 5: Skill Registry

**Files:**
- Create: `jarvis/skills/__init__.py`
- Create: `jarvis/skills/base.py`
- Create: `jarvis/tests/test_skills.py`

**Step 1: Write the failing test**

```
jarvis/tests/test_skills.py
```

```python
"""Tests for skill system."""

import pytest

from jarvis.skills.base import Skill, SkillRegistry
from jarvis.claude_client import Tool


class MockSkill(Skill):
    """A mock skill for testing."""

    name = "mock"
    description = "A mock skill"

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="mock_action",
                description="Do a mock action",
                parameters={"type": "object", "properties": {}},
                handler=self.mock_action,
            )
        ]

    async def mock_action(self) -> str:
        return "mock result"


def test_skill_registry_registers_skill():
    """Registry should register skills."""
    registry = SkillRegistry()
    skill = MockSkill()

    registry.register(skill)

    assert "mock" in registry.skills


def test_skill_registry_gets_all_tools():
    """Registry should return all tools from all skills."""
    registry = SkillRegistry()
    skill = MockSkill()
    registry.register(skill)

    tools = registry.get_all_tools()

    assert len(tools) == 1
    assert tools[0].name == "mock_action"


def test_skill_registry_finds_handler():
    """Registry should find the handler for a tool."""
    registry = SkillRegistry()
    skill = MockSkill()
    registry.register(skill)

    handler = registry.get_handler("mock_action")

    assert handler is not None


@pytest.mark.asyncio
async def test_skill_registry_executes_tool():
    """Registry should execute a tool and return result."""
    registry = SkillRegistry()
    skill = MockSkill()
    registry.register(skill)

    result = await registry.execute("mock_action", {})

    assert result == "mock result"
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_skills.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'jarvis.skills'"

**Step 3: Write minimal implementation**

```
jarvis/skills/__init__.py
```

```python
"""Jarvis skills system."""

from jarvis.skills.base import Skill, SkillRegistry

__all__ = ["Skill", "SkillRegistry"]
```

```
jarvis/skills/base.py
```

```python
"""Base classes for Jarvis skills."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from jarvis.claude_client import Tool
from jarvis.utils.logger import get_logger

logger = get_logger("skills")


class Skill(ABC):
    """Base class for all Jarvis skills."""

    name: str = "unnamed"
    description: str = "No description"

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """Get the tools provided by this skill.

        Returns:
            List of Tool instances.
        """
        pass


class SkillRegistry:
    """Registry for managing skills and their tools."""

    def __init__(self):
        """Initialize the registry."""
        self.skills: dict[str, Skill] = {}
        self._tool_handlers: dict[str, Callable] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill.

        Args:
            skill: Skill instance to register.
        """
        self.skills[skill.name] = skill

        # Index all tool handlers
        for tool in skill.get_tools():
            if tool.handler:
                self._tool_handlers[tool.name] = tool.handler

        logger.info(f"Registered skill: {skill.name}")

    def get_all_tools(self) -> list[Tool]:
        """Get all tools from all registered skills.

        Returns:
            List of all Tool instances.
        """
        tools = []
        for skill in self.skills.values():
            tools.extend(skill.get_tools())
        return tools

    def get_handler(self, tool_name: str) -> Optional[Callable]:
        """Get the handler function for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Handler function or None if not found.
        """
        return self._tool_handlers.get(tool_name)

    async def execute(self, tool_name: str, arguments: dict) -> Any:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Arguments to pass to the tool.

        Returns:
            Result from the tool execution.

        Raises:
            ValueError: If tool not found.
        """
        handler = self.get_handler(tool_name)
        if handler is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        logger.debug(f"Executing tool: {tool_name}")

        # Call handler (may be sync or async)
        import asyncio
        if asyncio.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)
```

**Step 4: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_skills.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add jarvis/skills/ jarvis/tests/test_skills.py
git commit -m "feat(jarvis): add skill registry system"
```

---

### Task 6: Time and Date Skill (First Real Skill)

**Files:**
- Create: `jarvis/skills/information/__init__.py`
- Create: `jarvis/skills/information/datetime_skill.py`
- Create: `jarvis/tests/test_datetime_skill.py`

**Step 1: Write the failing test**

```
jarvis/tests/test_datetime_skill.py
```

```python
"""Tests for datetime skill."""

import pytest
from datetime import datetime
from unittest.mock import patch

from jarvis.skills.information.datetime_skill import DateTimeSkill


def test_datetime_skill_has_tools():
    """DateTimeSkill should provide tools."""
    skill = DateTimeSkill()
    tools = skill.get_tools()

    tool_names = [t.name for t in tools]
    assert "get_current_time" in tool_names
    assert "get_current_date" in tool_names


def test_get_current_time_returns_time():
    """get_current_time should return formatted time."""
    skill = DateTimeSkill()

    with patch("jarvis.skills.information.datetime_skill.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 14, 15, 30, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        result = skill.get_current_time()

    assert "15:30" in result  # 24-hour format


def test_get_current_date_returns_date():
    """get_current_date should return formatted date."""
    skill = DateTimeSkill()

    with patch("jarvis.skills.information.datetime_skill.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 1, 14)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        result = skill.get_current_date()

    assert "January" in result
    assert "14" in result
    assert "2025" in result
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_datetime_skill.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create information skills package**

```
jarvis/skills/information/__init__.py
```

```python
"""Information skills for Jarvis."""

from jarvis.skills.information.datetime_skill import DateTimeSkill

__all__ = ["DateTimeSkill"]
```

**Step 4: Write minimal implementation**

```
jarvis/skills/information/datetime_skill.py
```

```python
"""Date and time skill for Jarvis."""

from datetime import datetime

from jarvis.skills.base import Skill
from jarvis.claude_client import Tool


class DateTimeSkill(Skill):
    """Skill for getting current date and time."""

    name = "datetime"
    description = "Get current date and time information"

    def get_tools(self) -> list[Tool]:
        """Get datetime tools."""
        return [
            Tool(
                name="get_current_time",
                description="Get the current time in 24-hour format",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                handler=self.get_current_time,
            ),
            Tool(
                name="get_current_date",
                description="Get the current date with day of week",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                handler=self.get_current_date,
            ),
        ]

    def get_current_time(self) -> str:
        """Get the current time.

        Returns:
            Formatted time string.
        """
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def get_current_date(self) -> str:
        """Get the current date.

        Returns:
            Formatted date string.
        """
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y")
```

**Step 5: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_datetime_skill.py -v`
Expected: 3 passed

**Step 6: Commit**

```bash
git add jarvis/skills/information/ jarvis/tests/test_datetime_skill.py
git commit -m "feat(jarvis): add datetime skill"
```

---

### Task 7: Core Daemon (Basic REPL)

**Files:**
- Create: `jarvis/jarvis_daemon.py`
- Create: `jarvis/tests/test_daemon.py`

**Step 1: Write the failing test**

```
jarvis/tests/test_daemon.py
```

```python
"""Tests for Jarvis daemon."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from jarvis.jarvis_daemon import Jarvis


def test_jarvis_initializes():
    """Jarvis should initialize with config."""
    with patch("jarvis.jarvis_daemon.load_config") as mock_load:
        mock_config = MagicMock()
        mock_config.anthropic_api_key = "test-key"
        mock_config.model = "claude-sonnet-4-20250514"
        mock_config.user_name = "Zack"
        mock_load.return_value = mock_config

        jarvis = Jarvis()

        assert jarvis.config == mock_config


def test_jarvis_registers_skills():
    """Jarvis should register default skills."""
    with patch("jarvis.jarvis_daemon.load_config") as mock_load:
        mock_config = MagicMock()
        mock_config.anthropic_api_key = "test-key"
        mock_config.model = "claude-sonnet-4-20250514"
        mock_config.user_name = "Zack"
        mock_load.return_value = mock_config

        jarvis = Jarvis()

        assert "datetime" in jarvis.skill_registry.skills


@pytest.mark.asyncio
async def test_jarvis_processes_message():
    """Jarvis should process a message and return response."""
    with patch("jarvis.jarvis_daemon.load_config") as mock_load:
        mock_config = MagicMock()
        mock_config.anthropic_api_key = "test-key"
        mock_config.model = "claude-sonnet-4-20250514"
        mock_config.user_name = "Zack"
        mock_load.return_value = mock_config

        jarvis = Jarvis()

        # Mock the Claude client
        jarvis.claude.chat = AsyncMock(return_value=MagicMock(
            text="Hello Zack!",
            tool_calls=[],
            stop_reason="end_turn",
        ))

        response = await jarvis.process("Hello")

        assert "Hello" in response or "Zack" in response
```

**Step 2: Run test to verify it fails**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_daemon.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

```
jarvis/jarvis_daemon.py
```

```python
"""Jarvis daemon - main entry point."""

import asyncio
import sys
from pathlib import Path

from jarvis.config import load_config, Config
from jarvis.claude_client import ClaudeClient, ChatResponse
from jarvis.skills import SkillRegistry
from jarvis.skills.information import DateTimeSkill
from jarvis.utils.logger import setup_logger, get_logger

logger = get_logger("daemon")


class Jarvis:
    """Main Jarvis assistant class."""

    def __init__(self, config_path: Path | None = None):
        """Initialize Jarvis.

        Args:
            config_path: Optional path to config file.
        """
        # Load configuration
        self.config = load_config(config_path)

        # Setup logging
        setup_logger(
            log_dir=self.config.config_dir / "logs",
            console=True,
        )

        logger.info("Initializing Jarvis...")

        # Initialize Claude client
        self.claude = ClaudeClient(
            api_key=self.config.anthropic_api_key,
            model=self.config.model,
            user_name=self.config.user_name,
        )

        # Initialize skill registry
        self.skill_registry = SkillRegistry()
        self._register_default_skills()

        # Register all tools with Claude
        for tool in self.skill_registry.get_all_tools():
            self.claude.register_tool(tool)

        logger.info("Jarvis initialized successfully")

    def _register_default_skills(self) -> None:
        """Register built-in skills."""
        self.skill_registry.register(DateTimeSkill())

    async def process(self, message: str) -> str:
        """Process a user message and return response.

        Args:
            message: User's message.

        Returns:
            Jarvis's response text.
        """
        logger.debug(f"Processing: {message}")

        # Get initial response from Claude
        response = await self.claude.chat(message)

        # Handle tool calls if any
        while response.tool_calls:
            for tool_call in response.tool_calls:
                logger.debug(f"Executing tool: {tool_call.name}")
                try:
                    result = await self.skill_registry.execute(
                        tool_call.name,
                        tool_call.arguments,
                    )
                    response = await self.claude.submit_tool_result(
                        tool_call.id,
                        result,
                    )
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    response = await self.claude.submit_tool_result(
                        tool_call.id,
                        f"Error: {e}",
                    )

        return response.text

    async def run_repl(self) -> None:
        """Run interactive REPL mode."""
        print("\n" + "=" * 50)
        print("  JARVIS - Personal AI Assistant")
        print("  Type 'quit' or 'exit' to stop")
        print("=" * 50 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("quit", "exit", "q"):
                    print("\nGoodbye!")
                    break

                # Process and respond
                response = await self.process(user_input)
                print(f"\nJarvis: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}\n")


async def main():
    """Main entry point."""
    jarvis = Jarvis()
    await jarvis.run_repl()


if __name__ == "__main__":
    asyncio.run(main())
```

**Step 4: Run test to verify it passes**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/test_daemon.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add jarvis/jarvis_daemon.py jarvis/tests/test_daemon.py
git commit -m "feat(jarvis): add core daemon with REPL interface"
```

---

### Task 8: Integration Test - Manual Verification

**Step 1: Create default config**

Run:
```bash
mkdir -p ~/.jarvis
cat > ~/.jarvis/config.yaml << 'EOF'
user_name: "Zack"
wake_word: "jarvis"
anthropic_api_key: "${ANTHROPIC_API_KEY}"
model: "claude-sonnet-4-20250514"
locations:
  - name: "Lewisville"
    lat: 33.046
    lon: -96.994
  - name: "Irving"
    lat: 32.814
    lon: -96.949
EOF
```

**Step 2: Run all tests**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m pytest tests/ -v`
Expected: All tests pass

**Step 3: Test REPL manually (if API key available)**

Run: `cd /home/zanick/IRIS-project/jarvis && python -m jarvis.jarvis_daemon`

Test interactions:
- "What time is it?" → Should call get_current_time tool
- "What's today's date?" → Should call get_current_date tool
- "Hello, who are you?" → Should respond conversationally

**Step 4: Commit completion of Phase 1**

```bash
git add -A
git commit -m "feat(jarvis): complete Phase 1 - foundation with working REPL"
```

---

## Phase 2: Command Bar (Summary)

Tasks for Phase 2 (to be expanded when ready):

1. **Weather Skill** - Fetch weather from Open-Meteo API
2. **App Launcher Skill** - Launch applications via subprocess
3. **GTK Command Bar** - Basic GTK4 window with input/output
4. **Global Hotkey** - Register Super+J to show command bar
5. **Integration** - Connect command bar to daemon via socket

---

## Phase 3: Voice (Summary)

Tasks for Phase 3 (to be expanded when ready):

1. **Audio Utils** - Microphone capture with sounddevice
2. **Wake Word Detection** - OpenWakeWord integration
3. **Speech-to-Text** - faster-whisper transcription
4. **Text-to-Speech** - Piper TTS output
5. **Voice Integration** - Connect voice pipeline to daemon

---

## Phase 4: Skills Expansion (Summary)

Tasks for Phase 4 (to be expanded when ready):

1. **System Stats Skill** - CPU, RAM, disk info
2. **File Manager Skill** - Open, search files
3. **Media Control Skill** - Play/pause, volume
4. **Clipboard Skill** - Read/write clipboard
5. **Shell Command Skill** - Execute approved commands

---

## Phase 5: Polish (Summary)

Tasks for Phase 5 (to be expanded when ready):

1. **System Tray Icon** - Status indicator
2. **Notifications** - libnotify integration
3. **Installer Script** - One-command setup
4. **Systemd Service** - Auto-start on login
5. **Documentation** - User guide
