from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from app.services.healthcheck import run_all
from app.ui_utils import inject_global_styles

LOGS_PATH = Path("logs/health_last.json")

st.set_page_config(page_title="Settings & Health", page_icon="⚙️", layout="wide")
inject_global_styles()
st.title("⚙️ Settings & Health")

with st.expander("Environment Keys", expanded=False):
    st.write("The dashboard expects the following environment variables:")
    st.code(
        """
POST_PROVIDER
GETLATE_API_KEY / GETLATE_BASE_URL
BUFFER_ACCESS_TOKEN / BUFFER_PROFILE_ID / BUFFER_BASE_URL
PUBLER_API_KEY / PUBLER_WORKSPACE_ID / PUBLER_BASE_URL
OPENAI_API_KEY / ELEVENLABS_API_KEY
"""
    )
    st.caption("Missing keys will trigger warnings in the Social Posts and learning flows.")

st.write("---")

if st.button("Run healthcheck"):
    results = run_all()
    st.session_state["health_results"] = results
else:
    if LOGS_PATH.exists():
        results = json.loads(LOGS_PATH.read_text(encoding="utf-8"))
        st.session_state["health_results"] = results

results = st.session_state.get("health_results")
if not results:
    st.info("Run the healthcheck to see provider status.")
else:
    cols = st.columns(len(results.get("checks", [])) or 1)
    for col, check in zip(cols, results.get("checks", [])):
        status = "✅" if check["ok"] else "⚠️"
        col.metric(check["name"], status, check.get("detail", ""))

    st.json(results)
