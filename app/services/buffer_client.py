"""Buffer.com API client."""
from __future__ import annotations

import os
from typing import List

import requests

BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE = os.getenv("BUFFER_PROFILE_ID")
BASE = os.getenv("BUFFER_BASE_URL", "https://api.bufferapp.com/1")


class BufferError(Exception):
    """Raised when Buffer returns an error response."""


def _headers() -> dict:
    if not BUFFER_TOKEN:
        raise BufferError("Missing BUFFER_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {BUFFER_TOKEN}"}


def post_to_buffer(
    title: str,
    caption: str,
    media_urls: List[str],
    platforms: List[str],
) -> dict:
    if not BUFFER_PROFILE:
        raise BufferError("Missing BUFFER_PROFILE_ID")
    text = f"{title}\n\n{caption}".strip()
    media_payload = {"photo": media_urls[0]} if media_urls else {}
    payload = {
        "profile_ids": [BUFFER_PROFILE],
        "text": text,
        "media": media_payload,
        "now": True,
    }
    response = requests.post(
        f"{BASE}/updates/create.json",
        headers=_headers(),
        data=payload,
        timeout=20,
    )
    if response.status_code >= 300:
        raise BufferError(f"{response.status_code}: {response.text}")
    return response.json()
