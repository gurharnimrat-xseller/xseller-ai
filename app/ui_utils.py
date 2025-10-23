"""UI helpers for consistent styling across Streamlit pages."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = APP_ROOT / "assets"
THEME_PATH = ASSETS_DIR / "dashboard_theme.json"


def load_theme() -> dict:
    if THEME_PATH.exists():
        try:
            return json.loads(THEME_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "primaryColor": "#10F4A0",
        "backgroundColor": "#0E1117",
        "secondaryBackgroundColor": "#262730",
        "textColor": "#FAFAFA",
        "font": "Inter",
    }


def inject_global_styles() -> None:
    theme = load_theme()
    primary = theme.get("primaryColor", "#10F4A0")
    background = theme.get("backgroundColor", "#0E1117")
    surface = theme.get("secondaryBackgroundColor", "#262730")
    text_color = theme.get("textColor", "#FAFAFA")

    css = f"""
    <style>
    html, body, [class*="css"]  {{
        color: {text_color};
        background-color: {background};
    }}
    section.main > div {{
        padding-top: 1.2rem;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {surface} 0%, rgba(255,255,255,0.04) 100%);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 12px 25px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.08);
    }}
    div[data-testid="stMetricLabel"] {{
        color: rgba(250, 250, 250, 0.85);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 2rem;
        color: {primary};
    }}
    div[data-testid="stMetricDelta"] p {{
        font-weight: 600;
    }}
    div.block-container {{
        padding: 2.5rem 3rem 4rem;
    }}
    .xseller-card {{
        background: linear-gradient(145deg, rgba(17,24,31,0.95) 0%, rgba(38,39,48,0.9) 100%);
        border-radius: 22px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 24px 40px -20px rgba(0,0,0,0.45);
    }}
    .xseller-badge {{
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 999px;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(16, 244, 160, 0.16);
        color: {primary};
        border: 1px solid rgba(16, 244, 160, 0.4);
    }}
    div[data-testid="stExpander"] > details {{
        border-radius: 18px;
        background: rgba(13, 17, 23, 0.65);
        border: 1px solid rgba(255,255,255,0.06);
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600;
        color: rgba(250,250,250,0.9);
    }}
    .xseller-borderless table {{
        background-color: transparent !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


__all__ = ["inject_global_styles", "load_theme"]
