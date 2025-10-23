from __future__ import annotations
import altair as alt
import pandas as pd
import streamlit as st

from services.analytics_service import load_summary
from services.theme_manager import theme_toggle
from ui_utils import inject_global_styles

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
theme_toggle(default="dark")
inject_global_styles()
st.title("📊 Performance Analytics")

analytics = load_summary()
if not analytics:
    st.info("Analytics summary not found. Populate `app/data/analytics_summary.json` to enable charts.")
    st.stop()
metrics = analytics.get("metrics", {})
col1, col2, col3 = st.columns(3)
col1.metric("Retention @ 75%", f"{metrics.get('retention', 0):.0%}")
col2.metric("Shares / 1K Views", f"{metrics.get('shares', 0):.1f}")
col3.metric("Follower Conversion", f"{metrics.get('follower_conversion', 0):.1%}")

st.write("---")

posts_data = analytics.get("daily_posts", [])
if posts_data:
    df_posts = pd.DataFrame(posts_data)
    chart_posts = (
        alt.Chart(df_posts)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(x="date:T", y="posts:Q", color=alt.value("#0984e3"))
        .properties(height=280, title="Posts per Day")
    )
    st.altair_chart(chart_posts, use_container_width=True)
else:
    st.warning("Daily posts data unavailable.")

platform_views = analytics.get("platform_views", [])
if platform_views:
    df_views = pd.DataFrame(platform_views)
    chart_views = (
        alt.Chart(df_views)
        .mark_area(line={"color": "#00b894"}, color="#00b89430")
        .encode(x="date:T", y="views:Q", color="platform:N")
        .properties(height=320, title="Views by Platform")
    )
    st.altair_chart(chart_views, use_container_width=True)
else:
    st.info("Platform views will appear once analytics capture that feed.")

if comments := analytics.get("feedback", []):
    st.write("---")
    st.subheader("📬 Feedback Inbox")
    for comment in comments:
        st.markdown(f"**{comment.get('author', 'Viewer')}** — {comment.get('timestamp', '')}")
        st.write(comment.get("text", ""))
        st.caption(f"Sentiment: {comment.get('sentiment', 'neutral')}")
else:
    st.caption("Add `feedback` entries inside analytics_summary.json to surface AI learning comments.")

csv = pd.DataFrame(posts_data).to_csv(index=False).encode("utf-8") if posts_data else b""
st.download_button("⬇️ Export daily posts CSV", csv, file_name="analytics_daily_posts.csv", disabled=not csv)
