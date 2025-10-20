from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from .hooks import HookSet
from .social import SocialPost
from .summarizer import Script

DEFAULT_QUEUE = {"shorts": [], "text_posts": []}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_queue(path: Path) -> Dict[str, List[dict]]:
    data = _load_json(path, DEFAULT_QUEUE.copy())
    if isinstance(data, list):
        # Backward compatibility with legacy structure
        shorts = [item for item in data if item.get("type") == "video"]
        text_posts = [item for item in data if item.get("type") == "text_post"]
        data = {"shorts": shorts, "text_posts": text_posts}
    data.setdefault("shorts", [])
    data.setdefault("text_posts", [])
    return data


def write_queue(path: Path, data: Dict[str, List[dict]]) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_history(path: Path | None) -> List[dict]:
    if not path:
        return []
    return _load_json(path, [])


def write_history(path: Path | None, data: List[dict]) -> None:
    if not path:
        return
    _ensure_parent(path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def merge_into_queue(
    queue_path: Path,
    scripts: Iterable[Script],
    hooks: Iterable[HookSet],
    social_posts: Iterable[SocialPost],
    db_path: Path | None = None,
    audio_paths: dict[str, str] | None = None,
) -> None:
    queue_data = load_queue(queue_path)
    shorts_index = {item.get("id"): idx for idx, item in enumerate(queue_data["shorts"]) if item.get("id")}
    text_index = {item.get("id"): idx for idx, item in enumerate(queue_data["text_posts"]) if item.get("id")}

    hooks_map = {h.script_id: h for h in hooks}
    social_map = {s.id: s for s in social_posts}
    history = load_history(db_path)
    history_ids = {item.get("id") for item in history}

    audio_paths = audio_paths or {}

    for script in scripts:
        hooks_data = hooks_map.get(script.id)
        social_data = social_map.get(script.id)

        short_payload = {
            "id": script.id,
            "title": script.title,
            "summary": script.summary,
            "why_it_matters": script.why_it_matters,
            "what_happened": script.what_happened,
            "whats_next": script.whats_next,
            "hooks": hooks_data.hooks if hooks_data else [],
            "video_path": script.link,
            "audio_path": audio_paths.get(script.id),
        }
        if script.id in shorts_index:
            queue_data["shorts"][shorts_index[script.id]].update(short_payload)
        else:
            queue_data["shorts"].append(short_payload)
            shorts_index[script.id] = len(queue_data["shorts"]) - 1

        if social_data:
            text_id = f"{script.id}-text"
            text_payload = {
                "id": text_id,
                "story_title": script.title,
                "platforms": {
                    platform: asdict(post)
                    for platform, post in social_data.platforms.items()
                },
            }
            if text_id in text_index:
                queue_data["text_posts"][text_index[text_id]].update(text_payload)
            else:
                queue_data["text_posts"].append(text_payload)
                text_index[text_id] = len(queue_data["text_posts"]) - 1

        if db_path and script.id not in history_ids:
            history.append(
                {
                    "id": script.id,
                    "title": script.title,
                    "summary": script.summary,
                    "source": script.link,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    write_queue(queue_path, queue_data)
    write_history(db_path, history)
