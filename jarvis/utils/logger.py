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


def _reset_logger() -> None:
    """Reset logger state. For testing only."""
    global _initialized, _log_dir
    _initialized = False
    _log_dir = None
    root_logger = logging.getLogger("jarvis")
    root_logger.handlers.clear()
