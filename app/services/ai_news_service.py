from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
QUEUE_FP = DATA_DIR / "ai_shorts_queue.json"
DB_FP = DATA_DIR / "ai_shorts_db.json"


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUEUE_FP.exists():
        QUEUE_FP.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
    if not DB_FP.exists():
        DB_FP.write_text(json.dumps([], indent=2), encoding="utf-8")


def _normalise_queue(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        items = data.get("items")
        if items is None:
            items = []
            for short in data.get("shorts", []):
                entry = dict(short)
                entry.setdefault("type", "video")
                items.append(entry)
            for post in data.get("text_posts", []):
                entry = dict(post)
                entry.setdefault("type", "text_post")
                items.append(entry)
        return {"items": items}
    if isinstance(data, list):
        return {"items": data}
    return {"items": []}


def load_queue() -> Dict[str, Any]:
    """Return queue as {'items': [...]} regardless of legacy format."""
    _ensure_files()
    try:
        raw = json.loads(QUEUE_FP.read_text(encoding="utf-8"))
    except Exception:  # pragma: no cover
        return {"items": []}
    return _normalise_queue(raw)


def load_db() -> List[Dict[str, Any]]:
    """Returns the full items DB (list)."""
    _ensure_files()
    try:
        return json.loads(DB_FP.read_text(encoding="utf-8"))
    except Exception:  # pragma: no cover
        return []


def save_queue(obj: Dict[str, Any]) -> None:
    _ensure_files()
    payload = _normalise_queue(obj)
    QUEUE_FP.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_db(items: List[Dict[str, Any]]) -> None:
    _ensure_files()
    DB_FP.write_text(json.dumps(items, indent=2), encoding="utf-8")
