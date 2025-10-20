from __future__ import annotations

import json
from datetime import datetime
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from .hooks import HookSet
from .social import SocialPost
from .summarizer import Script


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_queue(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_queue(path: Path, data: List[dict]) -> None:
    ensure_dir(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_db(path: Path) -> List[dict]:
    return load_queue(path)


def merge_into_queue(
    queue_path: Path,
    scripts: Iterable[Script],
    hooks: Iterable[HookSet],
    social_posts: Iterable[SocialPost],
    db_path: Path | None = None,
    audio_paths: dict[str, str] | None = None,
) -> None:
    queue = load_queue(queue_path)
    queue_index = {item["id"]: idx for idx, item in enumerate(queue) if "id" in item}
    hooks_map = {h.script_id: h for h in hooks}
    social_map = {s.id: s for s in social_posts}
    history = load_db(db_path) if db_path else []
    existing_history_ids = {item.get("id") for item in history}
    for script in scripts:
        hooks_data = hooks_map.get(script.id)
        social_data = social_map.get(script.id)
        video_entry = {
            "id": script.id,
            "type": "video",
            "title": script.title,
            "summary": script.summary,
            "why_it_matters": script.why_it_matters,
            "what_happened": script.what_happened,
            "whats_next": script.whats_next,
            "hooks": hooks_data.hooks if hooks_data else [],
            "video_path": script.link,  # placeholder until media pipeline attaches files
            "audio_path": (audio_paths or {}).get(script.id),
        }
        if script.id in queue_index:
            queue[queue_index[script.id]].update(video_entry)
        else:
            queue.append(video_entry)
            queue_index[script.id] = len(queue) - 1

        if social_data:
            text_id = f"{script.id}-text"
            text_entry = {
                "id": text_id,
                "type": "text_post",
                "story_title": script.title,
                "platforms": {
                    platform: asdict(post)
                    for platform, post in social_data.platforms.items()
                },
            }
            if text_id in queue_index:
                queue[queue_index[text_id]].update(text_entry)
            else:
                queue.append(text_entry)
                queue_index[text_id] = len(queue) - 1

        if db_path and script.id not in existing_history_ids:
            history_entry = {
                "id": script.id,
                "title": script.title,
                "summary": script.summary,
                "source": script.link,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            history.append(history_entry)

    write_queue(queue_path, queue)
    if db_path:
        write_queue(db_path, history)
