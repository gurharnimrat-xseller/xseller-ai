"""GetLate.dev API client."""
from __future__ import annotations

import os
from typing import List

import requests

GETLATE_KEY = os.getenv("GETLATE_API_KEY")
BASE = os.getenv("GETLATE_BASE_URL", "https://api.getlate.dev/v1")


class GetLateError(Exception):
    """Raised when GetLate.dev returns an error response."""


def _headers() -> dict:
    if not GETLATE_KEY:
        raise GetLateError("Missing GETLATE_API_KEY")
    return {"Authorization": f"Bearer {GETLATE_KEY}", "Content-Type": "application/json"}


def post_to_getlate(
    title: str,
    caption: str,
    media_urls: List[str],
    platforms: List[str],
) -> dict:
    payload = {
        "title": title,
        "text": caption,
        "media": media_urls,
        "platforms": platforms,
        "schedule": "now",
    }
    response = requests.post(
        f"{BASE}/posts",
        headers=_headers(),
        json=payload,
        timeout=20,
    )
    if response.status_code >= 300:
        raise GetLateError(f"{response.status_code}: {response.text}")
    return response.json()
