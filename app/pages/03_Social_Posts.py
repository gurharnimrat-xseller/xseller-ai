import json
from pathlib import Path

import streamlit as st

from app.services import buffer_client, getlate_client, publer_client
from app.services.publish_service import (
    PROVIDERS,
    enqueue_post,
    process_queue,
    _last_provider,
)

st.set_page_config(page_title="Social Posts", page_icon="📣", layout="wide")
st.title("📣 Multi-Provider Social Posts")

APP_ROOT = Path(__file__).resolve().parents[1]
DATA = APP_ROOT / "data"
CONFIG = APP_ROOT / "config" / "channels.json"
DB = DATA / "ai_shorts_db.json"
QUEUE = DATA / "publish_queue.json"

if CONFIG.exists():
    channel_meta = {item["id"]: item for item in json.loads(CONFIG.read_text(encoding="utf-8"))}
else:
    channel_meta = {}


def load_db() -> list:
    if DB.exists():
        try:
            return json.loads(DB.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def load_queue() -> dict:
    if QUEUE.exists():
        try:
            return json.loads(QUEUE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"items": []}
    return {"items": []}


current_provider = st.session_state.get("provider", _last_provider())

provider = st.selectbox(
    "Select Publishing Provider",
    PROVIDERS,
    index=PROVIDERS.index(current_provider) if current_provider in PROVIDERS else 0,
)
st.session_state["provider"] = provider

if provider == "getlate" and not getlate_client.GETLATE_KEY:
    st.warning("GetLate API key missing — posts will remain in queue until configured.")
elif provider == "buffer" and (not buffer_client.BUFFER_TOKEN or not buffer_client.BUFFER_PROFILE):
    st.warning("Buffer credentials missing — set BUFFER_ACCESS_TOKEN and BUFFER_PROFILE_ID.")
elif provider == "publer" and not publer_client.PUBLER_KEY:
    st.warning("Publer API key missing — enable PUBLER_API_KEY and PUBLER_WORKSPACE_ID.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Rendered Videos")
    items = load_db()
    videos = [item for item in items if item.get("render", {}).get("mp4_url")]
    if not videos:
        st.info("No rendered videos yet.")
    else:
        titles = [video.get("title", "Untitled") for video in videos]
        selected_title = st.selectbox("Select video", options=titles)
        chosen = videos[titles.index(selected_title)]
        st.video(chosen["render"]["mp4_url"])
        caption = st.text_area("Caption", value=chosen.get("script", "")[:250])
        platform_options = [
            "facebook",
            "instagram",
            "linkedin",
            "twitter",
            "youtube",
            "tiktok",
            "pinterest",
            "snapchat",
        ]
        label_map = {
            pid: f"{channel_meta.get(pid, {}).get('icon', '•')} {pid.title()}"
            for pid in platform_options
        }
        platforms = st.multiselect(
            "Select Platforms",
            options=platform_options,
            format_func=lambda pid: label_map.get(pid, pid.title()),
            default=["instagram", "tiktok"],
        )
        disabled = not platforms
        if st.button("Enqueue Post", disabled=disabled):
            enqueue_post(
                chosen["id"],
                chosen.get("title", "Untitled"),
                caption,
                [chosen["render"]["mp4_url"]],
                platforms,
                provider,
            )
            st.success(f"✅ Queued for {provider.title()}!")

with col2:
    st.subheader("Publish Queue")
    if st.button("Process Queue Now"):
        process_queue(provider)
        st.success(f"Queue processed using {provider.title()}")
    queue = load_queue()
    if not queue.get("items"):
        st.caption("Queue is empty.")
    else:
        for entry in queue.get("items", []):
            pretty_platforms = ", ".join(label_map.get(pid, pid.title()) for pid in entry.get("platforms", []))
            st.write(
                f"{entry['title']} → {pretty_platforms} → {entry['status']} ({entry.get('provider', '-')})"
            )
            if entry.get("error"):
                st.caption(entry["error"])
