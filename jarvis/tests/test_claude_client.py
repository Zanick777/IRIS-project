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
