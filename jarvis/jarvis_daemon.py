"""Jarvis daemon - main entry point."""

import asyncio
import sys
from pathlib import Path

from jarvis.config import load_config, Config
from jarvis.claude_client import ClaudeClient, ChatResponse
from jarvis.skills import SkillRegistry
from jarvis.skills.information import DateTimeSkill
from jarvis.utils.logger import setup_logger, get_logger

logger = get_logger("daemon")


class Jarvis:
    """Main Jarvis assistant class."""

    def __init__(self, config_path: Path | None = None):
        """Initialize Jarvis.

        Args:
            config_path: Optional path to config file.
        """
        # Load configuration
        self.config = load_config(config_path)

        # Setup logging
        setup_logger(
            log_dir=self.config.config_dir / "logs",
            console=True,
        )

        logger.info("Initializing Jarvis...")

        # Initialize Claude client
        self.claude = ClaudeClient(
            api_key=self.config.anthropic_api_key,
            model=self.config.model,
            user_name=self.config.user_name,
        )

        # Initialize skill registry
        self.skill_registry = SkillRegistry()
        self._register_default_skills()

        # Register all tools with Claude
        for tool in self.skill_registry.get_all_tools():
            self.claude.register_tool(tool)

        logger.info("Jarvis initialized successfully")

    def _register_default_skills(self) -> None:
        """Register built-in skills."""
        self.skill_registry.register(DateTimeSkill())

    async def process(self, message: str) -> str:
        """Process a user message and return response.

        Args:
            message: User's message.

        Returns:
            Jarvis's response text.
        """
        logger.debug(f"Processing: {message}")

        # Get initial response from Claude
        response = await self.claude.chat(message)

        # Handle tool calls if any
        while response.tool_calls:
            for tool_call in response.tool_calls:
                logger.debug(f"Executing tool: {tool_call.name}")
                try:
                    result = await self.skill_registry.execute(
                        tool_call.name,
                        tool_call.arguments,
                    )
                    response = await self.claude.submit_tool_result(
                        tool_call.id,
                        result,
                    )
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    response = await self.claude.submit_tool_result(
                        tool_call.id,
                        f"Error: {e}",
                    )

        return response.text

    async def run_repl(self) -> None:
        """Run interactive REPL mode."""
        print("\n" + "=" * 50)
        print("  JARVIS - Personal AI Assistant")
        print("  Type 'quit' or 'exit' to stop")
        print("=" * 50 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("quit", "exit", "q"):
                    print("\nGoodbye!")
                    break

                # Process and respond
                response = await self.process(user_input)
                print(f"\nJarvis: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}\n")


async def main():
    """Main entry point."""
    jarvis = Jarvis()
    await jarvis.run_repl()


if __name__ == "__main__":
    asyncio.run(main())
