"""
CSS and styling utilities for the Streamlit dashboard.
"""

DARK_CSS = """
<style>
/* ---- Global ---- */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Main background */
.stApp {
    background-color: #0d1117;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] .stMarkdown {
    color: #e6edf3;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1c2128 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(110, 64, 201, 0.2);
}
[data-testid="metric-container"] label {
    color: #8b949e !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e6edf3 !important;
    font-size: 1.8rem;
    font-weight: 700;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid #30363d;
    border-radius: 8px;
    overflow: hidden;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #161b22;
    border-bottom: 2px solid #30363d;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #8b949e;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background-color: #6e40c9 !important;
    color: #ffffff !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6e40c9 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: opacity 0.15s ease;
}
.stButton > button:hover {
    opacity: 0.85;
}

/* Selectbox / multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: #1c2128;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #e6edf3;
}

/* Slider */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: #6e40c9;
}

/* Section header */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #6e40c9;
    display: inline-block;
}

/* Stat card */
.stat-card {
    background: linear-gradient(135deg, #1c2128 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 10px;
    text-align: center;
}
.stat-card .value {
    font-size: 2rem;
    font-weight: 800;
    color: #6e40c9;
}
.stat-card .label {
    font-size: 0.78rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-fw { background: rgba(239,68,68,0.2); color: #f87171; }
.badge-mf { background: rgba(59,130,246,0.2); color: #60a5fa; }
.badge-df { background: rgba(34,197,94,0.2); color: #4ade80; }
.badge-gk { background: rgba(234,179,8,0.2); color: #facc15; }

/* Info box */
.info-box {
    background: rgba(110, 64, 201, 0.1);
    border: 1px solid rgba(110, 64, 201, 0.35);
    border-radius: 10px;
    padding: 14px 18px;
    color: #c9b8ef;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* Divider */
.pl-divider {
    border: none;
    border-top: 1px solid #30363d;
    margin: 1.2rem 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #161b22; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6e40c9; }
</style>
"""


LOGO_HTML = """
<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
  <div style="background:linear-gradient(135deg,#6e40c9,#8b5cf6);
              border-radius:10px;width:42px;height:42px;display:flex;
              align-items:center;justify-content:center;font-size:1.4rem;">
    ⚽
  </div>
  <div>
    <div style="font-size:1.1rem;font-weight:800;color:#e6edf3;line-height:1.1;">
      PL Analytics
    </div>
    <div style="font-size:0.7rem;color:#8b949e;letter-spacing:0.05em;">
      PREMIER LEAGUE · 2014–2024
    </div>
  </div>
</div>
"""


def inject_css():
    import streamlit as st
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def render_logo():
    import streamlit as st
    st.sidebar.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border-color:#30363d;margin:8px 0 16px;'>",
                        unsafe_allow_html=True)


def section_header(title: str) -> str:
    return f'<div class="section-header">{title}</div>'


def stat_card_html(value, label: str) -> str:
    return f"""
    <div class="stat-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>"""


def position_badge(pos: str) -> str:
    cls = {"FW": "badge-fw", "MF": "badge-mf", "DF": "badge-df", "GK": "badge-gk"}
    full = {"FW": "FWD", "MF": "MID", "DF": "DEF", "GK": "GK"}
    return f'<span class="badge {cls.get(pos,"")}"> {full.get(pos, pos)} </span>'
