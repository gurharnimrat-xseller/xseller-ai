import json
import os
from pathlib import Path
from typing import Any, Dict

import requests

REP_API = os.getenv("REPURPOSE_API_KEY")
REP_BASE = os.getenv("REPURPOSE_API_BASE", "https://api.repurpose.io/v1")
LOGS = Path("logs")
LOGS.mkdir(parents=True, exist_ok=True)


class RepurposeError(Exception):
    """Raised when Repurpose.io returns an error response."""


def _auth_headers() -> Dict[str, str]:
    if not REP_API:
        raise RepurposeError("REPURPOSE_API_KEY missing")
    return {"Authorization": f"Bearer {REP_API}", "Content-Type": "application/json"}


def ping() -> bool:
    """Return True if the Repurpose API is reachable with the configured key."""
    if not REP_API:
        return False
    try:
        response = requests.get(f"{REP_BASE}/ping", headers=_auth_headers(), timeout=15)
        return response.status_code in (200, 404, 405)
    except Exception:
        return False


def platforms() -> Dict[str, Any]:
    """Return the list of connected platforms from Repurpose."""
    response = requests.get(f"{REP_BASE}/platforms", headers=_auth_headers(), timeout=20)
    response.raise_for_status()
    return response.json()


def publish_video(
    platform_id: str,
    asset_url: str,
    title: str,
    caption: str,
    hashtags: str,
    schedule: str = "now",
) -> Dict[str, Any]:
    """
    Publish a video asset to a Repurpose-connected platform.

    Adjust payload with workflow_id if required by your Repurpose plan.
    """
    payload = {
        "platform": platform_id,
        "source_url": asset_url,
        "title": title[:80],
        "caption": f"{caption}\n{hashtags}".strip(),
        "schedule": schedule,
    }
    try:
        response = requests.post(
            f"{REP_BASE}/publish",
            headers=_auth_headers(),
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:  # pragma: no cover
        LOGS.joinpath("repurpose_error.log").write_text(str(exc))
        raise RepurposeError(str(exc)) from exc

    if response.status_code >= 300:
        LOGS.joinpath("repurpose_error.log").write_text(response.text)
        raise RepurposeError(f"{response.status_code}: {response.text}")
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        raise RepurposeError("Invalid JSON response from Repurpose.io") from exc
