"""Date and time skill for Jarvis."""

from datetime import datetime

from jarvis.skills.base import Skill
from jarvis.claude_client import Tool


class DateTimeSkill(Skill):
    """Skill for getting current date and time."""

    name = "datetime"
    description = "Get current date and time information"

    def get_tools(self) -> list[Tool]:
        """Get datetime tools."""
        return [
            Tool(
                name="get_current_time",
                description="Get the current time in 24-hour format",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                handler=self.get_current_time,
            ),
            Tool(
                name="get_current_date",
                description="Get the current date with day of week",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                handler=self.get_current_date,
            ),
        ]

    def get_current_time(self) -> str:
        """Get the current time.

        Returns:
            Formatted time string.
        """
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def get_current_date(self) -> str:
        """Get the current date.

        Returns:
            Formatted date string.
        """
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y")
