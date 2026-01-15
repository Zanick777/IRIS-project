"""Tests for Jarvis daemon."""

import tempfile
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from jarvis.jarvis_daemon import Jarvis
from jarvis.utils.logger import _reset_logger


@pytest.fixture(autouse=True)
def reset_logger_between_tests():
    """Reset logger state before each test."""
    _reset_logger()
    yield
    _reset_logger()


@pytest.fixture
def mock_config():
    """Create a mock config with temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock = MagicMock()
        mock.anthropic_api_key = "test-key"
        mock.model = "claude-sonnet-4-20250514"
        mock.user_name = "Zack"
        mock.config_dir = Path(tmpdir)
        yield mock


def test_jarvis_initializes(mock_config):
    """Jarvis should initialize with config."""
    with patch("jarvis.jarvis_daemon.load_config", return_value=mock_config):
        jarvis = Jarvis()
        assert jarvis.config == mock_config


def test_jarvis_registers_skills(mock_config):
    """Jarvis should register default skills."""
    with patch("jarvis.jarvis_daemon.load_config", return_value=mock_config):
        jarvis = Jarvis()
        assert "datetime" in jarvis.skill_registry.skills


@pytest.mark.asyncio
async def test_jarvis_processes_message(mock_config):
    """Jarvis should process a message and return response."""
    with patch("jarvis.jarvis_daemon.load_config", return_value=mock_config):
        jarvis = Jarvis()

        # Mock the Claude client
        jarvis.claude.chat = AsyncMock(return_value=MagicMock(
            text="Hello Zack!",
            tool_calls=[],
            stop_reason="end_turn",
        ))

        response = await jarvis.process("Hello")

        assert "Hello" in response or "Zack" in response
