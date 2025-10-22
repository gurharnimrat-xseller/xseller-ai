"""
Simple Publer.io API wrapper.
"""
import json
import os
from pathlib import Path
from typing import List

import requests

PUBLER_KEY = os.getenv("PUBLER_API_KEY")
WORKSPACE_ID = os.getenv("PUBLER_WORKSPACE_ID")
BASE = os.getenv("PUBLER_BASE_URL", "https://api.publer.io/v1")
LOGS = Path("logs")
LOGS.mkdir(exist_ok=True)


class PublerError(Exception):
    """Raised when Publer.io returns an error or configuration is missing."""


def _hdr() -> dict:
    if not PUBLER_KEY:
        raise PublerError("Missing PUBLER_API_KEY")
    return {"Authorization": f"Bearer {PUBLER_KEY}", "Content-Type": "application/json"}


def ping() -> bool:
    """Return True if the Publer API responds successfully."""
    try:
        response = requests.get(f"{BASE}/me", headers=_hdr(), timeout=10)
        return response.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def list_platforms() -> dict:
    """List connected platform accounts for the configured workspace."""
    if not WORKSPACE_ID:
        raise PublerError("Missing PUBLER_WORKSPACE_ID")
    response = requests.get(
        f"{BASE}/workspaces/{WORKSPACE_ID}/accounts", headers=_hdr(), timeout=15
    )
    response.raise_for_status()
    return response.json()


def create_post(
    text: str,
    media_urls: List[str],
    platforms: List[str],
    schedule: str = "now",
) -> dict:
    """Create a post via Publer for the given workspace."""
    if not WORKSPACE_ID:
        raise PublerError("Missing PUBLER_WORKSPACE_ID")
    payload = {
        "workspace_id": WORKSPACE_ID,
        "text": text,
        "media": media_urls,
        "platforms": platforms,
        "schedule": schedule,
    }
    response = requests.post(
        f"{BASE}/posts", headers=_hdr(), json=payload, timeout=30
    )
    if response.status_code >= 300:
        LOGS.joinpath("publer_error.log").write_text(response.text)
        raise PublerError(f"{response.status_code}: {response.text}")
    try:
        return response.json()
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise PublerError("Invalid JSON response from Publer.io") from exc
