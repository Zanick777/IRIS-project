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
