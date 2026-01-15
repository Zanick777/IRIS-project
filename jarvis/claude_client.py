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
