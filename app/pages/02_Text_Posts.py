from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.services.ai_news_service import load_queue
from app.services.theme_manager import theme_toggle
from app.ui_utils import inject_global_styles

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

st.set_page_config(page_title="Text Posts", page_icon="✍️", layout="wide")
theme_toggle(default="dark")
inject_global_styles()
st.title("✍️ Text + Image Posts")

text_posts = load_queue().get("text_posts", [])
col1, col2 = st.columns([3, 1])
col1.metric("Draft Posts", len(text_posts))
col2.caption("Auto-generated from the top AI stories in the last 24 hours.")

st.write("---")

if not text_posts:
    st.info("No text posts generated yet. Run the pipeline to summarise fresh articles.")
else:
    for post in text_posts:
        with st.expander(post.get("story_title", "AI Update"), expanded=False):
            for platform, payload in post.get("platforms", {}).items():
                st.markdown(f"### {platform}")
                st.write(payload.get("caption", ""))
                image_path = payload.get("image_path")
                if image_path and Path(image_path).exists():
                    st.image(image_path)
                elif prompt := payload.get("image_prompt"):
                    st.caption(f"Prompt: {prompt}")
                st.divider()

    df = pd.DataFrame(
        [
            {
                "Story": post.get("story_title"),
                "Platforms": ", ".join(post.get("platforms", {}).keys()),
            }
            for post in text_posts
        ]
    )
    st.download_button(
        "⬇️ Export summary CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="text_posts_overview.csv",
    )
