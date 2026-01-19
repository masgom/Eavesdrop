"""Module containing lifecycle and command hooks."""

from arc import GatewayContext, InvokerMissingPermissionsError, NotOwnerError
from loguru import logger

from core.templates import Templates, TemplateType


class Hooks:
    """Reusable hooks for the Eavesdrop Discord bot."""

    @staticmethod
    async def command_use(ctx: GatewayContext) -> None:
        """Handle command pre-execution."""
        logger.info(f"Command used by {ctx.user.display_name} in {ctx.channel.name}")

    @staticmethod
    async def command_error(ctx: GatewayContext, error: Exception) -> None:
        """Handle uncaught command exceptions."""
        if isinstance(error, (NotOwnerError, InvokerMissingPermissionsError)):
            await ctx.respond(
                component=Templates.generic(
                    TemplateType.ERROR, "You don't have permission to use this command."
                )
            )

            return

        logger.opt(exception=error).error("An unexpected error occurred in command")

        await ctx.respond(
            component=Templates.generic(
                TemplateType.ERROR, "An unexpected error occurred. Try again later."
            )
        )
