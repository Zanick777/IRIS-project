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
