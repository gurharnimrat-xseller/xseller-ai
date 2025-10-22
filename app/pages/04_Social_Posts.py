import json
from pathlib import Path
from typing import List

import streamlit as st

from services.publish_service import enqueue_post, process_queue

st.set_page_config(page_title="Social Posts", page_icon="📣", layout="wide")
st.title("📣 Social Posts")

DATA = Path("data")
DB = DATA / "ai_shorts_db.json"
QUEUE = DATA / "publish_queue.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_db() -> List[dict]:
    return _load_json(DB, [])


def load_queue() -> dict:
    return _load_json(QUEUE, {"items": []})


col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Rendered Videos")
    items = load_db()
    videos = [
        item
        for item in items
        if item.get("render", {}).get("mp4_url")
        and item.get("status") in ("rendered", "approved_video", "posted")
    ]
    if not videos:
        st.info("No rendered items found yet.")
        selected_video = None
    else:
        options = [
            f'{item.get("date", "unknown")} — {item.get("title", "Untitled")}'
            for item in videos
        ]
        selection = st.selectbox("Choose a video", options=options)
        selected_video = videos[options.index(selection)]
        st.video(selected_video["render"]["mp4_url"])
        default_caption = selected_video.get("script", "")[:250]
        caption = st.text_area("Caption", value=default_caption)
        hashtags = st.text_input(
            "Hashtags",
            value=" ".join(selected_video.get("hashtags", ["#AI", "#TechNews"])),
        )
        channel = st.selectbox(
            "Channel",
            options=[
                "youtube",
                "tiktok",
                "instagram",
                "facebook",
                "linkedin",
                "snapchat",
            ],
        )
        if st.button("Enqueue for Publish", disabled=selected_video is None):
            enqueue_post(
                selected_video["id"],
                channel,
                selected_video["render"]["mp4_url"],
                selected_video.get("title", "Untitled"),
                caption,
                hashtags,
            )
            st.success("Enqueued for publish.")

with col2:
    st.subheader("Publish Queue")
    if st.button("Process Queue Now"):
        process_queue()
        st.success("Queue processed. Refresh list below.")
    queue = load_queue()
    if not queue.get("items"):
        st.caption("Queue is empty.")
    else:
        for entry in queue["items"]:
            st.markdown(
                f"- **{entry['platform']}** — {entry.get('title','Untitled')} — `{entry['status']}`"
            )
            if entry.get("error"):
                st.caption(entry["error"])
