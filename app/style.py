# utm_genie_style.py
# CSS global compartido por todas las páginas de UTM Genie

import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Mono:wght@300;400&display=swap');

    /* ── Variables ── */
    :root {
        --bg:        #FAFAFA;
        --surface:   #FFFFFF;
        --border:    #E4E4E7;
        --text:      #1A1A1A;
        --text-sub:  #71717A;
        --accent:    #3D5A80;
        --accent-lt: #EEF2F7;
        --pill-bg:   #EEF2F7;
        --pill-txt:  #3D5A80;
        --danger:    #E11D48;
        --radius:    6px;
        --mono:      'DM Mono', monospace;
        --sans:      'Sora', sans-serif;
    }

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: var(--sans) !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    /* ── Ocultar decoración de Streamlit ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 2.5rem !important;
        max-width: 780px !important;
    }

    /* ── Tipografía ── */
    h1 {
        font-family: var(--sans) !important;
        font-weight: 600 !important;
        font-size: 1.6rem !important;
        letter-spacing: -0.03em !important;
        color: var(--text) !important;
        border-bottom: 1.5px solid var(--border);
        padding-bottom: 0.6rem;
        margin-bottom: 1.5rem !important;
    }
    h2 {
        font-family: var(--sans) !important;
        font-weight: 500 !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--text-sub) !important;
        margin-top: 2rem !important;
        margin-bottom: 0.6rem !important;
    }
    h3 {
        font-family: var(--sans) !important;
        font-weight: 500 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--text-sub) !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.4rem !important;
    }
    p, li, label, .stMarkdown {
        font-size: 0.875rem !important;
        line-height: 1.6 !important;
        color: var(--text) !important;
    }

    /* ── Inputs ── */
    .stTextInput > label,
    .stSelectbox > label,
    .stRadio > label {
        font-size: 0.65rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-sub) !important;
        margin-bottom: 4px !important;
    }
    .stTextInput input,
    .stSelectbox select {
        font-family: var(--sans) !important;
        font-size: 0.875rem !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        padding: 0.45rem 0.75rem !important;
        transition: border-color 0.15s !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(61,90,128,0.08) !important;
    }

    /* ── Botones ── */
    .stButton > button {
        font-family: var(--sans) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        background: transparent !important;
        color: var(--accent) !important;
        border: 1.5px solid var(--accent) !important;
        border-radius: var(--radius) !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: var(--accent) !important;
        color: white !important;
    }
    /* Botón primario */
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        color: white !important;
        border-color: var(--accent) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2e4460 !important;
        border-color: #2e4460 !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        font-family: var(--sans) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        background: transparent !important;
        color: var(--accent) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent) !important;
    }

    /* ── Radio tabs (modo individual/masivo) ── */
    .stRadio > div {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 4px !important;
        display: inline-flex !important;
        gap: 4px !important;
    }
    .stRadio label {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
        padding: 4px 14px !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        text-transform: uppercase !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.75rem 1rem !important;
    }
    [data-testid="metric-container"] label {
        font-size: 0.65rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-sub) !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--accent) !important;
    }

    /* ── Expanders ── */
    .stExpander {
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
    }
    .stExpander summary {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: var(--text-sub) !important;
    }

    /* ── Alerts / info ── */
    .stAlert {
        border-radius: var(--radius) !important;
        border: none !important;
        font-size: 0.8rem !important;
    }
    .stSuccess {
        background: #F0FDF4 !important;
        color: #166534 !important;
    }
    .stInfo {
        background: var(--accent-lt) !important;
        color: var(--accent) !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 0.8rem !important;
        font-family: var(--mono) !important;
    }

    /* ── Code blocks ── */
    .stCode, code {
        font-family: var(--mono) !important;
        font-size: 0.8rem !important;
        background: var(--accent-lt) !important;
        color: var(--accent) !important;
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1.5px solid var(--border) !important;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] a {
        font-size: 0.8rem !important;
        color: var(--text-sub) !important;
    }
    [data-testid="stSidebar"] a:hover {
        color: var(--accent) !important;
    }

    /* ── Captions ── */
    .stCaption, small {
        font-size: 0.7rem !important;
        color: var(--text-sub) !important;
        letter-spacing: 0.02em !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 1.5px solid var(--border) !important;
        margin: 2rem 0 !important;
    }

    /* ── Pastillas de bloques (sort_items) ── */
    .sortable-item {
        font-family: var(--sans) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em !important;
        background: var(--pill-bg) !important;
        color: var(--pill-txt) !important;
        border: 1.5px solid #C5D3E8 !important;
        border-radius: 20px !important;
        padding: 4px 14px !important;
    }

    </style>
    """, unsafe_allow_html=True)
