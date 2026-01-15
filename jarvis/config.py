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
