from __future__ import annotations

import streamlit as st

THEMES = {
    "dark": {
        "--bg": "#0E1117",
        "--bg2": "#1B1F2A",
        "--card": "#171A21",
        "--text": "#FAFAFA",
        "--muted": "#A0A6B2",
        "--accent": "#10F4A0",
        "--danger": "#FF5C5C",
        "--warning": "#FFC24A",
        "--grid": "rgba(255,255,255,0.06)",
    },
    "light": {
        "--bg": "#FFFFFF",
        "--bg2": "#F6F7F9",
        "--card": "#FFFFFF",
        "--text": "#0E1117",
        "--muted": "#4B5563",
        "--accent": "#16A34A",
        "--danger": "#DC2626",
        "--warning": "#D97706",
        "--grid": "rgba(0,0,0,0.06)",
    },
}

BASE_CSS = """
<style>
  :root {
    --bg: {--bg};
    --bg2: {--bg2};
    --card: {--card};
    --text: {--text};
    --muted: {--muted};
    --accent: {--accent};
    --danger: {--danger};
    --warning: {--warning};
    --grid: {--grid};
    --radius: 14px;
    --pad: 14px;
  }
  .stApp {
    background: var(--bg);
    color: var(--text);
  }
  section[data-testid="stSidebar"] > div {
    background: var(--bg2);
  }
  .stMetric, .stDataFrame, .stPlotlyChart, .stAltairChart, .stMarkdown, .stButton > button {
    border-radius: var(--radius) !important;
  }
  div[data-testid="stMetricValue"] {
    color: var(--text);
  }
  .stDataFrame thead tr th {
    background: var(--bg2) !important; color: var(--text) !important;
  }
  .stButton > button {
    background: var(--accent) !important; color: #0B0F14 !important; border: 0 !important;
  }
  .stTextInput > div > div > input,
  .stTextArea textarea, .stSelectbox > div > div {
    background: var(--card) !important; color: var(--text) !important; border-radius: var(--radius) !important;
    border: 1px solid var(--grid) !important;
  }
  canvas { background-color: var(--card) !important; }
</style>
"""

def get_theme_from_url(default: str = "dark") -> str:
    qs = st.query_params
    param = qs.get("theme")
    if isinstance(param, list):
        param = param[0] if param else default
    value = (param or default).lower()
    return "light" if value == "light" else "dark"

def apply_theme(theme_name: str) -> None:
    theme = THEMES.get(theme_name, THEMES["dark"])
    st.markdown(BASE_CSS.format(**theme), unsafe_allow_html=True)

def theme_toggle(default: str = "dark") -> str:
    current = get_theme_from_url(default)
    if "theme" not in st.session_state:
        st.session_state["theme"] = current
    options = ["dark", "light"]
    idx = options.index(st.session_state["theme"]) if st.session_state["theme"] in options else 0
    chosen = st.sidebar.selectbox("Theme", options, index=idx)
    if chosen != st.session_state["theme"]:
        st.session_state["theme"] = chosen
        st.query_params.update({"theme": chosen})
    apply_theme(st.session_state["theme"])
    return st.session_state["theme"]


__all__ = ["theme_toggle", "apply_theme", "get_theme_from_url", "THEMES"]
