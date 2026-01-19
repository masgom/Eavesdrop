"""Reusable message templates."""

from enum import Enum, auto
from typing import Self

from hikari import Color
from hikari.impl import ContainerComponentBuilder, TextDisplayComponentBuilder

from core.consts import Colors


class TemplateType(Enum):
    """Enumeration of template types."""

    INFO = auto()
    WARN = auto()
    ERROR = auto()
    SUCCESS = auto()

    @property
    def color(self: Self) -> Color:
        """Return the color associated with the template type."""
        return {
            TemplateType.INFO: Color.from_hex_code(Colors.BLURPLE),
            TemplateType.WARN: Color.from_hex_code(Colors.YELLOW),
            TemplateType.ERROR: Color.from_hex_code(Colors.RED),
            TemplateType.SUCCESS: Color.from_hex_code(Colors.GREEN),
        }.get(self, Color.from_hex_code(Colors.BLACK))


class Templates:
    """Reusable message templates."""

    @staticmethod
    def generic(template_type: TemplateType, message: str) -> ContainerComponentBuilder:
        """Template for a standard message."""
        return ContainerComponentBuilder(
            accent_color=template_type.color,
            components=[TextDisplayComponentBuilder(content=message)],
        )
