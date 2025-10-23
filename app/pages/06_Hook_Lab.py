from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.ui_utils import inject_global_styles

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HOOKS_PATH = DATA_DIR / "hooks_lab.csv"

st.set_page_config(page_title="Hook Lab", page_icon="🧪", layout="wide")
inject_global_styles()
st.title("🧪 Hook Lab")

if not HOOKS_PATH.exists():
    st.info("hooks_lab.csv not found. Populate it with weekly hook experiments.")
    df = pd.DataFrame(
        columns=["date", "story_title", "hook_style", "hook_text", "retention_3s", "ctr", "keep_or_kill"]
    )
else:
    df = pd.read_csv(HOOKS_PATH)

if df.empty:
    st.warning("No hook experiments logged yet.")
else:
    st.dataframe(df, use_container_width=True, height=400)
    top_hooks = df.sort_values(by="retention_3s", ascending=False).head(5)
    st.subheader("Top Retention Hooks")
    for _, row in top_hooks.iterrows():
        st.markdown(f"**{row['hook_style']}** — {row['story_title']}")
        st.write(row["hook_text"])
        st.caption(f"Retention 3s: {row['retention_3s']} • CTR: {row['ctr']}")

    st.download_button(
        "⬇️ Export Hook Lab CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="hook_lab.csv",
    )
