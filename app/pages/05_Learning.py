from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from app.ui_utils import inject_global_styles

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LEARNING_PATH = DATA_DIR / "learning_log.json"

st.set_page_config(page_title="Learning", page_icon="🧠", layout="wide")
inject_global_styles()
st.title("🧠 AI Learning Loop")

if LEARNING_PATH.exists():
    entries = json.loads(LEARNING_PATH.read_text(encoding="utf-8"))
else:
    entries = []
    LEARNING_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Recent Experiments")
    if not entries:
        st.info("No learning logs yet. Use the form to capture insights from campaigns.")
    else:
        for entry in entries[::-1]:
            st.markdown(f"### {entry.get('title', 'Untitled Insight')}")
            st.write(entry.get("summary", ""))
            st.caption(f"Hook: {entry.get('hook_style','n/a')} • Outcome: {entry.get('result','n/a')}")
            st.divider()

with col2:
    st.subheader("Add Learning")
    title = st.text_input("Experiment title")
    hook_style = st.selectbox("Hook style", ["Shock", "Impact", "Celebrity", "Data", "Other"])
    result = st.selectbox("Outcome", ["Win", "Neutral", "Miss"])
    summary = st.text_area("Summary")
    if st.button("Save Insight") and title and summary:
        entries.append(
            {
                "title": title,
                "hook_style": hook_style,
                "result": result,
                "summary": summary,
            }
        )
        LEARNING_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        st.success("Learning logged.")
        st.experimental_rerun()

st.caption("Learning entries sync with Hook Lab recommendations on the next pipeline run.")
