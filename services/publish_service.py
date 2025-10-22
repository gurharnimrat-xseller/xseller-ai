"""
Queue + publish pipeline via Publer API.
"""
import json
from pathlib import Path
from typing import Dict, List

from services.publer_client import PublerError, create_post

DATA = Path("data")
DATA.mkdir(exist_ok=True)
QUEUE = DATA / "publish_queue.json"

SUPPORTED_PLATFORMS = [
    "facebook",
    "instagram",
    "linkedin",
    "twitter",
    "youtube",
    "tiktok",
    "pinterest",
    "snapchat",
]


def _load_queue() -> Dict[str, List[dict]]:
    if not QUEUE.exists():
        QUEUE.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
    try:
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"items": []}


def _save_queue(obj: Dict[str, List[dict]]) -> None:
    QUEUE.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def enqueue_post(
    item_id: str,
    title: str,
    caption: str,
    media: List[str],
    platforms: List[str],
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
        }
    )
    _save_queue(queue)
    return True


def publish_one(entry: dict) -> dict:
    text = f"{entry['title']}\n\n{entry['caption']}".strip()
    try:
        response = create_post(
            text=text,
            media_urls=entry["media"],
            platforms=entry["platforms"],
        )
    except PublerError as exc:
        entry["status"] = "error"
        entry["error"] = str(exc)
        return {"status": "error", "error": str(exc)}

    entry["status"] = "posted"
    entry["response"] = response
    return {"status": "ok", "resp": response}


def process_queue() -> Dict[str, List[dict]]:
    queue = _load_queue()
    changed = False
    for item in queue["items"]:
        if item.get("status") == "queued":
            publish_one(item)
            changed = True
    if changed:
        _save_queue(queue)
    return queue
