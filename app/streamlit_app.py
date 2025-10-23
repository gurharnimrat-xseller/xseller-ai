from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.services.ai_news_service import load_queue
from app.services.analytics_service import load_summary
from app.services.theme_manager import theme_toggle
from app.ui_utils import inject_global_styles, load_theme

st.set_page_config(page_title="XSELLER.AI Ops Console", page_icon="🤖", layout="wide")
inject_global_styles()

active_theme = theme_toggle(default="dark")
theme = load_theme()
PRIMARY = theme.get("primaryColor", "#10F4A0")

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
HOOKS_PATH = DATA_DIR / "hooks_lab.csv"

analytics = load_summary()
queue_state = load_queue()
shorts = queue_state.get("shorts", [])
text_posts = queue_state.get("text_posts", [])
metrics = analytics.get("metrics", {})

def _metric_value(name: str, default: float = 0.0) -> float:
    return float(metrics.get(name, default))

retention = _metric_value("retention")
retention_delta = _metric_value("retention_delta")
shares = _metric_value("shares")
shares_delta = _metric_value("shares_delta")
follower_conv = _metric_value("follower_conversion")
follower_delta = _metric_value("follower_conversion_delta")

csv_export = pd.DataFrame({
    "metric": ["retention", "shares_per_1k", "follower_conversion"],
    "value": [retention, shares, follower_conv],
    "delta": [retention_delta, shares_delta, follower_delta],
}).to_csv(index=False).encode("utf-8")
pdf_placeholder = BytesIO()
pdf_placeholder.write(b"XSELLER.AI Dashboard Summary\n\nMetrics exported from Streamlit UI.")
pdf_placeholder.seek(0)

header_cols = st.columns([5, 0.8, 0.8])
with header_cols[0]:
    st.title("🤖 XSELLER.AI Ops Console")
with header_cols[1]:
    st.download_button("⬇️ CSV", csv_export, file_name="xseller_metrics.csv", help="Export metrics as CSV")
with header_cols[2]:
    st.download_button("📄 PDF", pdf_placeholder, file_name="xseller_summary.pdf", mime="application/pdf", help="Download snapshot PDF (placeholder)")

col1, col2, col3 = st.columns(3)
col1.metric("Retention @ 75%", f"{retention:.0%}", f"{retention_delta:+.1f}%")
col2.metric("Shares / 1K views", f"{shares:.1f}", f"{shares_delta:+.1f}")
col3.metric("Follower conversion", f"{follower_conv:.1%}", f"{follower_delta:+.2f}%")

st.write("---")

snapshot_left, snapshot_right = st.columns([2, 1])
with snapshot_left:
    st.subheader("📰 Pipeline Snapshot")
    st.markdown(
        f"<div class='xseller-card'><span class='xseller-badge'>Queue</span>\n        <h3>{len(shorts)} Short Videos</h3>\n        <p>{len(text_posts)} text posts waiting for approval.</p></div>",
        unsafe_allow_html=True,
    )
    if shorts:
        df_shorts = pd.DataFrame(
            [
                {
                    "Title": item.get("title"),
                    "Hooks": len(item.get("hooks", [])),
                    "Audio": "Yes" if item.get("audio_path") else "No",
                }
                for item in shorts[:6]
            ]
        )
        st.dataframe(df_shorts, use_container_width=True)
    else:
        st.info("Run the automation pipeline to populate fresh AI News Shorts.")

with snapshot_right:
    st.subheader("🔥 Hot Signals")
    for signal in analytics.get("signals", []):
        label = signal.get("label", "Signal")
        value = signal.get("value", "-")
        delta = signal.get("delta", "")
        st.metric(label, value, delta)
    if not analytics.get("signals"):
        st.caption("Signals will appear once analytics capture live campaign data.")

st.write("---")

posts_data = analytics.get("daily_posts", [])
if posts_data:
    df_posts = pd.DataFrame(posts_data)
    post_chart = (
        alt.Chart(df_posts)
        .mark_line(point=True, strokeWidth=2, color=PRIMARY)
        .encode(x="date:T", y="posts:Q", tooltip=["date:T", "posts:Q"])
        .properties(title="Daily Posts Trend", height=300)
    )
    st.altair_chart(post_chart, use_container_width=True)
else:
    st.info("Daily posts trend will render once analytics_summary.json contains 'daily_posts'.")

hook_chart_col, platform_chart_col = st.columns(2)

hooks_df = pd.read_csv(HOOKS_PATH) if HOOKS_PATH.exists() else pd.DataFrame()
if not hooks_df.empty:
    hook_chart = (
        alt.Chart(hooks_df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("hook_style:N", title="Hook Style"),
            y=alt.Y("mean(retention_3s):Q", title="Avg Retention 3s"),
            color=alt.value(PRIMARY),
            tooltip=["hook_style", "mean(retention_3s)", "mean(ctr)"]
        )
        .properties(title="Hook Style vs Retention", height=300)
    )
    hook_chart_col.altair_chart(hook_chart, use_container_width=True)
else:
    hook_chart_col.caption("Hook Lab data not available yet.")

platform_views = analytics.get("platform_views", [])
if platform_views:
    df_views = pd.DataFrame(platform_views)
    platform_chart = (
        alt.Chart(df_views)
        .mark_area(opacity=0.7)
        .encode(
            x="date:T",
            y="views:Q",
            color="platform:N",
            tooltip=["date:T", "platform:N", "views:Q"],
        )
        .properties(title="Views by Platform (30 days)", height=300)
    )
    platform_chart_col.altair_chart(platform_chart, use_container_width=True)
else:
    platform_chart_col.caption("Views by platform will appear once analytics captures the feed.")

st.write("---")
st.info("Use the sidebar to manage Shorts, Text Posts, Social Publishing, Analytics, Learning, Hook Lab, and Settings.")

logo_path = APP_ROOT / "assets" / "xseller_logo.svg"
if logo_path.exists():
    st.sidebar.image(str(logo_path), caption="XSELLER.AI", use_column_width=True)

st.sidebar.success("Ready to orchestrate tomorrow's AI coverage.")
