import json
from pathlib import Path
from typing import Dict, List

from services.repurpose_client import RepurposeError, publish_video


DATA = Path("data")
DATA.mkdir(exist_ok=True)
QUEUE = DATA / "publish_queue.json"

SUPPORTED_PLATFORMS = [
    "youtube",
    "tiktok",
    "instagram",
    "facebook",
    "linkedin",
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
    platform: str,
    mp4_url: str,
    title: str,
    caption: str,
    hashtags: str,
) -> bool:
    queue = _load_queue()
    queue["items"].append(
        {
            "item_id": item_id,
            "platform": platform,
            "mp4_url": mp4_url,
            "title": title,
            "caption": caption,
            "hashtags": hashtags,
            "status": "queued",
        }
    )
    _save_queue(queue)
    return True


def publish_one(entry: dict) -> dict:
    if entry["platform"] not in SUPPORTED_PLATFORMS:
        entry["status"] = "error"
        entry["error"] = "unsupported_platform"
        return {"status": "error", "error": "unsupported_platform"}
    try:
        response = publish_video(
            platform_id=entry["platform"],
            asset_url=entry["mp4_url"],
            title=entry["title"],
            caption=entry["caption"],
            hashtags=entry["hashtags"],
        )
    except RepurposeError as exc:
        entry["status"] = "error"
        entry["error"] = str(exc)
        return {"status": "error", "error": str(exc)}

    entry["status"] = "posted"
    entry["provider_response"] = response
    return {"status": "ok", "response": response}


def process_queue() -> Dict[str, List[dict]]:
    queue = _load_queue()
    updated = False
    for item in queue["items"]:
        if item.get("status") == "queued":
            publish_one(item)
            updated = True
    if updated:
        _save_queue(queue)
    return queue
