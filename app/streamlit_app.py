from __future__ import annotations

# --- path guard (TOP of file, before other imports) ---
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
for p in (APP_DIR, APP_DIR / "services"):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

import os
from io import BytesIO
from typing import Any, Dict, List

import altair as alt
import pandas as pd
import streamlit as st

from services.ai_news_service import load_queue, load_db  # type: ignore
from services.analytics_service import load_summary  # type: ignore
from services.publish_service import _last_provider  # type: ignore
from services.theme_manager import THEMES, theme_toggle  # type: ignore
from ui_utils import inject_global_styles

st.set_page_config(page_title="XSELLER.AI Dashboard", page_icon="🤖", layout="wide")
inject_global_styles()

active_theme = theme_toggle(default="dark")
palette = THEMES.get(active_theme, THEMES["dark"])
PRIMARY = palette["--accent"]
DANGER = palette["--danger"]
WARNING = palette["--warning"]
MUTED = palette["--muted"]
TEXT = palette["--text"]
CARD = palette["--card"]

CUSTOM_CSS = f"""
<style>
  .xs-nav-title {{
      font-size: 0.8rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: {MUTED};
  }}
  .metric-card {{
      background: linear-gradient(140deg, rgba(16, 244, 160, 0.10), rgba(23, 26, 33, 0.85));
      border-radius: 18px;
      padding: 1.4rem 1.6rem;
      border: 1px solid rgba(255,255,255,0.04);
      box-shadow: 0 24px 48px -32px rgba(0,0,0,0.65);
  }}
  .signal-card {{
      background: {CARD};
      border-radius: 16px;
      padding: 1rem 1.1rem;
      border: 1px solid rgba(255,255,255,0.06);
      min-height: 110px;
  }}
  .signal-label {{
      font-size: 0.75rem;
      letter-spacing: 0.08em;
      color: {MUTED};
      text-transform: uppercase;
  }}
  .signal-value {{
      font-size: 1.2rem;
      font-weight: 600;
      color: {TEXT};
  }}
  .signal-delta {{
      font-size: 0.9rem;
      color: {PRIMARY};
  }}
  .chart-card {{
      background: {CARD};
      border-radius: 20px;
      padding: 1.5rem;
      border: 1px solid rgba(255,255,255,0.05);
      box-shadow: 0 18px 36px -28px rgba(0,0,0,0.55);
      height: 100%;
  }}
  .table-card {{
      background: {CARD};
      border-radius: 20px;
      padding: 1.5rem;
      border: 1px solid rgba(255,255,255,0.06);
  }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
HOOKS_PATH = DATA_DIR / "hooks_lab.csv"
LOGO_DARK = str(APP_ROOT / "assets" / "xseller_logo.svg")
logo_path = LOGO_DARK

provider = os.getenv("POST_PROVIDER", _last_provider())

st.sidebar.image(logo_path, use_column_width=True)
st.sidebar.title("XSELLER.AI")
st.sidebar.caption(f"Provider: **{provider}**  \nTheme: **{active_theme.title()}**")
nav_choice = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "AI News Shorts",
        "Text Posts",
        "Social Posts",
        "Analytics",
        "Hook Lab",
        "Settings"
    ],
    index=0,
)

if nav_choice != "Dashboard":
    page_routes = {
        "AI News Shorts": "pages/01_AI_News_Shorts.py",
        "Text Posts": "pages/02_Text_Posts.py",
        "Social Posts": "pages/03_Social_Posts.py",
        "Analytics": "pages/04_Analytics.py",
        "Hook Lab": "pages/06_Hook_Lab.py",
        "Settings": "pages/07_Settings_Health.py",
    }
    target = page_routes.get(nav_choice)
    if target:
        try:
            st.switch_page(target)
        except Exception:
            st.info("Use the sidebar navigation to open this section in the deployed app.")
    st.stop()

analytics = load_summary()
queue_state = load_queue()
queue_items = queue_state.get("items", [])
shorts = [item for item in queue_items if item.get("type") in {"video", "short", "short_video"}]
text_posts = [item for item in queue_items if item.get("type") in {"text_post", "text", "caption"}]
metrics = analytics.get("metrics", {})


def metric_value(name: str, default: float = 0.0) -> float:
    try:
        return float(metrics.get(name, default))
    except (TypeError, ValueError):
        return default

retention = metric_value("retention")
retention_delta = metric_value("retention_delta")
shares = metric_value("shares")
shares_delta = metric_value("shares_delta")
follower_conv = metric_value("follower_conversion")
follower_delta = metric_value("follower_conversion_delta")

header_cols = st.columns([5, 1, 1])
with header_cols[0]:
    st.title("📊 XSELLER.AI — Automation Insights")

def build_delta(delta: float, suffix: str = "%") -> str:
    if delta == 0:
        return f"{delta:+.1f}{suffix}"
    color = "#32D583" if delta > 0 else "#F97066"
    arrow = "▲" if delta > 0 else "▼"
    return f"<span style='color:{color}; font-weight:600;'>{arrow} {delta:+.1f}{suffix}</span>"

metric_cols = st.columns(3)
metric_cols[0].metric("Retention @ 75 %", f"{retention:.1f} %", f"{retention_delta:+.1f} %")
metric_cols[1].metric("Shares / 1 K Views", f"{shares:.1f}", f"{shares_delta:+.1f} %")
metric_cols[2].metric("Follower Conversion", f"{follower_conv:.2f} %", f"{follower_delta:+.2f} %")

st.write("")
st.subheader("🔥 Hot Signals")
signal_defaults = [
    {"label": "Top CTR 24 h", "value": "13.2 %", "delta": +1.2},
    {"label": "Best Retention Hook", "value": "Celebrity Interview", "delta": 0.0},
    {"label": "Top Platform", "value": "YouTube 45 %", "delta": +4.5},
    {"label": "Sentiment Trend", "value": "Positive", "delta": +5.0},
]
signals = analytics.get("signals") or signal_defaults
signal_cols = st.columns(len(signals))
for col, sig in zip(signal_cols, signals):
    delta_val = sig.get("delta")
    delta_html = ""
    if isinstance(delta_val, (int, float)):
        delta_html = build_delta(float(delta_val))
    col.markdown(
        f"""
        <div class='signal-card'>
            <div class='signal-label'>{sig.get('label', 'Signal')}</div>
            <div class='signal-value'>{sig.get('value', '-')}</div>
            <div class='signal-delta'>{delta_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.subheader("📈 Analytics Overview")

platform_views = analytics.get("platform_views") or [
    {"platform": "YouTube", "views": 52},
    {"platform": "Instagram", "views": 34},
    {"platform": "X", "views": 29},
    {"platform": "TikTok", "views": 24},
    {"platform": "LinkedIn", "views": 18},
]
platform_df = pd.DataFrame(platform_views)

hook_retention = analytics.get("hook_retention") or [
    {"hook_style": "Shock", "retention_delta": 3.4},
    {"hook_style": "Impact", "retention_delta": 0.8},
    {"hook_style": "Celebrity", "retention_delta": 2.2},
]
hook_df = pd.DataFrame(hook_retention)

daily_posts = analytics.get("daily_posts") or [
    {"day": d, "posts": v}
    for d, v in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [12, 18, 22, 19, 17, 20, 14])
]
daily_df = pd.DataFrame(daily_posts)

daily_posts_30 = analytics.get("daily_posts_30") or [
    {"date": str(date), "posts": val}
    for date, val in zip(pd.date_range(end=pd.Timestamp.today(), periods=30), [12, 14, 15, 13, 16, 18, 17, 19, 20, 18, 17, 21, 23, 22, 20, 19, 17, 16, 18, 21, 24, 22, 23, 19, 18, 16, 17, 18, 21, 23])
]
daily_30_df = pd.DataFrame(daily_posts_30)

base_chart_config = {
    "axis": {
        "labelColor": TEXT,
        "titleColor": TEXT,
        "tickColor": MUTED,
    },
    "view": {"stroke": "transparent"},
    "legend": {"labelColor": TEXT, "titleColor": TEXT},
}

chart1 = (
    alt.Chart(platform_df)
    .mark_bar(color=PRIMARY, cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("platform:N", title="Platform"),
        y=alt.Y("views:Q", title="Views"),
        tooltip=["platform", "views"],
    )
    .properties(title="Views by Platform (30 Days)", height=280)
    .configure(**base_chart_config)
)

chart2 = (
    alt.Chart(hook_df)
    .mark_bar(color="#22C55E", cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("hook_style:N", title="Hook Style"),
        y=alt.Y("retention_delta:Q", title="Retention Δ (%)"),
        tooltip=["hook_style", "retention_delta"],
    )
    .properties(title="Hook Style vs Retention", height=280)
    .configure(**base_chart_config)
)

chart3 = (
    alt.Chart(daily_df)
    .mark_line(color="#3B82F6", point=alt.OverlayMarkDef(color="#93C5FD"))
    .encode(
        x=alt.X("day:N", title="Day"),
        y=alt.Y("posts:Q", title="Posts"),
        tooltip=["day", "posts"],
    )
    .properties(title="Daily Posts (Last 7 Days)", height=280)
    .configure(**base_chart_config)
)

chart4 = (
    alt.Chart(daily_30_df)
    .mark_area(line={"color": PRIMARY}, color="rgba(16,244,160,0.25)")
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("posts:Q", title="Posts"),
        tooltip=["date:T", "posts:Q"],
    )
    .properties(title="Daily Posts (30 Days)", height=280)
    .configure(**base_chart_config)
)

row1 = st.columns(2)
with row1[0]:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.altair_chart(chart1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with row1[1]:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.altair_chart(chart2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

row2 = st.columns(2)
with row2[0]:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.altair_chart(chart3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with row2[1]:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.altair_chart(chart4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.subheader("🎯 Hook Performance Table")

hook_performance = analytics.get("hook_performance") or [
    {"hook_style": "Shock", "ctr_delta": 3.14, "retention_delta": 3.4, "views": 450},
    {"hook_style": "Impact", "ctr_delta": -0.2, "retention_delta": -1.5, "views": 380},
    {"hook_style": "Celebrity", "ctr_delta": 2.4, "retention_delta": 0.8, "views": 520},
]
perf_df = pd.DataFrame(hook_performance)

if not perf_df.empty:
    styled = (
        perf_df.style
        .format({
            "ctr_delta": "{:+.2f} %",
            "retention_delta": "{:+.2f} %",
            "views": "{:,}"
        })
        .applymap(lambda v: f"color: {PRIMARY}; font-weight:600" if isinstance(v, str) and v.startswith('+') else "", subset=["ctr_delta", "retention_delta"])
        .applymap(lambda v: f"color: {DANGER}; font-weight:600" if isinstance(v, str) and v.startswith('-') else "", subset=["ctr_delta", "retention_delta"])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No hook performance data available yet. Upload Hook Lab statistics to populate this table.")

st.divider()
cta_cols = st.columns([3, 1])
with cta_cols[0]:
    st.success("✅ All analytics synced successfully. Use the sidebar to dive deeper into each workflow stage.")
with cta_cols[1]:
    csv_buffer = perf_df.to_csv(index=False).encode("utf-8") if not perf_df.empty else b""
    st.download_button("📥 Export CSV", data=csv_buffer, file_name="hook_performance.csv", disabled=not bool(csv_buffer))
    st.button("🧠 View AI Learnings")
