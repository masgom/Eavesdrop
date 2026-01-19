"""Module for interacting with whisper.cpp."""

from typing import Any

import ffmpeg
import httpx
from httpx import AsyncClient, Response
from loguru import logger

from core.consts import WHISPER_API_BASE_URL


async def inference(
    audio_url: str, audio_name: str, audio_type: str | None
) -> str | None:
    """Return a text transcription of the audio from the provided URL."""
    async with AsyncClient() as client:
        async with client.stream("GET", audio_url) as res_audio:
            res_audio.raise_for_status()
            audio_data: bytes = await res_audio.aread()

            logger.debug(f"HTTP {res_audio.status_code} GET {res_audio.url}")
            logger.trace(f"{audio_data=}")

            # whisper.cpp requires WAV audio format
            if audio_type != "audio/wav":
                audio_data = await to_wav(audio_data)

            res: Response = (
                await client.post(
                    f"{WHISPER_API_BASE_URL}/inference",
                    data={
                        "temperature": "0.0",
                        "temperature_inc": "0.2",
                        "response_format": "json",
                    },
                    files={"file": (audio_name, audio_data, audio_type)},
                )
            ).raise_for_status()

            logger.debug(f"HTTP {res.status_code} GET {res.url}")
            logger.trace(f"{res.text=}")

            data: dict[str, Any] = res.json()

            if error := data.get("error"):
                raise RuntimeError(f"Whisper failed to transcribe audio: {error}")

            text: str | None = data.get("text")

            if not text:
                raise RuntimeError("Whisper returned no transcription text")

            result: str = ""

            for line in text.splitlines():
                result += f"> {line.strip()}\n"

            result = result.strip()

            logger.info(f"Transcribed audio {audio_name}: {result}")

            return result


async def to_wav(in_bytes: bytes) -> bytes:
    """Return the provided audio bytes as WAV format."""
    process = (
        ffmpeg.input("pipe:0")
        .output("pipe:1", format="wav")
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    wav, stderr = process.communicate(input=in_bytes)

    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed to convert to WAV: {stderr.decode()}")

    logger.debug("Converted input to WAV audio")

    return wav
