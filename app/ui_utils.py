import streamlit as st

def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
          body, .stApp { background:#0E1117; color:#FAFAFA; }
          [data-testid="stSidebar"] { background:#1B1F2A; }
          .stMetric { background:#171A21; border-radius:14px; padding:1rem; }
          .stButton>button { background:#10F4A0; color:#0B0F14; border:0; border-radius:12px; }
          .stTextInput input, textarea, select { background:#171A21 !important; color:#FAFAFA !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
