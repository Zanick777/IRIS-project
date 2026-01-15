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
