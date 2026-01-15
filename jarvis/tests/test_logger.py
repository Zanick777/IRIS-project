"""Tests for logger utility."""

import tempfile
from pathlib import Path

import pytest

from jarvis.utils.logger import setup_logger, get_logger, _reset_logger


@pytest.fixture(autouse=True)
def reset_logger_between_tests():
    """Reset logger state before each test."""
    _reset_logger()
    yield
    _reset_logger()


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
