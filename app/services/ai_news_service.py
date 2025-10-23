"""Helpers for AI news articles and queue state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / "data"
QUEUE_PATH = DATA_DIR / "ai_shorts_queue.json"
DB_PATH = DATA_DIR / "ai_shorts_db.json"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_queue() -> Dict[str, List[dict]]:
    data = _load_json(QUEUE_PATH, {"shorts": [], "text_posts": []})
    if isinstance(data, list):
        return {"shorts": data, "text_posts": []}
    return data


def load_db() -> List[dict]:
    return _load_json(DB_PATH, [])


def save_queue(payload: Dict[str, List[dict]]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
