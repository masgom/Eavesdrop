"""Entrypoint for the Eavesdrop Discord bot."""

from os import name as OS_NAME
from sys import stdout

from arc import GatewayClient
from hikari import (
    Activity,
    ActivityType,
    ApplicationContextType,
    GatewayBot,
    GatewayConnectionError,
    Intents,
    Permissions,
)
from loguru import logger
from loguru_discord import DiscordSink
from loguru_discord.intercept import Intercept

from core.consts import (
    DISCORD_BOT_TOKEN,
    DISCORD_SERVER_IDS,
    IS_DEBUG,
    LOG_DISCORD_WEBHOOK_LEVEL,
    LOG_DISCORD_WEBHOOK_URL,
    LOG_LEVEL,
)


def start() -> None:
    """Initialize the Eavesdrop Discord Bot."""
    logger.info("Eavesdrop - Voice Message Transcription")
    logger.info("https://github.com/EthanC/Eavesdrop")

    if LOG_LEVEL:
        logger.remove()
        logger.add(stdout, level=LOG_LEVEL)

        logger.success(f"Set console logging level to {LOG_LEVEL}")

    Intercept.setup({"TRACE_HIKARI": "TRACE"})

    if LOG_DISCORD_WEBHOOK_URL:
        logger.add(
            DiscordSink(LOG_DISCORD_WEBHOOK_URL, suppress=[GatewayConnectionError]),
            level=LOG_DISCORD_WEBHOOK_LEVEL,
            backtrace=False,
        )

        logger.success(
            f"Enabled logging to Discord webhook at level {LOG_DISCORD_WEBHOOK_LEVEL}"
        )

    # Replace default asyncio event loop with libuv on UNIX
    # https://github.com/hikari-py/hikari#uvloop
    if OS_NAME != "nt":
        try:
            import uvloop  # type: ignore

            uvloop.install()

            logger.success("Installed libuv event loop")
        except Exception as e:
            logger.opt(exception=e).debug("Defaulted to asyncio event loop")

    bot: GatewayBot = GatewayBot(
        DISCORD_BOT_TOKEN,
        allow_color=False,
        banner=None,
        suppress_optimization_warning=IS_DEBUG,
        intents=Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT,
    )
    client: GatewayClient = GatewayClient(
        bot,
        default_enabled_guilds=DISCORD_SERVER_IDS,
        default_permissions=Permissions.VIEW_CHANNEL
        | Permissions.READ_MESSAGE_HISTORY
        | Permissions.SEND_MESSAGES,
        invocation_contexts=[ApplicationContextType.GUILD],
    )

    client.set_type_dependency(GatewayBot, bot)

    client.load_extensions_from("extensions")

    bot.run(
        activity=Activity(
            name="Eavesdropping on voice messages", type=ActivityType.LISTENING
        ),
        asyncio_debug=IS_DEBUG,
        check_for_updates=False,
    )


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        logger.debug("Exiting due to keyboard interrupt")
    except Exception as e:
        logger.opt(exception=e).critical("Fatal error occurred during runtime")
