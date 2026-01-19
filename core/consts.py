"""Enumerations and constant values."""

from enum import StrEnum, auto
from pathlib import Path
from typing import Final

from environs import env
from loguru import logger

if env.read_env(Path(__file__).resolve().parent.parent / ".env", recurse=False):
    logger.success("Loaded environment variables")


class Environment(StrEnum):
    """Enumeration of environment variable names."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        """Transform the value to uppercase."""
        return name.upper()

    LOG_LEVEL = auto()
    LOG_DISCORD_WEBHOOK_URL = auto()
    LOG_DISCORD_WEBHOOK_LEVEL = auto()
    DISCORD_BOT_TOKEN = auto()
    DISCORD_SERVER_IDS = auto()
    WHISPER_API_BASE_URL = auto()


LOG_LEVEL: Final[str | None] = env.str(Environment.LOG_LEVEL, default=None)
IS_DEBUG: Final[bool] = LOG_LEVEL in {"DEBUG", "TRACE"}
LOG_DISCORD_WEBHOOK_URL: Final[str | None] = env.str(
    Environment.LOG_DISCORD_WEBHOOK_URL, default=None
)
LOG_DISCORD_WEBHOOK_LEVEL: Final[str] = env.str(
    Environment.LOG_DISCORD_WEBHOOK_LEVEL, default="WARNING"
)
DISCORD_BOT_TOKEN: Final[str] = env.str(Environment.DISCORD_BOT_TOKEN)
DISCORD_SERVER_IDS: Final[list[int]] = env.list(
    Environment.DISCORD_SERVER_IDS, [], int, delimiter=","
)
WHISPER_API_BASE_URL: Final[str] = env.url(Environment.WHISPER_API_BASE_URL).geturl()


class Colors(StrEnum):
    """Enumeration of generic colors."""

    BLURPLE = "#5865F2"
    YELLOW = "#D1B036"
    RED = "#DA3E44"
    GREEN = "#6AAA64"
    BLACK = "#151515"
