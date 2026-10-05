import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Precipitation Analyzer",
    page_icon="🌧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ─────────────────────────────────────────────
# SIDEBAR  (runs first so the theme choice is known before CSS is built)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌧 Precipitation Analyzer")
    st.caption("Analyze • Visualize • Understand")
    st.divider()

    st.markdown("#### 📁 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Drop CSV / Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload a file with date and rainfall columns.",
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("#### ⚙️ Settings")

    theme_choice = st.radio(
        "Theme",
        ["🌙 Dark", "☀️ Light"],
        index=0,
        horizontal=True,
        help="Dashboard theme. Dark is default.",
    )
    st.session_state.theme = "dark" if "Dark" in theme_choice else "light"

    baseline_year = st.selectbox(
        "Baseline period (for anomaly)",
        ["None", "2018–2020", "2019–2021", "2020–2022"],
        help="Reference period used to compute precipitation anomalies.",
    )

    st.divider()
    st.markdown("#### 📊 Sections")
    show_stats = st.checkbox("Statistics", value=True)
    show_timeseries = st.checkbox("Time Series", value=True)
    show_cumulative = st.checkbox("Cumulative", value=True)
    show_extremes = st.checkbox("Extremes", value=True)
    show_anomaly = st.checkbox("Anomaly", value=True)

    st.divider()
    st.caption("**by Junaid Ali**")
    st.caption("Civil Engineering Research")

# ─────────────────────────────────────────────
# COLOR PALETTES  (edit colors here)
# ─────────────────────────────────────────────
PALETTES = {
    "dark": {
        "bg": (
            "radial-gradient(circle at 12% 8%, rgba(56,189,248,0.20), transparent 42%),"
            "radial-gradient(circle at 88% 18%, rgba(167,139,250,0.20), transparent 46%),"
            "radial-gradient(circle at 50% 100%, rgba(14,165,233,0.12), transparent 50%),"
            "repeating-linear-gradient(105deg, rgba(148,163,184,0.045) 0 1px, transparent 1px 22px),"
            "linear-gradient(160deg, #070B14 0%, #0B1220 50%, #111A2E 100%)"
        ),
        "sidebar-bg": "linear-gradient(180deg, #0E1730 0%, #0A1020 100%)",
        "card": "rgba(19, 28, 46, 0.75)",
        "card-border": "rgba(56,189,248,0.20)",
        "text": "#E2E8F0",
        "muted": "#94A3B8",
        "subtle": "#64748B",
        "accent": "#38BDF8",
        "accent2": "#A78BFA",
        "glow": "rgba(56,189,248,0.38)",
        "shadow": "rgba(0,0,0,0.45)",
        "input-bg": "rgba(15,23,42,0.85)",
        "popup-bg": "#0B1220",
        "line": "rgba(148,163,184,0.15)",
        "title-grad": "linear-gradient(90deg, #38BDF8, #A78BFA)",
    },
    "light": {
        "bg": (
            "radial-gradient(circle at 10% 0%, rgba(14,165,233,0.20), transparent 45%),"
            "radial-gradient(circle at 90% 10%, rgba(139,92,246,0.15), transparent 45%),"
            "repeating-linear-gradient(105deg, rgba(14,116,144,0.05) 0 1px, transparent 1px 22px),"
            "linear-gradient(160deg, #F0F9FF 0%, #EEF2FF 60%, #F8FAFC 100%)"
        ),
        "sidebar-bg": "linear-gradient(180deg, #E0F2FE 0%, #EDE9FE 100%)",
        "card": "rgba(255, 255, 255, 0.85)",
        "card-border": "rgba(2,132,199,0.25)",
        "text": "#0F172A",
        "muted": "#475569",
        "subtle": "#64748B",
        "accent": "#0284C7",
        "accent2": "#7C3AED",
        "glow": "rgba(2,132,199,0.30)",
        "shadow": "rgba(15,23,42,0.14)",
        "input-bg": "#FFFFFF",
        "popup-bg": "#FFFFFF",
        "line": "rgba(15,23,42,0.10)",
        "title-grad": "linear-gradient(90deg, #0284C7, #7C3AED)",
    },
}

P = PALETTES[st.session_state.theme]
ROOT_VARS = ":root{" + "".join(f"--{k}:{v};" for k, v in P.items()) + "}"

# ─────────────────────────────────────────────
# CUSTOM CSS — Times New Roman + gradient theme + hover pop-ups
# ─────────────────────────────────────────────
STATIC_CSS = """
/* ─── GLOBAL FONT ─── */
html, body, [class*="css"], .stApp, .stMarkdown, .stText,
button, input, select, textarea, label, p, h1, h2, h3, h4, h5, h6 {
    font-family: 'Times New Roman', Times, serif !important;
}

/* ─── BACKGROUND ─── */
.stApp {
    background: var(--bg) !important;
    background-attachment: fixed !important;
    color: var(--text);
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--line);
}

/* ─── GENERIC TEXT COLORS (theme-aware) ─── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stCheckbox label p, .stRadio label p {
    color: var(--text);
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }

/* ─── INPUT WIDGETS ─── */
div[data-baseweb="select"] > div {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--card-border) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] svg { color: var(--text) !important; fill: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] {
    background: var(--input-bg) !important;
    border: 1px dashed var(--accent) !important;
    border-radius: 10px;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] small { color: var(--muted) !important; }
button[kind], .stButton > button {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--card-border) !important;
}

/* ─── HOVER POP-UP EFFECT (everything lifts when the cursor is near) ─── */
[data-testid="stFileUploaderDropzone"],
div[data-baseweb="select"],
[data-testid="stCheckbox"],
[data-testid="stRadio"],
[data-testid="stAlert"],
[data-testid="stDataFrame"],
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
button,
.empty-box, .metric-card, .main-header, .section-title {
    transition: transform 0.25s cubic-bezier(.2,.8,.2,1),
                box-shadow 0.25s ease,
                border-color 0.25s ease,
                background 0.25s ease;
}
[data-testid="stFileUploaderDropzone"]:hover,
div[data-baseweb="select"]:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 24px var(--shadow), 0 0 0 1px var(--accent), 0 0 18px var(--glow);
}
[data-testid="stCheckbox"]:hover,
[data-testid="stRadio"]:hover {
    transform: translateX(6px) scale(1.03);
    filter: drop-shadow(0 4px 10px var(--glow));
}
[data-testid="stSidebar"] h3:hover,
[data-testid="stSidebar"] h4:hover {
    transform: translateX(5px);
    color: var(--accent) !important;
}
button:hover {
    transform: translateY(-3px) scale(1.06);
    box-shadow: 0 10px 22px var(--shadow), 0 0 16px var(--glow);
    border-color: var(--accent) !important;
}
[data-testid="stAlert"]:hover,
[data-testid="stDataFrame"]:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 14px 30px var(--shadow), 0 0 22px var(--glow);
}

/* ─── HEADER ─── */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1.2rem;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    background: var(--card);
    backdrop-filter: blur(8px);
}
.main-header:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 14px 30px var(--shadow), 0 0 24px var(--glow);
}
.main-header .main-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.5px;
    background: var(--title-grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
}
.main-header .main-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    margin: 0;
    font-style: italic;
}
.main-header .author-tag {
    font-size: 0.95rem;
    color: var(--muted);
    font-style: italic;
}

/* ─── METRIC CARDS ─── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-left: 4px solid var(--accent);
    padding: 1rem 1.1rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px var(--shadow);
    position: relative;
    backdrop-filter: blur(8px);
}
.metric-card:hover {
    transform: translateY(-8px) scale(1.05);
    border-left-color: var(--accent2);
    box-shadow: 0 18px 36px var(--shadow), 0 0 28px var(--glow);
    z-index: 50;
}
.metric-card .metric-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.metric-card .metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin-top: 0.25rem;
}

/* ─── CUSTOM HOVER POPUP (ⓘ) ─── */
.info-icon {
    display: inline-block;
    margin-left: 6px;
    color: var(--accent);
    cursor: help;
    font-size: 0.9rem;
    position: relative;
    transition: transform 0.2s ease;
}
.info-icon:hover { transform: scale(1.35); }
.info-icon .popup {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: var(--popup-bg);
    color: var(--text);
    text-align: left;
    text-transform: none;
    letter-spacing: 0;
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 10px 12px;
    position: absolute;
    z-index: 9999;
    bottom: 130%;
    left: 50%;
    margin-left: -140px;
    transform: translateY(8px) scale(0.95);
    transition: opacity 0.2s ease, transform 0.2s ease;
    font-size: 0.85rem;
    line-height: 1.4;
    box-shadow: 0 10px 28px var(--shadow), 0 0 20px var(--glow);
}
.info-icon:hover .popup {
    visibility: visible;
    opacity: 1;
    transform: translateY(0) scale(1);
}
.popup-title {
    font-weight: 700;
    color: var(--accent);
    display: block;
    margin-bottom: 4px;
    font-size: 0.92rem;
}
.popup-formula {
    display: block;
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--line);
    color: var(--accent2);
    font-style: italic;
    font-size: 0.8rem;
}

/* Streamlit's own (?) help tooltips */
[data-testid="stTooltipContent"] {
    background: var(--popup-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 28px var(--shadow), 0 0 20px var(--glow) !important;
}
[data-testid="stTooltipContent"] * { color: var(--text) !important; }

/* ─── SECTION TITLE ─── */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    margin: 1.6rem 0 0.7rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid var(--line);
    letter-spacing: 0.3px;
}
.section-title:hover {
    transform: translateX(8px);
    border-bottom-color: var(--accent);
    color: var(--accent);
}

/* ─── EMPTY STATE BOX ─── */
.empty-box {
    border: 2px dashed var(--accent);
    border-radius: 14px;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--card);
    backdrop-filter: blur(8px);
    margin-top: 1rem;
}
.empty-box:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 40px var(--shadow), 0 0 34px var(--glow);
    border-color: var(--accent2);
}
.empty-box h3 { color: var(--text); margin: 0; }
.empty-box p { color: var(--muted); margin-top: 0.5rem; }
.empty-box small { color: var(--subtle); font-size: 0.85rem; }

/* ─── FOOTER ─── */
.footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    text-align: center;
    font-size: 0.85rem;
    color: var(--subtle);
    font-style: italic;
}
"""

st.markdown(f"<style>{ROOT_VARS}{STATIC_CSS}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div>
        <p class="main-title">🌧 Precipitation Analyzer</p>
        <p class="main-subtitle">Analyze • Visualize • Understand</p>
    </div>
    <div class="author-tag">by Junaid Ali</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ─────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div class="empty-box">
        <h3>📁 Drop CSV / Excel file here</h3>
        <p>or use the sidebar to browse</p>
        <small>Supported: .csv, .xlsx, .xls</small>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<p class="section-title">ℹ️ What happens next?</p>', unsafe_allow_html=True)
    st.markdown("""
    - Automatic column detection (date + rainfall)
    - Data quality check
    - Full statistical analysis + charts
    - Downloadable professional PDF report
    """)

    st.markdown("""
    <div class="footer">
        Developed by Junaid Ali · Civil Engineering Research
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"❌ Could not read file: {e}")
    st.stop()

st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")

st.write("")
st.markdown('<p class="section-title">👀 Data Preview</p>', unsafe_allow_html=True)
st.dataframe(df.head(10), use_container_width=True)

# ─────────────────────────────────────────────
# DATA SUMMARY (with custom hover popups)
# ─────────────────────────────────────────────
st.write("")
st.markdown('<p class="section-title">📊 Data Summary</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">
            Records
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Records</span>
                    Total number of rows in the uploaded dataset.
                </span>
            </span>
        </div>
        <div class="metric-value">{len(df):,}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">
            Columns
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Columns</span>
                    Number of variables detected in the file.
                </span>
            </span>
        </div>
        <div class="metric-value">{len(df.columns)}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">
            Status
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Status</span>
                    Current state of the loaded dataset.
                </span>
            </span>
        </div>
        <div class="metric-value">Loaded</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">
            Engine
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Analysis Engine</span>
                    Core version of the precipitation analyzer.
                </span>
            </span>
        </div>
        <div class="metric-value">V1</div>
    </div>
    """, unsafe_allow_html=True)

st.info("🔧 **Step 1 complete.** Next: auto-detect date & rainfall columns, then full statistics, charts, and PDF report.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Developed by Junaid Ali · Civil Engineering Research
</div>
""", unsafe_allow_html=True)
