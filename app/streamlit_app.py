from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="XSELLER.AI Ops Console", page_icon="🤖", layout="wide")

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
CONFIG_DIR = APP_ROOT / "config"
ASSETS_DIR = APP_ROOT / "assets"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _load_dataframe(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(path)
    except Exception:  # pragma: no cover
        return pd.DataFrame(columns=columns)


ai_queue = _load_json(DATA_DIR / "ai_shorts_queue.json", {"shorts": [], "text_posts": []})
ai_db = _load_json(DATA_DIR / "ai_shorts_db.json", [])
analytics = _load_json(DATA_DIR / "analytics_summary.json", {
    "daily_posts": [],
    "platform_views": [],
    "metrics": {
        "retention": 0,
        "shares": 0,
        "follower_conversion": 0,
    },
})

metrics: Dict[str, float] = analytics.get("metrics", {})
col1, col2, col3 = st.columns(3)
col1.metric("Retention @ 75%", f"{metrics.get('retention', 0):.0%}", "Target ≥ 60%")
col2.metric("Shares / 1K Views", f"{metrics.get('shares', 0):.1f}", "Target ≥ 25")
col3.metric("Follower Conversion", f"{metrics.get('follower_conversion', 0):.1%}", "Target ≥ 1.8%")

st.write("---")
left, right = st.columns([2, 1])

with left:
    st.subheader("📰 Pipeline Snapshot")
    shorts = ai_queue.get("shorts", [])
    text_posts = ai_queue.get("text_posts", [])
    st.write(f"**Short videos queued:** {len(shorts)}")
    st.write(f"**Text posts queued:** {len(text_posts)}")
    if shorts:
        df_shorts = pd.DataFrame([
            {
                "Title": item.get("title"),
                "Hooks": len(item.get("hooks", [])),
                "Has Audio": bool(item.get("audio_path")),
            }
            for item in shorts[:5]
        ])
        st.dataframe(df_shorts, use_container_width=True)
    else:
        st.info("Run the automation pipeline to populate fresh AI News Shorts.")

with right:
    st.subheader("🔔 Hot Signals")
    signal_data = analytics.get("signals", [])
    if signal_data:
        for sig in signal_data:
            st.metric(sig.get("label", "Signal"), sig.get("value", "-"), sig.get("delta", ""))
    else:
        st.caption("Signals will appear once analytics are connected.")

st.write("---")

posts_chart_data = analytics.get("daily_posts", [])
if posts_chart_data:
    df_posts = pd.DataFrame(posts_chart_data)
    chart = (
        alt.Chart(df_posts)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(x="date:T", y="posts:Q", color=alt.value("#00b894"))
        .properties(height=280, title="Daily Posts")
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.caption("Daily posts chart will render once analytics_summary.json is populated.")

st.write("\n")
st.info(
    "Use the sidebar to navigate AI News Shorts, Text Posts, Social Publishing, Analytics, Learning, Hook Lab, and Settings."
)

logo_path = ASSETS_DIR / "xseller_logo.svg"
if logo_path.exists():
    st.sidebar.image(str(logo_path), caption="XSELLER.AI", use_column_width=True)

st.sidebar.success("Ready to orchestrate tomorrow's AI coverage.")
