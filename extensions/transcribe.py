"""Extension containing voice transcription commands."""

import arc
from arc import AutodeferMode, GatewayClient, GatewayContext, GatewayPluginBase
from hikari import (
    Attachment,
    GuildMessageCreateEvent,
    Message,
    MessageFlag,
    MessageReference,
)
from hikari.messages import MessageReferenceType
from loguru import logger

from core.hooks import Hooks
from core.templates import Templates, TemplateType
from core.whisper import inference

plugin: GatewayPluginBase = GatewayPluginBase("transcribe", autodefer=AutodeferMode.ON)


@arc.loader
def ext_loader(client: GatewayClient) -> None:
    """Load this extension."""
    logger.debug(f"Loading the {plugin.name} extension")
    logger.trace(f"{plugin=}")

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load the {plugin.name} extension")

        return

    logger.info(f"Loaded the {plugin.name} extension")


@plugin.include
@arc.with_hook(Hooks.command_use)
@arc.message_command("Transcribe Audio")
async def command_transcribe(ctx: GatewayContext, msg: Message) -> None:
    """Handle the Transcribe Audio message command."""
    valid: list[Attachment] = await validate_attachments(msg)

    # Check for Forwarded Message
    if msg.message_reference:
        ref: MessageReference = msg.message_reference

        if ref.type == MessageReferenceType.FORWARD and ref.id:
            fwd: Message = await ctx.client.rest.fetch_message(ref.channel_id, ref.id)

            valid.extend(await validate_attachments(fwd))

    if not valid:
        await ctx.respond(
            component=Templates.generic(
                TemplateType.ERROR,
                f"{msg.make_link(msg.guild_id)} does not contain transcribable media.",
            )
        )

        return

    # Explicitly defer for safety
    await ctx.defer()

    if result := await transcribe_attachments(valid):
        await ctx.respond("\n\n".join(result))

        logger.success(f"Transcribed message {msg.id} in server {msg.guild_id}")
        logger.debug(f"{msg=}")


@plugin.listen()
async def event_transcribe(event: GuildMessageCreateEvent) -> None:
    """Transcribe voice messages upon creation."""
    valid: list[Attachment] = await validate_attachments(event.message, voice_only=True)

    if valid:
        if result := await transcribe_attachments(valid):
            await plugin.client.rest.create_message(
                event.message.channel_id, "\n\n".join(result), reply=event.message.id
            )

        logger.success(
            f"Transcribed voice message {event.message.id} in server {event.message.guild_id}"
        )
        logger.debug(f"{event=}")


async def validate_attachments(
    msg: Message, *, voice_only: bool = False
) -> list[Attachment]:
    """Return a list of attachments valid for transcription."""
    valid: list[Attachment] = []

    if MessageFlag.IS_VOICE_MESSAGE in msg.flags:
        logger.debug(f"Voice message {msg.id} attachments are valid for transcription")
        logger.trace(f"{msg=}")

        valid.extend(msg.attachments)
    else:
        if voice_only:
            logger.debug(
                f"Non-voice message {msg.id} attachments are not valid for transcription"
            )
            logger.trace(f"{msg=}")

            return valid

        for attachment in msg.attachments:
            if not attachment.media_type:
                logger.debug(
                    f"Skipped attachment {attachment.filename} on message {msg.id}, unknown media type"
                )
                logger.trace(f"{msg=}")

                continue

            media_type: str = attachment.media_type.lower()

            if media_type.startswith("audio/"):
                logger.debug(
                    f"{media_type} attachment {attachment.filename} on message {msg.id} is valid for transcription"
                )
                logger.trace(f"{msg=}")

                valid.append(attachment)
            elif media_type.startswith("video/"):
                logger.debug(
                    f"{media_type} attachment {attachment.filename} on message {msg.id} is valid for transcription"
                )
                logger.trace(f"{msg=}")

                valid.append(attachment)

    return valid


async def transcribe_attachments(attachments: list[Attachment]) -> list[str]:
    """Return a list of transcriptions for the provided attachments."""
    transcriptions: list[str] = []

    for attachment in attachments:
        transcription: str | None = await inference(
            attachment.url, attachment.filename, attachment.media_type
        )

        if transcription:
            transcriptions.append(transcription)

    if not transcriptions:
        raise RuntimeError(
            f"Failed to generate transcription for attachment {attachment.filename}"
        )

    logger.debug(f"Transcribed attachment {attachment.filename}")
    logger.debug(f"{transcriptions=}")

    return transcriptions


@plugin.set_error_handler
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handle errors originating from this plugin."""
    await Hooks.command_error(ctx, error)
