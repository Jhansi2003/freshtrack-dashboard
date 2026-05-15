import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import warnings
from datetime import datetime

# =========================================================
# CONFIG & SETTINGS
# =========================================================
warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="FreshTrack AI | Tactical Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# BRANDING & THEME (PROFESSIONAL DARK)
# =========================================================
PRIMARY_COLOR = "#3b82f6"
BG_COLOR = "#050505"
CARD_BG = "#111111"
BORDER_COLOR = "#262626"
TEXT_COLOR = "#e5e7eb"

# High-end "Sophisticated Dark" CSS Injection
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Main Background */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #0f0f0f;
        border-right: 1px solid {BORDER_COLOR};
    }}
    [data-testid="stSidebarNav"] {{
        padding-top: 2rem;
    }}
    
    /* Metrics / KPI Cards */
    [data-testid="stMetric"] {{
        background-color: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 16px;
        padding: 24px !important;
        transition: all 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{
        border-color: {PRIMARY_COLOR}66;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px -10px rgba(59, 130, 246, 0.2);
    }}
    [data-testid="stMetricLabel"] p {{
        color: #666;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.15em;
        font-size: 0.7rem;
    }}
    [data-testid="stMetricValue"] div {{
        font-weight: 300;
        color: white;
        font-size: 2rem;
    }}

    /* Typography */
    .main-header {{
        font-size: 2.8rem;
        font-weight: 300;
        letter-spacing: -0.03em;
        color: white;
        margin-bottom: 0.2rem;
    }}
    .sub-head {{
        color: #666;
        font-size: 1rem;
        margin-bottom: 2.5rem;
    }}
    
    /* Section Cards */
    .glass-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
    }}
    
    /* Button Redesign */
    .stButton > button {{
        width: 100%;
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.8rem;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }}
    .stButton > button:hover {{
        background-color: #2563eb;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
        transform: scale(1.01);
    }}

    /* Recommendation Refined Cards */
    .rec-card {{
        padding: 24px;
        border-radius: 20px;
        height: 100%;
        border: 1px solid {BORDER_COLOR};
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}
    .rec-tag {{
        font-weight: 800;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 4px 8px;
        border-radius: 6px;
        width: fit-content;
    }}
    .rec-rose {{ background: rgba(244, 63, 94, 0.05); border-left: 5px solid #f43f5e; }}
    .rec-blue {{ background: rgba(59, 130, 246, 0.05); border-left: 5px solid #3b82f6; }}
    .rec-amber {{ background: rgba(245, 158, 11, 0.05); border-left: 4px solid #f59e0b; }}
    .rec-emerald {{ background: rgba(16, 185, 129, 0.05); border-left: 5px solid #10b981; }}
</style>
