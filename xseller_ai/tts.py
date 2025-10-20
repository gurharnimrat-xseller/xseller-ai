from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from .settings import settings

logger = logging.getLogger(__name__)

try:
    from elevenlabs import ElevenLabs  # type: ignore
except ImportError:  # pragma: no cover
    ElevenLabs = None  # type: ignore


def synthesize_speech(
    text: str,
    output_path: Path,
    *,
    voice_id: str | None = None,
    model_id: str | None = None,
    api_key: Optional[str] = None,
) -> Optional[Path]:
    """Generate TTS audio using ElevenLabs if credentials are available."""
    api_key = api_key or settings.elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning("ELEVENLABS_API_KEY missing; skipping TTS generation.")
        return None
    if ElevenLabs is None:
        logger.warning("elevenlabs package not installed; skipping TTS generation.")
        return None

    voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "Bella")
    model_id = model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2")

    client = ElevenLabs(api_key=api_key)
    logger.info("Generating TTS audio with ElevenLabs voice=%s model=%s", voice_id, model_id)

    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=model_id,
            text=text,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("ElevenLabs TTS failed: %s", exc)
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(audio)
    return output_path
