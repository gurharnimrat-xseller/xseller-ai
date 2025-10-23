"""Utilities for analytics data access and transformations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / "data"
ANALYTICS_PATH = DATA_DIR / "analytics_summary.json"


def load_summary(default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    default = default or {
        "metrics": {"retention": 0, "shares": 0, "follower_conversion": 0},
        "daily_posts": [],
        "platform_views": [],
    }
    if not ANALYTICS_PATH.exists():
        return default
    try:
        return json.loads(ANALYTICS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_summary(payload: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    ANALYTICS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
