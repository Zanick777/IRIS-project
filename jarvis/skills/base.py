"""Base classes for Jarvis skills."""

import inspect
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
        if inspect.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)
