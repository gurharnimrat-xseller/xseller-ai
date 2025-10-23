"""Unified publish pipeline supporting GetLate, Buffer, and Publer."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app.services.buffer_client import post_to_buffer
from app.services.getlate_client import post_to_getlate

try:
    from app.services.publer_client import create_post
except Exception:  # pragma: no cover - optional dependency guard
    class PublerMissing(Exception):
        pass

    def create_post(*_args, **_kwargs):  # type: ignore
        raise PublerMissing("Publer client not available")


DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(exist_ok=True)
QUEUE = DATA / "publish_queue.json"
CONFIG = DATA / "last_provider.json"

SUPPORTED_PLATFORMS = [
    "youtube",
    "tiktok",
    "instagram",
    "facebook",
    "linkedin",
    "twitter",
    "snapchat",
    "pinterest",
]

PROVIDERS = ["getlate", "buffer", "publer"]


def _load_queue() -> Dict[str, List[dict]]:
    if not QUEUE.exists():
        QUEUE.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
    try:
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"items": []}


def _save_queue(queue: Dict[str, List[dict]]) -> None:
    QUEUE.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def _remember_provider(name: str) -> None:
    CONFIG.write_text(
        json.dumps({"provider": name, "ts": datetime.utcnow().isoformat()}, indent=2),
        encoding="utf-8",
    )


def _last_provider() -> str:
    if CONFIG.exists():
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            provider = data.get("provider")
            if provider in PROVIDERS:
                return provider
        except (json.JSONDecodeError, OSError):  # pragma: no cover
            pass
    env_provider = os.getenv("POST_PROVIDER", "getlate")
    return env_provider if env_provider in PROVIDERS else "getlate"


def enqueue_post(
    item_id: str,
    title: str,
    caption: str,
    media: List[str],
    platforms: List[str],
    provider: str | None = None,
) -> bool:
    queue = _load_queue()
    queue["items"].append(
        {
            "item_id": item_id,
            "title": title,
            "caption": caption,
            "media": media,
            "platforms": platforms,
            "status": "queued",
            "provider": provider or _last_provider(),
        }
    )
    _save_queue(queue)
    return True


def _dispatch(
    provider: str,
    title: str,
    caption: str,
    media: List[str],
    platforms: List[str],
) -> dict:
    if provider == "getlate":
        try:
            return {"provider": "getlate", "resp": post_to_getlate(title, caption, media, platforms)}
        except Exception as exc:
            return {"provider": "getlate", "error": str(exc)}
    if provider == "buffer":
        try:
            return {"provider": "buffer", "resp": post_to_buffer(title, caption, media, platforms)}
        except Exception as exc:
            return {"provider": "buffer", "error": str(exc)}
    if provider == "publer":
        try:
            text = f"{title}\n\n{caption}".strip()
            return {"provider": "publer", "resp": create_post(text=text, media_urls=media, platforms=platforms)}
        except Exception as exc:
            return {"provider": "publer", "error": str(exc)}
    return {"provider": provider, "error": f"Unknown provider {provider}"}


def publish_one(entry: dict) -> dict:
    provider = entry.get("provider") or _last_provider()
    result = _dispatch(provider, entry["title"], entry["caption"], entry["media"], entry["platforms"])
    if "error" in result:
        entry["status"] = "error"
        entry["error"] = result["error"]
    else:
        entry["status"] = "posted"
        entry["response"] = result["resp"]
    entry["provider"] = provider
    return result


def process_queue(provider: str | None = None) -> Dict[str, List[dict]]:
    queue = _load_queue()
    selected_provider = provider or _last_provider()
    changed = False
    for item in queue["items"]:
        if item.get("status") == "queued":
            item["provider"] = selected_provider
            publish_one(item)
            changed = True
    if changed:
        _save_queue(queue)
    _remember_provider(selected_provider)
    return queue


__all__ = [
    "enqueue_post",
    "process_queue",
    "_last_provider",
    "SUPPORTED_PLATFORMS",
    "PROVIDERS",
]
