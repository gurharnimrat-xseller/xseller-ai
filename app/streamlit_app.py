import csv
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"


def load_json(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_daily_output_dirs(base: Path):
    if not base.exists():
        return []
    dated_dirs = [
        d for d in base.iterdir() if d.is_dir() and d.name[0].isdigit() and "-" in d.name
    ]
    return sorted(dated_dirs, reverse=True)


def render_video_queue(queue_items):
    if not queue_items:
        st.info("No video items queued. Pipeline will populate this section after the next run.")
        return

    for item in queue_items:
        with st.expander(item.get("title", "Untitled Video"), expanded=False):
            st.write(item.get("summary", ""))
            hooks = item.get("hooks", [])
            if hooks:
                st.write("**Hook Lab Variants**")
                for hook in hooks:
                    st.markdown(f"- {hook}")
            video_path = item.get("video_path")
            if video_path and Path(video_path).exists():
                st.video(str(video_path))
            audio_path = item.get("audio_path")
            if audio_path and Path(audio_path).exists():
                st.audio(str(audio_path))
            st.checkbox("Approve", key=f"video_approve_{item.get('id','')}")


def render_text_posts(posts):
    if not posts:
        st.info("No text posts generated yet. They will appear here after the pipeline run.")
        return

    for post in posts:
        story_title = post.get("story_title", "AI Update")
        with st.expander(story_title, expanded=False):
            for platform, content in post.get("platforms", {}).items():
                st.markdown(f"### {platform}")
                st.write(content.get("caption", ""))
                image_path = content.get("image_path")
                if image_path and Path(image_path).exists():
                    st.image(str(image_path))
                elif prompt := content.get("image_prompt"):
                    st.caption(f"Image prompt: {prompt}")
                st.checkbox("Approve", key=f"text_{platform}_{post.get('id','')}")


def render_outputs():
    st.subheader("Daily Output Folders")
    dirs = get_daily_output_dirs(OUTPUTS_DIR)
    if not dirs:
        st.info("No dated output directories yet.")
        return

    selected_day = st.selectbox(
        "Select run date",
        options=[d.name for d in dirs],
        index=0,
    )
    videos_dir = OUTPUTS_DIR / selected_day / "video"
    social_dir = OUTPUTS_DIR / selected_day / "social"

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Videos**")
        if videos_dir.exists():
            for file in videos_dir.glob("*.mp4"):
                st.markdown(f"- {file.name}")
        else:
            st.caption("No videos saved.")

    with cols[1]:
        st.markdown("**Social Posts**")
        if social_dir.exists():
            for file in social_dir.iterdir():
                st.markdown(f"- {file.name}")
        else:
            st.caption("No social assets saved.")


def main():
    st.set_page_config(page_title="Xseller AI Dashboard", layout="wide")

    st.title("🤖 XSELLER.AI — Daily AI News Automation")
    st.caption("Monitor AI shorts, social posts, and automation performance.")

    queue_path = DATA_DIR / "ai_shorts_queue.json"
    queue_items = load_json(queue_path)
    video_items = [item for item in queue_items if item.get("type") == "video"]
    text_post_items = [item for item in queue_items if item.get("type") == "text_post"]
    hooks_lab_records = load_hooks_lab(DATA_DIR / "hooks_lab.csv")

    tabs = st.tabs(
        [
            "AI News Shorts",
            "Text Posts",
            "Hook Lab",
            "KPI Dashboard",
            "Outputs",
        ]
    )

    with tabs[0]:
        st.header("AI News Shorts Queue")
        render_video_queue(video_items)

    with tabs[1]:
        st.header("Text Posts")
        render_text_posts(text_post_items)

    with tabs[2]:
        st.header("Hook Lab")
        st.write(
            "Upload weekly learnings or import `hooks_lab.csv` to track hooks, topics, and performance."
        )
        st.dataframe(hooks_lab_records)

    with tabs[3]:
        st.header("KPI Dashboard")
        st.write(
            "Integrate your analytics source here (Repurpose.io, platform APIs) to surface retention, shares, and conversions."
        )
        st.metric("Retention @ 75%", "—", "Target: ≥60%")
        st.metric("Shares / 1k Views", "—", "Target: ≥25")
        st.metric("Follower Conversion", "—", "Target: ≥1.8%")

    with tabs[4]:
        render_outputs()

    st.sidebar.success(
        "Connected domain: app.xseller.ai is live!"
    )
    st.sidebar.markdown(f"Last refreshed: {datetime.utcnow():%Y-%m-%d %H:%M UTC}")


if __name__ == "__main__":
    main()
