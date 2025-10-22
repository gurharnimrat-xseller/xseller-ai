import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# --- NEW: safe paths & loaders ---
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"

QUEUE_JSON = DATA_DIR / "ai_shorts_queue.json"
DB_JSON = DATA_DIR / "ai_shorts_db.json"
HOOKS_CSV = DATA_DIR / "hooks_lab.csv"


def _safe_read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        pass
    return default


def load_queue_json():
    """Returns (shorts_list, text_posts_list). Creates empty file on first run."""
    if not QUEUE_JSON.exists():
        QUEUE_JSON.write_text(json.dumps(
            {"shorts": [], "text_posts": []}, indent=2))
    data = _safe_read_json(QUEUE_JSON, {"shorts": [], "text_posts": []})
    if isinstance(data, list):
        shorts = [item for item in data if item.get("type") == "video"]
        text_posts = [item for item in data if item.get("type") == "text_post"]
        data = {"shorts": shorts, "text_posts": text_posts}
        QUEUE_JSON.write_text(json.dumps(data, indent=2))
    return data.get("shorts", []), data.get("text_posts", [])


def load_db_json():
    """Optional: local DB cache for the dashboard"""
    return _safe_read_json(DB_JSON, [])


def load_hooks_lab(path: Path = HOOKS_CSV) -> pd.DataFrame:
    """Create the CSV if missing; return a DataFrame."""
    if not path.exists():
        pd.DataFrame(
            columns=[
                "date",
                "story_title",
                "hook_style",
                "hook_text",
                "retention_3s",
                "ctr",
                "keep_or_kill",
            ]
        ).to_csv(path, index=False)
    return pd.read_csv(path)


def get_daily_output_dirs(base: Path):
    if not base.exists():
        return []
    dated_dirs = [
        d for d in base.iterdir() if d.is_dir() and d.name[0].isdigit() and "-" in d.name
    ]
    return sorted(dated_dirs, reverse=True)


def render_video_queue(queue_items):
    if not queue_items:
        st.info(
            "No video items queued. Pipeline will populate this section after the next run.")
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
            st.checkbox("Approve", key=f"video_approve_{item.get('id', '')}")


def render_text_posts(posts):
    if not posts:
        st.info(
            "No text posts generated yet. They will appear here after the pipeline run.")
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
                st.checkbox(
                    "Approve", key=f"text_{platform}_{post.get('id', '')}")


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

    shorts_queue, text_post_queue = load_queue_json()
    hooks_lab_records = load_hooks_lab(HOOKS_CSV)
    db_records = load_db_json()

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
        render_video_queue(shorts_queue)

    with tabs[1]:
        st.header("Text Posts")
        render_text_posts(text_post_queue)

    with tabs[2]:
        st.header("Hook Lab")
        st.write(
            "Upload weekly learnings or import `hooks_lab.csv` to track hooks, topics, and performance."
        )
        st.dataframe(hooks_lab_records)
        if db_records:
            st.markdown("### Recent Scripts")
            st.json(db_records)

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
    st.sidebar.markdown(
        f"Last refreshed: {datetime.utcnow():%Y-%m-%d %H:%M UTC}")


if __name__ == "__main__":
    main()
