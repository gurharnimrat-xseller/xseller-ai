from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.services.ai_news_service import load_queue
from app.services.theme_manager import theme_toggle
from app.ui_utils import inject_global_styles

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"

st.set_page_config(page_title="AI News Shorts", page_icon="📰", layout="wide")
theme_toggle(default="dark")
inject_global_styles()
st.title("📰 AI News Shorts Queue")

queue_data = load_queue()
queue_items = queue_data.get("items", [])
short_items = [item for item in queue_items if item.get("type") in {"video", "short", "short_video"}]
col_a, col_b, col_c = st.columns(3)
col_a.metric("Queued Videos", len(short_items))
produced = len(list(OUTPUTS_DIR.glob("*/video/*.mp4"))) if OUTPUTS_DIR.exists() else 0
col_b.metric("Rendered Videos", produced)
col_c.metric("Pending Scripts", max(len(short_items) - produced, 0))

st.write("---")

if not short_items:
    st.info("No AI News Shorts queued yet. Run the automation pipeline to populate this tab.")
else:
    df = pd.DataFrame(
        [
            {
                "Title": item.get("title"),
                "Summary": (item.get("summary", "")[:140] + "…") if item.get("summary") else "",
                "Hooks": len(item.get("hooks", [])),
                "Has Audio": bool(item.get("audio_path")),
            }
            for item in short_items
        ]
    )
    st.dataframe(df, use_container_width=True)

    with st.expander("Preview & Approve", expanded=False):
        titles = [item.get("title", "Untitled") for item in short_items]
        selected_title = st.selectbox("Select short to preview", options=titles)
        current = short_items[titles.index(selected_title)]
        st.write(current.get("summary", "No summary yet."))
        hooks = current.get("hooks", [])
        if hooks:
            st.markdown("**Hook Lab Variants**")
            for hook in hooks:
                st.success(hook)
        video_path = current.get("video_path")
        if video_path and Path(video_path).exists():
            st.video(video_path)
        audio_path = current.get("audio_path")
        if audio_path and Path(audio_path).exists():
            st.audio(audio_path)
        st.button("Mark Approved", key=f"approve_{current.get('id')}")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export queue as CSV", csv, file_name="ai_news_shorts_queue.csv")

st.write("---")
st.caption("Need platform outputs? Jump to the Social Posts tab to publish.")
