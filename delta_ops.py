"""
DELTA OPS DASHBOARD
4 Tabs: Dashboard | Operational Issues | Circular Implementation | Task Reminders
Ops data stored in:      DELTA_OPS_data.csv
Circular data stored in: DELTA_OPS_circular_data.csv
Task data stored in:     DELTA_OPS_task_data.csv
"""

import os
import io
import html as _html
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DELTA OPS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Design System ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

:root {
    --bg:           #05070f;
    --bg2:          #0c1020;
    --bg3:          #121828;
    --border:       #1e2d4a;
    --border-hi:    #2a4070;
    --text:         #c8d8f0;
    --muted:        #4a6080;
    --accent:       #00c2ff;
    --accent2:      #0066cc;
    --hi:           #ff4466;
    --med:          #ffaa00;
    --lo:           #00dd88;
    --open:         #ff4466;
    --inprog:       #ffaa00;
    --closed:       #00dd88;
    --circular:     #aa66ff;
}

* { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--text);
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Top header ── */
.ops-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px 14px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(90deg, var(--bg2) 0%, var(--bg) 100%);
}
.ops-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--accent);
}
.ops-logo span { color: var(--text); }
.ops-timestamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 24px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    color: var(--muted) !important;
    padding: 14px 28px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: var(--bg) !important;
    padding: 0 !important;
}

/* ── Section wrapper ── */
.tab-body { padding: 28px 32px; }

/* ── Metric cards ── */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.metric-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-line, var(--accent));
}
.metric-card.hi::before  { background: var(--hi); }
.metric-card.med::before { background: var(--med); }
.metric-card.lo::before  { background: var(--lo); }
.metric-card.circ::before { background: var(--circular); }
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.14em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 34px;
    font-weight: 700;
    line-height: 1;
}
.metric-card.hi  .metric-value { color: var(--hi); }
.metric-card.med .metric-value { color: var(--med); }
.metric-card.lo  .metric-value { color: var(--lo); }
.metric-card.circ .metric-value { color: var(--circular); }
.metric-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 6px;
}

/* ── Section title ── */
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    color: var(--muted);
    text-transform: uppercase;
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Status pills ── */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.pill-open       { background: rgba(255,68,102,0.15); color: var(--open);   border: 1px solid rgba(255,68,102,0.3); }
.pill-inprogress { background: rgba(255,170,0,0.15);  color: var(--inprog); border: 1px solid rgba(255,170,0,0.3); }
.pill-closed     { background: rgba(0,221,136,0.15);  color: var(--closed); border: 1px solid rgba(0,221,136,0.3); }
.pill-high       { background: rgba(255,68,102,0.15); color: var(--hi);   border: 1px solid rgba(255,68,102,0.3); }
.pill-medium     { background: rgba(255,170,0,0.15);  color: var(--med); border: 1px solid rgba(255,170,0,0.3); }
.pill-low        { background: rgba(0,221,136,0.15);  color: var(--lo); border: 1px solid rgba(0,221,136,0.3); }
.pill-circular   { background: rgba(170,102,255,0.15); color: var(--circular); border: 1px solid rgba(170,102,255,0.3); }

/* ── Issue table ── */
.issue-table { width: 100%; border-collapse: collapse; }
.issue-table th {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--bg2);
}
.issue-table td {
    font-size: 12px;
    padding: 11px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    vertical-align: middle;
}
.issue-table tr:hover td { background: var(--bg2); }
.issue-table td.team-cell {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
}

/* ── Form ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
}
.stButton > button {
    background: var(--accent2) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover { background: var(--accent) !important; color: var(--bg) !important; }

/* ── Alert bar ── */
.alert-bar {
    padding: 10px 16px;
    border-radius: 4px;
    font-size: 12px;
    margin-bottom: 16px;
    border-left: 3px solid;
}
.alert-hi   { background: rgba(255,68,102,0.08);  border-color: var(--hi);  color: var(--hi); }
.alert-info { background: rgba(0,194,255,0.08);   border-color: var(--accent); color: var(--accent); }
.alert-success { background: rgba(0,221,136,0.08); border-color: var(--lo); color: var(--lo); }

/* ── Circular card ── */
.circ-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--circular);
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.15s;
}
.circ-card:hover { border-color: var(--border-hi); }
.circ-card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 8px;
    line-height: 1.5;
}
.circ-card-meta {
    font-size: 12px;
    color: var(--text);
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    align-items: center;
}
.card-team {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.06em;
}
.card-meta-item {
    font-size: 12px;
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
}
.circ-badge {
    display: inline-block;
    background: rgba(170,102,255,0.15);
    color: var(--circular);
    border: 1px solid rgba(170,102,255,0.3);
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 2px 8px;
    text-transform: uppercase;
}

/* ── Charts ── */
.chart-wrapper {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
}

/* ── Streamlit overrides ── */
label, .stLabel { color: var(--text) !important; font-size: 12px !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 0.08em !important; }
div[data-testid="stWidgetLabel"] p { color: var(--text) !important; font-size: 12px !important; font-family: 'IBM Plex Mono', monospace !important; }
.stSelectbox label, .stMultiSelect label, .stTextArea label, .stTextInput label, .stDateInput label, .stRadio label { color: var(--text) !important; font-size: 12px !important; }
.stMarkdown p { color: var(--text) !important; }
.stSuccess { background: rgba(0,221,136,0.08) !important; border: 1px solid rgba(0,221,136,0.3) !important; color: var(--lo) !important; }
.stError   { background: rgba(255,68,102,0.08) !important; border: 1px solid rgba(255,68,102,0.3) !important; }
div[data-testid="stDataFrame"] { background: var(--bg2) !important; }
div[data-testid="stExpander"] summary { color: var(--text) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }
div[data-testid="stExpander"] { border-color: var(--border) !important; background: var(--bg2) !important; }
.stMultiSelect [data-baseweb="tag"] { background: rgba(0,194,255,0.15) !important; color: var(--accent) !important; }
.stMultiSelect [data-baseweb="select"] span { color: var(--text) !important; }
p, span, div { color: var(--text); }

/* ── Bulk upload panel ── */
.bulk-panel {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    border-radius: 6px;
    padding: 18px 20px;
    margin-top: 24px;
}
.bulk-panel-circ {
    border-top-color: var(--circular);
}
.bulk-step {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.18em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.bulk-step b { color: var(--accent); }
.bulk-step-circ b { color: var(--circular); }
.col-pill {
    display: inline-block;
    background: rgba(0,194,255,0.08);
    border: 1px solid rgba(0,194,255,0.2);
    border-radius: 3px;
    padding: 1px 7px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    margin: 2px 2px 2px 0;
}
.col-pill-circ {
    background: rgba(170,102,255,0.08);
    border-color: rgba(170,102,255,0.2);
    color: var(--circular);
}
.col-pill-req {
    background: rgba(255,68,102,0.08);
    border-color: rgba(255,68,102,0.3);
    color: var(--hi);
}
.upload-result {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px 14px;
    margin: 10px 0;
    font-size: 12px;
}
.upload-ok   { border-left: 3px solid var(--lo);  }
.upload-err  { border-left: 3px solid var(--hi);  }
.upload-warn { border-left: 3px solid var(--med); }

/* ── Radio override ── */
.stRadio > div { gap: 6px !important; }
.stRadio label { color: var(--text) !important; font-size: 12px !important; }

/* ── Export button style ── */
.stDownloadButton > button {
    background: rgba(0,194,255,0.1) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(0,194,255,0.3) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
    text-transform: uppercase !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,194,255,0.2) !important;
    color: var(--accent) !important;
}

/* ── Task Reminder styles ── */
:root { --task: #ff9933; }
.metric-card.task::before { background: var(--task); }
.metric-card.task .metric-value { color: var(--task); }
.bulk-panel-task { border-top-color: var(--task); }
.task-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--task);
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.15s;
}
.task-card:hover { border-color: var(--border-hi); }
.task-card.overdue { border-left-color: var(--hi); background: rgba(255,68,102,0.04); }
.task-card.due-today { border-left-color: var(--med); background: rgba(255,170,0,0.04); }
.task-card.done { border-left-color: var(--lo); opacity: 0.65; }
.task-card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 8px;
    line-height: 1.5;
}
.task-card-meta {
    font-size: 12px;
    color: var(--text);
    display: flex;
    gap: 18px;
    flex-wrap: wrap;
    align-items: center;
}
.task-badge {
    display: inline-block;
    background: rgba(255,153,51,0.15);
    color: var(--task);
    border: 1px solid rgba(255,153,51,0.3);
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 2px 9px;
    text-transform: uppercase;
}
.overdue-badge {
    background: rgba(255,68,102,0.15);
    color: var(--hi);
    border-color: rgba(255,68,102,0.4);
}
.today-badge {
    background: rgba(255,170,0,0.15);
    color: var(--med);
    border-color: rgba(255,170,0,0.4);
}
</style>""", unsafe_allow_html=True)


# ─── Data layer ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
OPS_CSV    = os.path.join(BASE_DIR, "DELTA_OPS_data.csv")
CIRC_CSV   = os.path.join(BASE_DIR, "DELTA_OPS_circular_data.csv")
TASK_CSV   = os.path.join(BASE_DIR, "DELTA_OPS_task_data.csv")

OPS_COLUMNS  = ["team", "issue_description", "issue_date", "reported_to", "severity", "status"]
CIRC_COLUMNS = ["team", "circular_description", "due_date", "reported_to", "severity", "status"]
TASK_COLUMNS = ["team", "issue_description", "due_date", "task", "severity", "status"]

OPS_TEAMS    = ["DP", "BROKING", "EAGLE"]
CIRC_TEAMS   = ["DP", "BROKING", "EAGLE", "COMPLIANCE"]
TASK_TEAMS   = ["DP", "BROKING", "EAGLE", "COMPLIANCE"]
SEVERITIES   = ["High", "Medium", "Low"]
STATUSES     = ["Open", "In Progress", "Closed"]
OPS_REPORTED_TO  = ["Tech Excel", "CDSL", "NSE", "BSE", "EGD-Tech"]
CIRC_REPORTED_TO = ["SEBI", "NSE", "BSE", "NSDL", "CDSL", "Techexcel", "Tech", "EGD"]
TASK_TYPES   = ["MNRL", "Closure Email", "Testing", "Review", "Reporting", "Follow Up", "Escalation", "Other"]

# ── Sheet tab names (must match exactly in your Google Sheet) ─────────────────
GS_TAB_OPS  = "ops_data"
GS_TAB_CIRC = "circular_data"
GS_TAB_TASK = "task_data"


# ─── Google Sheets connection (optional — falls back to CSV if not configured) ─
def _get_gsheet():
    """
    Returns a gspread.Spreadsheet object if Google Sheets credentials are
    configured in st.secrets, otherwise returns None (CSV fallback mode).

    To enable Google Sheets:
    1. Go to console.cloud.google.com → create a Service Account
    2. Give it Editor access to your Google Sheet
    3. Download the JSON key file
    4. Add to .streamlit/secrets.toml:

        [gcp_service_account]
        type                        = "service_account"
        project_id                  = "YOUR_PROJECT_ID"
        private_key_id              = "..."
        private_key                 = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
        client_email                = "your-sa@your-project.iam.gserviceaccount.com"
        client_id                   = "..."
        auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
        token_uri                   = "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url        = "..."

        [google_sheets]
        spreadsheet_id = "YOUR_SPREADSHEET_ID_FROM_URL"

    5. On Streamlit Cloud: paste these into App Settings → Secrets
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = dict(st.secrets["gcp_service_account"])
        sheet_id   = st.secrets["google_sheets"]["spreadsheet_id"]

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id)
    except Exception:
        return None  # secrets not set or gspread not installed → use CSV


def _ensure_tab(sheet, tab_name: str, headers: list):
    """Create the worksheet tab if it doesn't exist, write headers."""
    try:
        ws = sheet.worksheet(tab_name)
    except Exception:
        ws = sheet.add_worksheet(title=tab_name, rows=2000, cols=len(headers))
        ws.append_row(headers, value_input_option="USER_ENTERED")
    return ws


def _gsheet_read(tab_name: str, columns: list, date_cols: list) -> pd.DataFrame:
    """Read a sheet tab into a DataFrame. Returns empty DF on any failure."""
    try:
        sh = _get_gsheet()
        if sh is None:
            return None  # signal: use CSV
        ws = _ensure_tab(sh, tab_name, columns)
        records = ws.get_all_records(expected_headers=columns)
        if not records:
            return pd.DataFrame(columns=columns)
        df = pd.DataFrame(records)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns].copy()
        for dc in date_cols:
            df[dc] = pd.to_datetime(df[dc], dayfirst=True, errors="coerce")
        return df
    except Exception:
        return None  # signal: use CSV


def _gsheet_write(df: pd.DataFrame, tab_name: str, columns: list, date_fmt_cols: dict):
    """
    Overwrite an entire sheet tab with current DataFrame.
    date_fmt_cols: {col_name: strftime_format}  e.g. {"issue_date": "%d-%m-%Y"}
    """
    try:
        sh = _get_gsheet()
        if sh is None:
            return False
        ws = _ensure_tab(sh, tab_name, columns)

        out = df[columns].copy()
        for col, fmt in date_fmt_cols.items():
            out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime(fmt).fillna("")

        # Clear and rewrite — faster than cell-by-cell for small datasets
        ws.clear()
        ws.append_row(columns, value_input_option="USER_ENTERED")
        if len(out) > 0:
            rows = out.fillna("").values.tolist()
            ws.append_rows(rows, value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False


# ─── Load functions (Google Sheets → CSV fallback) ───────────────────────────
def load_ops():
    df = _gsheet_read(GS_TAB_OPS, OPS_COLUMNS, ["issue_date"])
    if df is not None:
        return df
    # CSV fallback
    if os.path.exists(OPS_CSV):
        try:
            df = pd.read_csv(OPS_CSV)
            for col in OPS_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[OPS_COLUMNS].copy()
            df["issue_date"] = pd.to_datetime(df["issue_date"], dayfirst=True, errors="coerce")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=OPS_COLUMNS)


def load_circ():
    df = _gsheet_read(GS_TAB_CIRC, CIRC_COLUMNS, ["due_date"])
    if df is not None:
        return df
    # CSV fallback
    if os.path.exists(CIRC_CSV):
        try:
            df = pd.read_csv(CIRC_CSV)
            for col in CIRC_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[CIRC_COLUMNS].copy()
            df["due_date"] = pd.to_datetime(df["due_date"], dayfirst=True, errors="coerce")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=CIRC_COLUMNS)


def load_task():
    df = _gsheet_read(GS_TAB_TASK, TASK_COLUMNS, ["due_date"])
    if df is not None:
        return df
    # CSV fallback
    if os.path.exists(TASK_CSV):
        try:
            df = pd.read_csv(TASK_CSV)
            for col in TASK_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[TASK_COLUMNS].copy()
            df["due_date"] = pd.to_datetime(df["due_date"], dayfirst=True, errors="coerce")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=TASK_COLUMNS)


# ─── Save functions (Google Sheets + CSV backup) ─────────────────────────────
def save_ops(df):
    # Always write CSV as local backup
    out = df.copy()
    out["issue_date"] = pd.to_datetime(out["issue_date"], errors="coerce").dt.strftime("%d-%m-%Y")
    try:
        out.to_csv(OPS_CSV, index=False)
    except Exception:
        pass
    # Write to Google Sheets if connected
    _gsheet_write(df, GS_TAB_OPS, OPS_COLUMNS, {"issue_date": "%d-%m-%Y"})


def save_circ(df):
    out = df.copy()
    out["due_date"] = pd.to_datetime(out["due_date"], errors="coerce").dt.strftime("%d-%m-%Y")
    try:
        out.to_csv(CIRC_CSV, index=False)
    except Exception:
        pass
    _gsheet_write(df, GS_TAB_CIRC, CIRC_COLUMNS, {"due_date": "%d-%m-%Y"})


# ─── Bulk upload helpers ───────────────────────────────────────────────────────

def make_ops_template() -> bytes:
    sample = pd.DataFrame([
        {"team": "DP",      "issue_description": "Settlement mismatch detected in morning run",
         "issue_date": date.today().strftime("%d-%m-%Y"), "reported_to": "Tech Excel", "severity": "High",   "status": "Open"},
        {"team": "BROKING", "issue_description": "Client account showing FO capital shortfall post EOD",
         "issue_date": date.today().strftime("%d-%m-%Y"), "reported_to": "CDSL",       "severity": "Medium", "status": "In Progress"},
        {"team": "EAGLE",   "issue_description": "EOD reconciliation failed for BSE segment",
         "issue_date": (date.today() - timedelta(days=2)).strftime("%d-%m-%Y"), "reported_to": "BSE", "severity": "Low", "status": "Closed"},
    ])
    return sample.to_csv(index=False).encode()


def make_circ_template() -> bytes:
    """Template matching revised circular format: Team, Circular_No_description, Due_date, reported_to, severity, status"""
    sample = pd.DataFrame([
        {"Team": "DP",         "Circular_No_description": "Nomination",          "Due_date": date.today().strftime("%d-%m-%Y"), "reported_to": "Techexcel", "severity": "High",   "status": "Open"},
        {"Team": "BROKING",    "Circular_No_description": "Settlement Holidays",  "Due_date": date.today().strftime("%d-%m-%Y"), "reported_to": "Tech",      "severity": "Medium", "status": "In Progress"},
        {"Team": "EAGLE",      "Circular_No_description": "Risk Metrics",         "Due_date": (date.today() - timedelta(days=3)).strftime("%d-%m-%Y"), "reported_to": "CDSL", "severity": "Low", "status": "Closed"},
        {"Team": "COMPLIANCE", "Circular_No_description": "RMS",                  "Due_date": (date.today() - timedelta(days=3)).strftime("%d-%m-%Y"), "reported_to": "CDSL", "severity": "Low", "status": "Closed"},
    ])
    return sample.to_csv(index=False).encode()


def validate_ops_bulk(df_raw: pd.DataFrame):
    """Validate OPS CSV upload. Returns (clean_df, errors_list)."""
    errors = []
    df = df_raw.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    REQUIRED = ["team", "issue_description", "issue_date", "reported_to", "severity", "status"]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
        errors.append(f"Your file columns: {list(df.columns)}")
        errors.append(f"Required: {REQUIRED}")
        return None, errors

    df["team"]              = df["team"].astype(str).str.strip().str.upper()
    df["severity"]          = df["severity"].astype(str).str.strip().str.title()
    df["status"]            = df["status"].astype(str).str.strip().str.title()
    df["reported_to"]       = df["reported_to"].astype(str).str.strip()
    df["issue_description"] = df["issue_description"].astype(str).str.strip()

    bad_team = df[~df["team"].isin(OPS_TEAMS)]["team"].unique().tolist()
    if bad_team:
        errors.append(f"Invalid team(s): {bad_team} — must be one of {OPS_TEAMS}")

    bad_sev = df[~df["severity"].isin(SEVERITIES)]["severity"].unique().tolist()
    if bad_sev:
        errors.append(f"Invalid severity: {bad_sev} — must be one of {SEVERITIES}")

    bad_stat = df[~df["status"].isin(STATUSES)]["status"].unique().tolist()
    if bad_stat:
        errors.append(f"Invalid status: {bad_stat} — must be one of {STATUSES}")

    parsed_dates = pd.to_datetime(df["issue_date"], dayfirst=True, errors="coerce")
    null_dates = int(parsed_dates.isna().sum())
    if null_dates:
        errors.append(f"{null_dates} invalid date(s). Use DD-MM-YYYY or YYYY-MM-DD.")
    df["issue_date"] = parsed_dates

    empty_desc = int((df["issue_description"].str.len() == 0).sum())
    if empty_desc:
        errors.append(f"{empty_desc} row(s) have empty issue_description.")

    if errors:
        return None, errors

    return df[OPS_COLUMNS], []


def validate_circ_bulk(df_raw: pd.DataFrame):
    """Validate Circular CSV upload. Returns (clean_df, errors_list).
    Accepts: Team, Circular_No_description, Due_date, reported_to, severity, status"""
    errors = []
    df = df_raw.copy()

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Accept aliases for circular description column
    col_aliases = {
        "circular_no_description": "circular_description",
        "circular_no/description": "circular_description",
        "description": "circular_description",
        "issue_description": "circular_description",
        "circular": "circular_description",
    }
    for alias, canonical in col_aliases.items():
        if alias in df.columns and canonical not in df.columns:
            df.rename(columns={alias: canonical}, inplace=True)

    # Accept due_date or issue_date
    if "issue_date" in df.columns and "due_date" not in df.columns:
        df.rename(columns={"issue_date": "due_date"}, inplace=True)

    REQUIRED = ["team", "circular_description", "due_date", "reported_to", "severity", "status"]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
        errors.append(f"Your file columns: {list(df.columns)}")
        errors.append(f"Required: Team, Circular_No_description, Due_date, reported_to, severity, status")
        return None, errors

    df["team"]                 = df["team"].astype(str).str.strip().str.upper()
    df["severity"]             = df["severity"].astype(str).str.strip().str.title()
    df["status"]               = df["status"].astype(str).str.strip().str.title()
    df["reported_to"]          = df["reported_to"].astype(str).str.strip()
    df["circular_description"] = df["circular_description"].astype(str).str.strip()

    bad_team = df[~df["team"].isin(CIRC_TEAMS)]["team"].unique().tolist()
    if bad_team:
        errors.append(f"Invalid team(s): {bad_team} — must be one of {CIRC_TEAMS}")

    bad_sev = df[~df["severity"].isin(SEVERITIES)]["severity"].unique().tolist()
    if bad_sev:
        errors.append(f"Invalid severity: {bad_sev} — must be one of {SEVERITIES}")

    bad_stat = df[~df["status"].isin(STATUSES)]["status"].unique().tolist()
    if bad_stat:
        errors.append(f"Invalid status: {bad_stat} — must be one of {STATUSES}")

    parsed_dates = pd.to_datetime(df["due_date"], dayfirst=True, errors="coerce")
    null_dates = int(parsed_dates.isna().sum())
    if null_dates:
        errors.append(f"{null_dates} invalid date(s) in 'due_date'. Use DD-MM-YYYY or YYYY-MM-DD.")
    df["due_date"] = parsed_dates

    empty_desc = int((df["circular_description"].str.len() == 0).sum())
    if empty_desc:
        errors.append(f"{empty_desc} row(s) have empty Circular_No_description.")

    if errors:
        return None, errors

    return df[CIRC_COLUMNS], []


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode()


def load_task():
    if os.path.exists(TASK_CSV):
        try:
            df = pd.read_csv(TASK_CSV)
            for col in TASK_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[TASK_COLUMNS].copy()
            df["due_date"] = pd.to_datetime(df["due_date"], dayfirst=True, errors="coerce")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=TASK_COLUMNS)


def save_task(df):
    out = df.copy()
    out["due_date"] = pd.to_datetime(out["due_date"], errors="coerce").dt.strftime("%d-%m-%Y")
    try:
        out.to_csv(TASK_CSV, index=False)
    except Exception:
        pass
    _gsheet_write(df, GS_TAB_TASK, TASK_COLUMNS, {"due_date": "%d-%m-%Y"})


def make_task_template() -> bytes:
    sample = pd.DataFrame([
        {"team": "DP",      "issue_description": "SEBI circular SEBI/HO/MRD/2026/001 — settlement cycle update",
         "Due Date": date.today().strftime("%d-%m-%Y"), "Task": "MNRL",          "severity": "High",   "status": "Open"},
        {"team": "BROKING", "issue_description": "NSE circular implementation — peak margin reporting change",
         "Due Date": date.today().strftime("%d-%m-%Y"), "Task": "Closure Email", "severity": "Medium", "status": "In Progress"},
        {"team": "EAGLE",   "issue_description": "CDSL circular — KYC re-validation for dormant accounts",
         "Due Date": (date.today() - timedelta(days=3)).strftime("%d-%m-%Y"), "Task": "Testing", "severity": "Low", "status": "Closed"},
    ])
    return sample.to_csv(index=False).encode()


def validate_task_bulk(df_raw: pd.DataFrame):
    """Validate Task CSV upload. Returns (clean_df, errors_list).
    Accepts: team, issue_description, Due Date, Task, severity, status"""
    errors = []
    df = df_raw.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Accept 'due_date' alias
    if "due_date" not in df.columns and "issue_date" in df.columns:
        df.rename(columns={"issue_date": "due_date"}, inplace=True)

    REQUIRED = ["team", "issue_description", "due_date", "task", "severity", "status"]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
        errors.append(f"Your file columns: {list(df.columns)}")
        errors.append(f"Required: team, issue_description, Due Date, Task, severity, status")
        return None, errors

    df["team"]              = df["team"].astype(str).str.strip().str.upper()
    df["severity"]          = df["severity"].astype(str).str.strip().str.title()
    df["status"]            = df["status"].astype(str).str.strip().str.title()
    df["task"]              = df["task"].astype(str).str.strip()
    df["issue_description"] = df["issue_description"].astype(str).str.strip()

    bad_team = df[~df["team"].isin(TASK_TEAMS)]["team"].unique().tolist()
    if bad_team:
        errors.append(f"Invalid team(s): {bad_team} — must be one of {TASK_TEAMS}")

    bad_sev = df[~df["severity"].isin(SEVERITIES)]["severity"].unique().tolist()
    if bad_sev:
        errors.append(f"Invalid severity: {bad_sev} — must be one of {SEVERITIES}")

    bad_stat = df[~df["status"].isin(STATUSES)]["status"].unique().tolist()
    if bad_stat:
        errors.append(f"Invalid status: {bad_stat} — must be one of {STATUSES}")

    parsed_dates = pd.to_datetime(df["due_date"], dayfirst=True, errors="coerce")
    null_dates = int(parsed_dates.isna().sum())
    if null_dates:
        errors.append(f"{null_dates} invalid date(s) in 'Due Date'. Use DD-MM-YYYY or YYYY-MM-DD.")
    df["due_date"] = parsed_dates

    empty_desc = int((df["issue_description"].str.len() == 0).sum())
    if empty_desc:
        errors.append(f"{empty_desc} row(s) have empty issue_description.")

    if errors:
        return None, errors

    return df[TASK_COLUMNS], []


# ── Session state ─────────────────────────────────────────────────────────────
if "ops_data" not in st.session_state:
    st.session_state["ops_data"] = load_ops()
if "circ_data" not in st.session_state:
    st.session_state["circ_data"] = load_circ()
if "task_data" not in st.session_state:
    st.session_state["task_data"] = load_task()

# Flash message state
if "flash" not in st.session_state:
    st.session_state["flash"] = None

# Active tab tracking — used to return to the correct tab after rerun
# Values: "ops", "circ", "task", None (defaults to dashboard on ops import)
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = None

df_ops  = st.session_state["ops_data"]
df_circ = st.session_state["circ_data"]
df_task = st.session_state["task_data"]

# ─── Header ───────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y  %H:%M")
st.markdown(f"""
<div class="ops-header">
    <div class="ops-logo">⚡ DELTA <span>OPS</span></div>
    <div class="ops-timestamp">LAST REFRESH · {now_str} IST</div>
</div>
""", unsafe_allow_html=True)

# Flash message is displayed per-tab below (so it appears in the right context)
_flash_snapshot = st.session_state.get("flash")
if _flash_snapshot:
    st.session_state["flash"] = None  # consume immediately


def show_flash():
    """Render and clear the flash message in the current tab context."""
    if _flash_snapshot:
        ftype, fmsg = _flash_snapshot
        if ftype == "success":
            st.markdown(f'<div class="alert-bar alert-success">✅ &nbsp; {fmsg}</div>', unsafe_allow_html=True)
        elif ftype == "error":
            st.markdown(f'<div class="alert-bar alert-hi">❌ &nbsp; {fmsg}</div>', unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────
_tab_index_map = {"dashboard": 0, "ops": 1, "circ": 2, "task": 3}
_default_tab = _tab_index_map.get(st.session_state.get("active_tab", "dashboard"), 0)

tab1, tab2, tab3, tab4 = st.tabs(["01  DASHBOARD", "02  OPERATIONAL ISSUES", "03  CIRCULAR IMPLEMENTATION", "04  TASK REMINDERS"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)
    if st.session_state.get("active_tab") == "dashboard":
        show_flash()
        st.session_state["active_tab"] = None

    # ── Alert bar for open high-severity ─────────────────────────────────────
    hi_open = df_ops[(df_ops["severity"] == "High") & (df_ops["status"] == "Open")]
    if len(hi_open) > 0:
        teams_aff = ", ".join(hi_open["team"].unique())
        st.markdown(f'<div class="alert-bar alert-hi">⚠ &nbsp; {len(hi_open)} HIGH severity operational issue(s) open — Teams: {teams_aff}</div>', unsafe_allow_html=True)

    # ── Alert bar for overdue tasks ───────────────────────────────────────────
    today_ts = pd.Timestamp(date.today())
    if not df_task.empty:
        overdue_tasks = df_task[
            (df_task["due_date"] < today_ts) &
            (~df_task["status"].str.strip().str.lower().isin(["closed"]))
        ]
        if len(overdue_tasks) > 0:
            ot_teams = ", ".join(overdue_tasks["team"].unique())
            st.markdown(f'<div class="alert-bar alert-hi">🔔 &nbsp; {len(overdue_tasks)} OVERDUE task(s) — Teams: {ot_teams}</div>', unsafe_allow_html=True)

    # ── Metric cards ─────────────────────────────────────────────────────────
    total_ops  = len(df_ops)
    n_open     = (df_ops["status"] == "Open").sum()
    n_inprog   = (df_ops["status"] == "In Progress").sum()
    n_closed   = (df_ops["status"] == "Closed").sum()
    n_high     = (df_ops["severity"] == "High").sum()
    n_circ     = len(df_circ)
    n_task     = len(df_task)
    n_task_overdue = 0 if df_task.empty else int((
        (df_task["due_date"] < today_ts) &
        (~df_task["status"].str.strip().str.lower().isin(["closed"]))
    ).sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card hi">
            <div class="metric-label">Open Issues</div>
            <div class="metric-value">{n_open}</div>
            <div class="metric-sub">of {total_ops} total ops</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card med">
            <div class="metric-label">In Progress</div>
            <div class="metric-value">{n_inprog}</div>
            <div class="metric-sub">being actioned</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card lo">
            <div class="metric-label">Closed</div>
            <div class="metric-value">{n_closed}</div>
            <div class="metric-sub">resolved</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card circ">
            <div class="metric-label">Circular Items</div>
            <div class="metric-value">{n_circ}</div>
            <div class="metric-sub">{(df_circ["severity"]=="High").sum() if not df_circ.empty else 0} high severity</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-card task">
            <div class="metric-label">Task Reminders</div>
            <div class="metric-value">{n_task}</div>
            <div class="metric-sub">{n_task_overdue} overdue</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Helper pills (defined here for dashboard use) ─────────────────────────
    def sev_pill(s):
        cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(s, "low")
        return f'<span class="pill pill-{cls}">{s}</span>'

    def status_pill(s):
        cls = {"Open": "open", "In Progress": "inprogress", "Closed": "closed"}.get(s, "closed")
        return f'<span class="pill pill-{cls}">{s}</span>'

    # ── Row 1: Ops charts ─────────────────────────────────────────────────────
    st.markdown('<p class="section-title">Operational Issues</p>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1.2, 1, 1])

    with col_a:
        st.markdown('<p class="section-title">Status Breakdown</p>', unsafe_allow_html=True)
        if not df_ops.empty:
            status_counts = df_ops["status"].value_counts()
            colors_status = {"Open": "#ff4466", "In Progress": "#ffaa00", "Closed": "#00dd88"}
            fig_donut = go.Figure(go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.62,
                marker_colors=[colors_status.get(s, "#4a6080") for s in status_counts.index],
                textfont_size=11,
                textfont_family="IBM Plex Mono",
                showlegend=True,
            ))
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220, margin=dict(t=10,b=10,l=10,r=10),
                legend=dict(font=dict(family="IBM Plex Mono", size=10), orientation="h",
                            yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{total_ops}</b>", x=0.5, y=0.5,
                                  font_size=22, font_family="IBM Plex Mono",
                                  font_color="#c8d8f0", showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False}, key="db_donut")
        else:
            st.markdown('<div class="alert-bar alert-info">No ops data yet.</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<p class="section-title">Severity Distribution</p>', unsafe_allow_html=True)
        if not df_ops.empty:
            sev_counts = df_ops["severity"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
            fig_sev = go.Figure(go.Bar(
                x=sev_counts.values,
                y=sev_counts.index,
                orientation="h",
                marker_color=["#ff4466","#ffaa00","#00dd88"],
                text=sev_counts.values.astype(int),
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=12, color="#c8d8f0"),
            ))
            fig_sev.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220,
                margin=dict(t=10,b=10,l=10,r=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(tickfont=dict(family="IBM Plex Mono", size=11)),
            )
            st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False}, key="db_sev")

    with col_c:
        st.markdown('<p class="section-title">Issues by Team</p>', unsafe_allow_html=True)
        if not df_ops.empty:
            team_counts = df_ops["team"].value_counts()
            fig_team = go.Figure(go.Bar(
                x=team_counts.index,
                y=team_counts.values,
                marker_color="#00c2ff",
                marker_opacity=0.75,
                text=team_counts.values,
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=11, color="#c8d8f0"),
            ))
            fig_team.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220,
                margin=dict(t=30,b=10,l=10,r=10),
                xaxis=dict(tickfont=dict(family="IBM Plex Mono", size=10), gridcolor="#1e2d4a"),
                yaxis=dict(showgrid=True, gridcolor="#1e2d4a", showticklabels=False,
                           range=[0, team_counts.values.max() * 1.35]),
            )
            st.plotly_chart(fig_team, use_container_width=True, config={"displayModeBar": False}, key="db_team")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Circular Implementation charts ────────────────────────────────
    st.markdown('<p class="section-title">Circular Implementation</p>', unsafe_allow_html=True)
    circ_col1, circ_col2, circ_col3 = st.columns([1.2, 1, 1])

    with circ_col1:
        st.markdown('<p class="section-title">Status Breakdown</p>', unsafe_allow_html=True)
        if not df_circ.empty:
            circ_status_counts2 = df_circ["status"].value_counts()
            colors_cs = {"Open": "#ff4466", "In Progress": "#ffaa00", "Closed": "#00dd88"}
            fig_circ_donut = go.Figure(go.Pie(
                labels=circ_status_counts2.index,
                values=circ_status_counts2.values,
                hole=0.62,
                marker_colors=[colors_cs.get(s, "#aa66ff") for s in circ_status_counts2.index],
                textfont_size=11, textfont_family="IBM Plex Mono", showlegend=True,
            ))
            fig_circ_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220, margin=dict(t=10,b=10,l=10,r=10),
                legend=dict(font=dict(family="IBM Plex Mono", size=10), orientation="h",
                            yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{len(df_circ)}</b>", x=0.5, y=0.5,
                                  font_size=22, font_family="IBM Plex Mono",
                                  font_color="#c8d8f0", showarrow=False)]
            )
            st.plotly_chart(fig_circ_donut, use_container_width=True, config={"displayModeBar": False}, key="db_circ_donut")
        else:
            st.markdown('<div class="alert-bar alert-info">No circular data yet.</div>', unsafe_allow_html=True)

    with circ_col2:
        st.markdown('<p class="section-title">Completion Progress</p>', unsafe_allow_html=True)
        if not df_circ.empty:
            circ_status_counts = df_circ["status"].value_counts()
            total_c = circ_status_counts.sum()
            pct_done = int(circ_status_counts.get("Closed", 0) / total_c * 100) if total_c > 0 else 0
            fig_prog_db = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct_done,
                number={"suffix": "%", "font": {"family": "IBM Plex Mono", "size": 32, "color": "#00dd88"}},
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#4a6080",
                              tickfont=dict(family="IBM Plex Mono", size=10)),
                    bar=dict(color="#00dd88", thickness=0.3),
                    bgcolor="#0c1020",
                    borderwidth=1, bordercolor="#1e2d4a",
                    steps=[
                        dict(range=[0, 40],  color="#1a0a0f"),
                        dict(range=[40, 70], color="#1a150a"),
                        dict(range=[70, 100], color="#0a1a12"),
                    ],
                    threshold=dict(line=dict(color="#aa66ff", width=3), thickness=0.8, value=75)
                ),
                title={"text": "Circulars Closed", "font": {"family": "IBM Plex Mono", "size": 11, "color": "#4a6080"}},
            ))
            fig_prog_db.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color="#c8d8f0",
                height=220, margin=dict(t=30, b=10, l=30, r=30)
            )
            st.plotly_chart(fig_prog_db, use_container_width=True, config={"displayModeBar": False}, key="db_prog")

    with circ_col3:
        st.markdown('<p class="section-title">By Team</p>', unsafe_allow_html=True)
        if not df_circ.empty:
            circ_team = df_circ["team"].value_counts()
            fig_ct_db = go.Figure(go.Bar(
                x=circ_team.index, y=circ_team.values,
                marker_color="#aa66ff", marker_opacity=0.75,
                text=circ_team.values, textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=11, color="#c8d8f0"),
            ))
            fig_ct_db.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220,
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis=dict(tickfont=dict(family="IBM Plex Mono", size=10)),
                yaxis=dict(showgrid=True, gridcolor="#1e2d4a", showticklabels=False,
                           range=[0, circ_team.values.max() * 1.35]),
            )
            st.plotly_chart(fig_ct_db, use_container_width=True, config={"displayModeBar": False}, key="db_ct")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Task Reminder charts ───────────────────────────────────────────
    st.markdown('<p class="section-title">Task Reminders</p>', unsafe_allow_html=True)
    task_col1, task_col2, task_col3 = st.columns([1.2, 1, 1])

    with task_col1:
        st.markdown('<p class="section-title">By Status</p>', unsafe_allow_html=True)
        if not df_task.empty:
            task_stat_counts = df_task["status"].value_counts()
            colors_ts = {"Open": "#ff4466", "In Progress": "#ffaa00", "Closed": "#00dd88"}
            fig_ts_db = go.Figure(go.Pie(
                labels=task_stat_counts.index,
                values=task_stat_counts.values,
                hole=0.55,
                marker_colors=[colors_ts.get(s, "#ff9933") for s in task_stat_counts.index],
                textfont_size=10, textfont_family="IBM Plex Mono", showlegend=True,
            ))
            fig_ts_db.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220, margin=dict(t=10,b=10,l=10,r=10),
                legend=dict(font=dict(family="IBM Plex Mono", size=9), orientation="h",
                            yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{len(df_task)}</b>", x=0.5, y=0.5,
                                  font_size=20, font_family="IBM Plex Mono",
                                  font_color="#c8d8f0", showarrow=False)]
            )
            st.plotly_chart(fig_ts_db, use_container_width=True, config={"displayModeBar": False}, key="db_ts")
        else:
            st.markdown('<div class="alert-bar alert-info">No task data yet.</div>', unsafe_allow_html=True)

    with task_col2:
        st.markdown('<p class="section-title">Task Status Overview</p>', unsafe_allow_html=True)
        if not df_task.empty:
            today_norm = pd.Timestamp(date.today()).normalize()
            due_norm   = pd.to_datetime(df_task["due_date"], errors="coerce").dt.normalize()
            is_closed    = df_task["status"].str.strip().str.lower() == "closed"
            is_overdue   = (due_norm < today_norm) & (~is_closed)
            is_due_today = (due_norm == today_norm) & (~is_closed)

            n_closed    = int(is_closed.sum())
            n_due_today = int(is_due_today.sum())
            n_overdue   = int(is_overdue.sum())
            total_tasks = len(df_task)
            def pct(n): return round(n / total_tasks * 100) if total_tasks > 0 else 0

            categories = ["Closed",    "Due Today",  "Overdue"]
            values     = [n_closed,    n_due_today,  n_overdue]
            colors     = ["#00dd88",   "#ffaa00",    "#ff4466"]
            borders    = ["#00ff99",   "#ffcc44",    "#ff6680"]
            txt_dark   = ["#001a0d",   "#1a0f00",    "#1a000a"]

            fig_ot = go.Figure()
            for cat, val, col, bord, tdark in zip(categories, values, colors, borders, txt_dark):
                p     = pct(val)
                label = f"  {val}  ({p}%)"
                fig_ot.add_trace(go.Bar(
                    name=cat,
                    x=[max(val, 0.12)],   # tiny stub so zero rows still render
                    y=[cat],
                    orientation="h",
                    marker=dict(color=col, opacity=0.90, line=dict(color=bord, width=1.5)),
                    text=[label],
                    textposition="inside" if val > 0 else "outside",
                    textfont=dict(
                        family="IBM Plex Mono", size=13,
                        color=tdark if val > 0 else col
                    ),
                    insidetextanchor="middle",
                    width=0.52,
                    showlegend=False,
                ))

            max_val = max(values + [1])
            fig_ot.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0",
                height=220,
                margin=dict(t=10, b=28, l=82, r=40),
                showlegend=False,
                xaxis=dict(
                    showgrid=True, gridcolor="#1e2d4a",
                    showticklabels=False, zeroline=True,
                    zerolinecolor="#2a4070", zerolinewidth=1,
                    range=[0, max_val * 1.6],
                ),
                yaxis=dict(
                    tickfont=dict(family="IBM Plex Mono", size=12, color="#c8d8f0"),
                    tickcolor="#4a6080",
                    categoryorder="array",
                    categoryarray=["Overdue", "Due Today", "Closed"],
                ),
                bargap=0.30,
            )
            fig_ot.add_annotation(
                text=f"Total · {total_tasks} tasks",
                xref="paper", yref="paper",
                x=1.0, y=-0.16,
                showarrow=False,
                font=dict(family="IBM Plex Mono", size=9, color="#4a6080"),
                xanchor="right",
            )
            st.plotly_chart(fig_ot, use_container_width=True, config={"displayModeBar": False}, key="db_ot")

    with task_col3:
        st.markdown('<p class="section-title">Tasks by Team &amp; Status</p>', unsafe_allow_html=True)
        if not df_task.empty:
            teams_order_db = [t for t in TASK_TEAMS if t in df_task["team"].values]
            status_colors_db = [("Open", "#ff4466"), ("In Progress", "#ffaa00"), ("Closed", "#00dd88")]
            fig_tts_db = go.Figure()
            for status_val, color in status_colors_db:
                counts = [len(df_task[(df_task["team"] == t) & (df_task["status"] == status_val)]) for t in teams_order_db]
                fig_tts_db.add_trace(go.Bar(
                    name=status_val,
                    y=teams_order_db,
                    x=counts,
                    orientation="h",
                    marker=dict(color=color, opacity=0.88),
                    text=[str(c) if c > 0 else "" for c in counts],
                    textposition="inside",
                    textfont=dict(family="IBM Plex Mono", size=11, color="#ffffff"),
                    insidetextanchor="middle",
                ))
            fig_tts_db.update_layout(
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c8d8f0", height=220,
                margin=dict(t=10, b=10, l=10, r=30),
                xaxis=dict(showgrid=True, gridcolor="#1e2d4a", showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(family="IBM Plex Mono", size=11, color="#c8d8f0"), autorange="reversed"),
                legend=dict(font=dict(family="IBM Plex Mono", size=9, color="#c8d8f0"), orientation="h",
                            yanchor="bottom", y=-0.28, xanchor="center", x=0.5,
                            bgcolor="rgba(0,0,0,0)"),
                bargap=0.3,
            )
            st.plotly_chart(fig_tts_db, use_container_width=True, config={"displayModeBar": False}, key="db_tts")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — OPERATIONAL ISSUES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)
    if st.session_state.get("active_tab") == "ops":
        show_flash()
        st.session_state["active_tab"] = None

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<p class="section-title">Filter</p>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sel_team = st.multiselect("Team", options=OPS_TEAMS, default=[], key="f_team")
        with fc2:
            sel_sev = st.multiselect("Severity", options=SEVERITIES, default=[], key="f_sev")
        with fc3:
            sel_stat = st.multiselect("Status", options=STATUSES, default=[], key="f_stat")

        filt = df_ops.copy()
        if sel_team:  filt = filt[filt["team"].isin(sel_team)]
        if sel_sev:   filt = filt[filt["severity"].isin(sel_sev)]
        if sel_stat:  filt = filt[filt["status"].isin(sel_stat)]

        tbl_title_col, tbl_export_col = st.columns([3, 1])
        with tbl_title_col:
            st.markdown('<p class="section-title">Operational Issues</p>', unsafe_allow_html=True)
        with tbl_export_col:
            if not filt.empty:
                exp_filt = filt.copy()
                exp_filt["issue_date"] = pd.to_datetime(exp_filt["issue_date"], errors="coerce").dt.strftime("%d-%m-%Y")
                st.download_button(
                    "📤 Export",
                    data=exp_filt.to_csv(index=False).encode(),
                    file_name=f"DELTA_OPS_issues_{date.today().strftime('%d%m%Y')}.csv",
                    mime="text/csv",
                    key="export_ops_filtered",
                    use_container_width=True,
                )

        if filt.empty:
            st.markdown('<div class="alert-bar alert-info">No issues match current filters.</div>', unsafe_allow_html=True)
        else:
            def sev_pill(s):
                cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(s, "low")
                return f'<span class="pill pill-{cls}">{s}</span>'
            def status_pill(s):
                cls = {"Open": "open", "In Progress": "inprogress", "Closed": "closed"}.get(s, "closed")
                return f'<span class="pill pill-{cls}">{s}</span>'

            for status_label, default_open in [("Open", True), ("In Progress", True), ("Closed", False)]:
                group = filt[filt["status"] == status_label].sort_values("severity")
                if group.empty:
                    continue
                label = f"{status_label}  ({len(group)})"
                with st.expander(label, expanded=default_open):
                    rows_html2 = ""
                    for idx_row, row in group.iterrows():
                        date_str = row["issue_date"].strftime("%d %b %Y") if pd.notna(row["issue_date"]) else "—"
                        rows_html2 += f"""
                        <tr>
                            <td class="team-cell">{_html.escape(str(row['team']))}</td>
                            <td>{_html.escape(str(row['issue_description']))}</td>
                            <td>{date_str}</td>
                            <td>{_html.escape(str(row['reported_to']))}</td>
                            <td>{sev_pill(row['severity'])}</td>
                            <td>{status_pill(row['status'])}</td>
                        </tr>"""
                    st.markdown(f"""
                    <div class="chart-wrapper">
                    <table class="issue-table">
                        <thead><tr>
                            <th>Team</th><th>Description</th><th>Date</th>
                            <th>Reported To</th><th>Severity</th><th>Status</th>
                        </tr></thead>
                        <tbody>{rows_html2}</tbody>
                    </table>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Delete section ────────────────────────────────────────────────────
        if not df_ops.empty:
            st.markdown('<p class="section-title" style="margin-top:24px">Delete Issues</p>', unsafe_allow_html=True)
            ops_delete_options = {
                f"[{i}] {row['team']} | {str(row['issue_description'])[:50]} | {row['status']}": i
                for i, row in df_ops.iterrows()
            }
            ops_to_delete = st.multiselect(
                "Select issue(s) to delete (multi-select supported)",
                options=list(ops_delete_options.keys()),
                key="ops_delete_select"
            )
            if ops_to_delete:
                if st.button("🗑 DELETE SELECTED ISSUES", key="ops_delete_btn", use_container_width=True):
                    indices_to_drop = [ops_delete_options[k] for k in ops_to_delete]
                    st.session_state["ops_data"] = df_ops.drop(index=indices_to_drop).reset_index(drop=True)
                    save_ops(st.session_state["ops_data"])
                    st.session_state["flash"] = ("success", f"{len(indices_to_drop)} issue(s) deleted.")
                    st.session_state["active_tab"] = "ops"
                    st.rerun()

    with col_right:
        st.markdown('<p class="section-title">Log New Issue</p>', unsafe_allow_html=True)
        with st.container():
            f_team  = st.selectbox("Team", OPS_TEAMS, key="n_team")
            f_desc  = st.text_area("Issue Description", height=90, key="n_desc",
                                    placeholder="Describe the operational issue…")
            f_date  = st.date_input("Issue Date", value=date.today(), key="n_date")
            f_rep   = st.selectbox("Reported To", OPS_REPORTED_TO, key="n_rep")
            f_sev2  = st.selectbox("Severity", SEVERITIES, key="n_sev2")
            f_stat2 = st.selectbox("Status", STATUSES, key="n_stat2")

            if st.button("LOG ISSUE", key="log_btn"):
                if f_desc.strip():
                    new_row = {
                        "team":              f_team,
                        "issue_description": f_desc.strip(),
                        "issue_date":        pd.Timestamp(f_date),
                        "reported_to":       f_rep,
                        "severity":          f_sev2,
                        "status":            f_stat2,
                    }
                    st.session_state["ops_data"] = pd.concat(
                        [st.session_state["ops_data"], pd.DataFrame([new_row])],
                        ignore_index=True
                    )
                    save_ops(st.session_state["ops_data"])
                    st.session_state["flash"] = ("success", "Issue logged and saved.")
                    st.session_state["active_tab"] = "ops"
                    st.rerun()
                else:
                    st.error("Description cannot be empty.")

        # ── Update status ─────────────────────────────────────────────────────
        if len(df_ops) > 0:
            st.markdown('<p class="section-title" style="margin-top:24px">Update Status</p>', unsafe_allow_html=True)
            desc_options = df_ops["issue_description"].str[:55].tolist()
            sel_desc = st.selectbox("Select Issue", desc_options, key="upd_desc")
            new_status = st.selectbox("New Status", STATUSES, key="upd_stat")
            if st.button("UPDATE STATUS", key="upd_btn"):
                idx = df_ops[df_ops["issue_description"].str[:55] == sel_desc].index
                if len(idx) > 0:
                    st.session_state["ops_data"].loc[idx[0], "status"] = new_status
                    save_ops(st.session_state["ops_data"])
                    st.session_state["flash"] = ("success", "Status updated.")
                    st.session_state["active_tab"] = "ops"
                    st.rerun()

        # ── Bulk CSV Upload ────────────────────────────────────────────────────
        st.markdown("""
        <div class="bulk-panel">
            <div class="bulk-step"><b>BULK UPLOAD</b> · Operational Issues CSV</div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-title" style="margin-top:4px">Step 1 — Download Template</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:11px; color:#4a6080; margin-bottom:8px; font-family:'IBM Plex Mono',monospace;">
            <span style="color:#ff4466">★ Required columns:</span>
            team · issue_description · issue_date · reported_to · severity · status<br>
            <span style="color:#4a6080">team: DP | BROKING | EAGLE &nbsp;·&nbsp;
            severity: High | Medium | Low &nbsp;·&nbsp; status: Open | In Progress | Closed<br>
            Date format: DD-MM-YYYY or YYYY-MM-DD</span>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "📥 Download OPS Template",
            data=make_ops_template(),
            file_name="DELTA_OPS_issue_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_ops_tmpl"
        )

        st.markdown('<p class="section-title" style="margin-top:16px">Step 2 — Upload CSV</p>', unsafe_allow_html=True)

        uploaded_ops = st.file_uploader(
            "Upload Operational Issues CSV",
            type=["csv"],
            key="bulk_ops_upload",
        )

        if uploaded_ops is not None:
            # Use file hash to prevent processing same file twice
            file_key = f"ops_imported_{uploaded_ops.name}_{uploaded_ops.size}"

            try:
                raw_ops = pd.read_csv(uploaded_ops)
                st.markdown(
                    f'<div class="upload-result upload-ok">📄 <b>{uploaded_ops.name}</b> &nbsp;·&nbsp; '
                    f'<b>{len(raw_ops)}</b> rows detected</div>',
                    unsafe_allow_html=True
                )

                with st.expander("👁 Preview uploaded rows", expanded=False):
                    st.dataframe(raw_ops.head(10), use_container_width=True)

                clean_ops, errs_ops = validate_ops_bulk(raw_ops)

                if errs_ops:
                    for e in errs_ops:
                        st.markdown(f'<div class="upload-result upload-err">❌ {e}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="upload-result upload-warn">⚠ No data saved. Fix errors and re-upload.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="upload-result upload-ok">✅ Validation passed — '
                        f'<b>{len(clean_ops)}</b> issues ready to import</div>',
                        unsafe_allow_html=True
                    )

                    with st.expander("✅ Preview validated data", expanded=False):
                        st.dataframe(clean_ops, use_container_width=True)

                    st.markdown('<p class="section-title" style="margin-top:12px">Step 3 — Import Mode</p>', unsafe_allow_html=True)

                    ops_mode = st.radio(
                        "Import mode",
                        ["Append — add to existing", "Replace — clear all and import fresh"],
                        key="ops_import_mode",
                        index=0
                    )

                    if "Replace" in ops_mode:
                        st.markdown('<div class="upload-result upload-warn">⚠ Replace will permanently delete ALL current operational data.</div>', unsafe_allow_html=True)

                    # Guard: only show import button if this file hasn't been imported yet
                    already_imported = st.session_state.get(file_key, False)
                    if already_imported:
                        st.markdown('<div class="upload-result upload-ok">✅ This file has already been imported. Upload a new file to import again.</div>', unsafe_allow_html=True)
                    else:
                        if st.button("💾 CONFIRM IMPORT", key="ops_confirm_import", use_container_width=True):
                            existing = st.session_state["ops_data"]
                            if "Replace" in ops_mode:
                                merged = clean_ops.copy()
                            else:
                                merged = pd.concat([existing, clean_ops], ignore_index=True)
                            st.session_state["ops_data"] = merged
                            save_ops(merged)
                            st.session_state[file_key] = True  # mark as imported
                            st.session_state["flash"] = (
                                "success",
                                f"{len(clean_ops)} issues imported ({'replaced' if 'Replace' in ops_mode else 'appended'}). Total: {len(merged)} rows."
                            )
                            st.rerun()

            except Exception as e:
                st.markdown(f'<div class="upload-result upload-err">❌ Cannot read file: {e}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — CIRCULAR IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)
    if st.session_state.get("active_tab") == "circ":
        show_flash()
        st.session_state["active_tab"] = None

    col_cl, col_cr = st.columns([2, 1])

    with col_cl:
        # Filter bar for circulars
        st.markdown('<p class="section-title">Filter</p>', unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            c_sel_team = st.multiselect("Team", options=CIRC_TEAMS, default=[], key="cf_team")
        with cc2:
            c_sel_sev = st.multiselect("Severity", options=SEVERITIES, default=[], key="cf_sev")
        with cc3:
            c_sel_stat = st.multiselect("Status", options=STATUSES, default=[], key="cf_stat")

        filt_circ = df_circ.copy()
        if c_sel_team:  filt_circ = filt_circ[filt_circ["team"].isin(c_sel_team)]
        if c_sel_sev:   filt_circ = filt_circ[filt_circ["severity"].isin(c_sel_sev)]
        if c_sel_stat:  filt_circ = filt_circ[filt_circ["status"].isin(c_sel_stat)]

        # Title + export
        circ_title_col, circ_export_col = st.columns([3, 1])
        with circ_title_col:
            st.markdown('<p class="section-title">Active Circulars</p>', unsafe_allow_html=True)
        with circ_export_col:
            if not filt_circ.empty:
                exp_circ = filt_circ.copy()
                exp_circ["due_date"] = pd.to_datetime(exp_circ["due_date"], errors="coerce").dt.strftime("%d-%m-%Y")
                st.download_button(
                    "📤 Export",
                    data=exp_circ.to_csv(index=False).encode(),
                    file_name=f"DELTA_OPS_circulars_{date.today().strftime('%d%m%Y')}.csv",
                    mime="text/csv",
                    key="export_circ_filtered",
                    use_container_width=True,
                )

        if filt_circ.empty:
            st.markdown('<div class="alert-bar alert-info">No circular implementation items match filters. Log one using the form →</div>', unsafe_allow_html=True)
        else:
            def render_circ_cards(df_group):
                for _, row in df_group.iterrows():
                    date_str   = row["due_date"].strftime("%d %b %Y") if pd.notna(row["due_date"]) else "—"
                    status_cls = {"Open": "open", "In Progress": "inprogress", "Closed": "closed"}.get(str(row["status"]), "closed")
                    sev_cls    = {"High": "high", "Medium": "medium", "Low": "low"}.get(str(row["severity"]), "low")
                    desc       = _html.escape(str(row["circular_description"]))
                    team       = _html.escape(str(row["team"]))
                    rep_to     = _html.escape(str(row["reported_to"]))
                    sev_lbl    = _html.escape(str(row["severity"]))
                    stat_lbl   = _html.escape(str(row["status"]))
                    card = (
                        f'<div class="circ-card">'
                        f'<div class="circ-card-title">{desc}</div>'
                        f'<div class="circ-card-meta">'
                        f'<span class="card-team">{team}</span>'
                        f'<span class="card-meta-item">&#128197;&nbsp;{date_str}</span>'
                        f'<span class="card-meta-item">&#128228;&nbsp;{rep_to}</span>'
                        f'<span class="pill pill-{sev_cls}">{sev_lbl}</span>'
                        f'<span class="pill pill-{status_cls}">{stat_lbl}</span>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card, unsafe_allow_html=True)

            # ── Grouped expand/collapse by status ────────────────────────────
            for status_label, default_open in [("Open", True), ("In Progress", True), ("Closed", False)]:
                group = filt_circ[filt_circ["status"] == status_label].sort_values("severity")
                if group.empty:
                    continue
                label = f"{status_label}  ({len(group)})"
                with st.expander(label, expanded=default_open):
                    render_circ_cards(group)

        # ── Delete section ─────────────────────────────────────────────────────
        if not df_circ.empty:
            st.markdown('<p class="section-title" style="margin-top:24px">Delete Circular Items</p>', unsafe_allow_html=True)
            circ_delete_options = {
                f"[{i}] {row['team']} | {str(row['circular_description'])[:50]} | {row['status']}": i
                for i, row in df_circ.iterrows()
            }
            circ_to_delete = st.multiselect(
                "Select circular item(s) to delete (multi-select supported)",
                options=list(circ_delete_options.keys()),
                key="circ_delete_select"
            )
            if circ_to_delete:
                if st.button("🗑 DELETE SELECTED CIRCULARS", key="circ_delete_btn", use_container_width=True):
                    indices_to_drop = [circ_delete_options[k] for k in circ_to_delete]
                    st.session_state["circ_data"] = df_circ.drop(index=indices_to_drop).reset_index(drop=True)
                    save_circ(st.session_state["circ_data"])
                    st.session_state["flash"] = ("success", f"{len(indices_to_drop)} circular item(s) deleted.")
                    st.session_state["active_tab"] = "circ"
                    st.rerun()

    with col_cr:
        # ── Log circular ──────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Log Circular Item</p>', unsafe_allow_html=True)

        c_team  = st.selectbox("Team", CIRC_TEAMS, key="c_team")
        c_desc  = st.text_area("Circular Description", height=90, key="c_desc",
                                placeholder="Circular No / implementation detail…")
        c_date  = st.date_input("Due Date", value=date.today(), key="c_date")
        c_rep   = st.selectbox("Reported To", CIRC_REPORTED_TO, key="c_rep")
        c_sev   = st.selectbox("Severity", SEVERITIES, key="c_sev")
        c_stat  = st.selectbox("Status", STATUSES, key="c_stat")

        if st.button("LOG CIRCULAR", key="circ_btn"):
            if c_desc.strip():
                new_row = {
                    "team":                 c_team,
                    "circular_description": c_desc.strip(),
                    "due_date":             pd.Timestamp(c_date),
                    "reported_to":          c_rep,
                    "severity":             c_sev,
                    "status":               c_stat,
                }
                st.session_state["circ_data"] = pd.concat(
                    [st.session_state["circ_data"], pd.DataFrame([new_row])],
                    ignore_index=True
                )
                save_circ(st.session_state["circ_data"])
                st.session_state["flash"] = ("success", "Circular item logged.")
                st.session_state["active_tab"] = "circ"
                st.rerun()
            else:
                st.error("Description cannot be empty.")

        # ── Update circular status ────────────────────────────────────────────
        if not df_circ.empty:
            st.markdown('<p class="section-title" style="margin-top:24px">Update Circular Status</p>', unsafe_allow_html=True)
            circ_descs = df_circ["circular_description"].str[:55].tolist()
            sel_circ = st.selectbox("Select Circular", circ_descs, key="upd_circ_desc")
            new_circ_status = st.selectbox("New Status", STATUSES, key="upd_circ_stat")
            if st.button("UPDATE", key="upd_circ_btn"):
                idx = df_circ[df_circ["circular_description"].str[:55] == sel_circ].index
                if len(idx) > 0:
                    st.session_state["circ_data"].loc[idx[0], "status"] = new_circ_status
                    save_circ(st.session_state["circ_data"])
                    st.session_state["flash"] = ("success", "Circular status updated.")
                    st.session_state["active_tab"] = "circ"
                    st.rerun()

        # ── Bulk CSV Upload — Circulars ────────────────────────────────────────
        st.markdown("""
        <div class="bulk-panel bulk-panel-circ">
            <div class="bulk-step bulk-step-circ"><b style="color:#aa66ff">BULK UPLOAD</b> · Circular Implementation CSV</div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-title" style="margin-top:4px">Step 1 — Download Template</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:11px; color:#4a6080; margin-bottom:8px; font-family:'IBM Plex Mono',monospace;">
            <span style="color:#aa66ff">★ Required columns:</span>
            Team · Circular_No_description · Due_date · reported_to · severity · status<br>
            <span style="color:#4a6080">team: DP | BROKING | EAGLE | COMPLIANCE<br>
            severity: High | Medium | Low &nbsp;·&nbsp; status: Open | In Progress | Closed<br>
            Date format: DD-MM-YYYY or YYYY-MM-DD</span>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "📥 Download Circular Template",
            data=make_circ_template(),
            file_name="DELTA_OPS_circular_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_circ_tmpl"
        )

        st.markdown('<p class="section-title" style="margin-top:16px">Step 2 — Upload CSV</p>', unsafe_allow_html=True)

        uploaded_circ = st.file_uploader(
            "Upload Circular Items CSV",
            type=["csv"],
            key="bulk_circ_upload",
        )

        if uploaded_circ is not None:
            circ_file_key = f"circ_imported_{uploaded_circ.name}_{uploaded_circ.size}"

            try:
                raw_circ = pd.read_csv(uploaded_circ)
                st.markdown(
                    f'<div class="upload-result upload-ok">📄 <b>{uploaded_circ.name}</b> &nbsp;·&nbsp; '
                    f'<b>{len(raw_circ)}</b> rows detected</div>',
                    unsafe_allow_html=True
                )

                with st.expander("👁 Preview uploaded rows", expanded=False):
                    st.dataframe(raw_circ.head(10), use_container_width=True)

                clean_circ, errs_circ = validate_circ_bulk(raw_circ)

                if errs_circ:
                    for e in errs_circ:
                        st.markdown(f'<div class="upload-result upload-err">❌ {e}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="upload-result upload-warn">⚠ No data saved. Fix errors and re-upload.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="upload-result upload-ok">✅ Validation passed — '
                        f'<b>{len(clean_circ)}</b> circular items ready to import</div>',
                        unsafe_allow_html=True
                    )

                    with st.expander("✅ Preview validated data", expanded=False):
                        st.dataframe(clean_circ, use_container_width=True)

                    st.markdown('<p class="section-title" style="margin-top:12px">Step 3 — Import Mode</p>', unsafe_allow_html=True)

                    circ_mode = st.radio(
                        "Import mode",
                        ["Append — add to existing", "Replace — clear all and import fresh"],
                        key="circ_import_mode",
                        index=0
                    )

                    if "Replace" in circ_mode:
                        st.markdown('<div class="upload-result upload-warn">⚠ Replace will permanently delete ALL current circular data.</div>', unsafe_allow_html=True)

                    already_imported_circ = st.session_state.get(circ_file_key, False)
                    if already_imported_circ:
                        st.markdown('<div class="upload-result upload-ok">✅ This file has already been imported. Upload a new file to import again.</div>', unsafe_allow_html=True)
                    else:
                        if st.button("💾 CONFIRM IMPORT", key="circ_confirm_import", use_container_width=True):
                            existing_circ = st.session_state["circ_data"]
                            if "Replace" in circ_mode:
                                merged_circ = clean_circ.copy()
                            else:
                                merged_circ = pd.concat([existing_circ, clean_circ], ignore_index=True)
                            st.session_state["circ_data"] = merged_circ
                            save_circ(merged_circ)
                            st.session_state[circ_file_key] = True  # mark as imported
                            st.session_state["flash"] = (
                                "success",
                                f"{len(clean_circ)} circular items imported ({'replaced' if 'Replace' in circ_mode else 'appended'}). Total: {len(merged_circ)} rows."
                            )
                            st.session_state["active_tab"] = "circ"
                            st.rerun()

            except Exception as e:
                st.markdown(f'<div class="upload-result upload-err">❌ Cannot read file: {e}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — TASK REMINDERS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="tab-body">', unsafe_allow_html=True)
    if st.session_state.get("active_tab") == "task":
        show_flash()
        st.session_state["active_tab"] = None

    today_ts4 = pd.Timestamp(date.today())

    col_tl, col_tr = st.columns([2, 1])

    with col_tl:
        st.markdown('<p class="section-title">Filter</p>', unsafe_allow_html=True)
        tf1, tf2, tf3, tf4f = st.columns(4)
        with tf1:
            t_sel_team = st.multiselect("Team", options=TASK_TEAMS, default=[], key="tf_team")
        with tf2:
            t_sel_task = st.multiselect("Task Type", options=TASK_TYPES, default=[], key="tf_task")
        with tf3:
            t_sel_sev = st.multiselect("Severity", options=SEVERITIES, default=[], key="tf_sev")
        with tf4f:
            t_sel_stat = st.multiselect("Status", options=STATUSES, default=[], key="tf_stat")

        filt_task = df_task.copy()
        if t_sel_team:  filt_task = filt_task[filt_task["team"].isin(t_sel_team)]
        if t_sel_task:  filt_task = filt_task[filt_task["task"].isin(t_sel_task)]
        if t_sel_sev:   filt_task = filt_task[filt_task["severity"].isin(t_sel_sev)]
        if t_sel_stat:  filt_task = filt_task[filt_task["status"].isin(t_sel_stat)]

        if not filt_task.empty:
            filt_task = filt_task.copy()
            filt_task["_sort_key"] = filt_task["due_date"].fillna(pd.Timestamp("2099-01-01"))
            filt_task = filt_task.sort_values("_sort_key")

        task_title_col, task_export_col = st.columns([3, 1])
        with task_title_col:
            st.markdown('<p class="section-title">Task Reminders</p>', unsafe_allow_html=True)
        with task_export_col:
            if not filt_task.empty:
                exp_task = filt_task.drop(columns=["_sort_key"], errors="ignore").copy()
                exp_task["due_date"] = pd.to_datetime(exp_task["due_date"], errors="coerce").dt.strftime("%d-%m-%Y")
                st.download_button(
                    "📤 Export",
                    data=exp_task.to_csv(index=False).encode(),
                    file_name=f"DELTA_OPS_tasks_{date.today().strftime('%d%m%Y')}.csv",
                    mime="text/csv",
                    key="export_task_filtered",
                    use_container_width=True,
                )

        if filt_task.empty:
            st.markdown('<div class="alert-bar alert-info">No tasks match current filters. Add one using the form →</div>', unsafe_allow_html=True)
        else:
            def render_task_cards(df_group):
                today_d = date.today()
                for _, row in df_group.iterrows():
                    due        = row["due_date"]
                    due_str    = due.strftime("%d %b %Y") if pd.notna(due) else "—"
                    is_closed  = str(row["status"]).strip().lower() == "closed"
                    is_overdue = pd.notna(due) and due.date() < today_d and not is_closed
                    is_today   = pd.notna(due) and due.date() == today_d and not is_closed

                    if is_closed:
                        card_cls = "task-card done"
                    elif is_overdue:
                        card_cls = "task-card overdue"
                    elif is_today:
                        card_cls = "task-card due-today"
                    else:
                        card_cls = "task-card"

                    if is_overdue:
                        urgency = '<span class="task-badge overdue-badge">OVERDUE</span>'
                    elif is_today:
                        urgency = '<span class="task-badge today-badge">DUE TODAY</span>'
                    else:
                        days_left = (due.date() - today_d).days if pd.notna(due) else None
                        if days_left is not None and 0 < days_left <= 3 and not is_closed:
                            urgency = f'<span class="task-badge today-badge">DUE IN {days_left}D</span>'
                        else:
                            urgency = ""

                    sev_cls    = {"High": "high", "Medium": "medium", "Low": "low"}.get(str(row["severity"]), "low")
                    status_cls = {"Open": "open", "In Progress": "inprogress", "Closed": "closed"}.get(str(row["status"]), "closed")

                    # Safely escape all user data
                    desc      = _html.escape(str(row["issue_description"]))
                    team      = _html.escape(str(row["team"]))
                    task_type = _html.escape(str(row["task"]))
                    sev_lbl   = _html.escape(str(row["severity"]))
                    stat_lbl  = _html.escape(str(row["status"]))

                    card = (
                        f'<div class="{card_cls}">'
                        f'<div class="task-card-title">{desc}</div>'
                        f'<div class="task-card-meta">'
                        f'<span class="card-team">{team}</span>'
                        f'<span class="task-badge">{task_type}</span>'
                        f'<span class="card-meta-item">&#128197;&nbsp;Due:&nbsp;{due_str}</span>'
                        f'<span class="pill pill-{sev_cls}">{sev_lbl}</span>'
                        f'<span class="pill pill-{status_cls}">{stat_lbl}</span>'
                        f'{urgency}'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card, unsafe_allow_html=True)

            # ── Grouped expand/collapse by status (same pattern as circular) ──
            for status_label, default_open in [("Open", True), ("In Progress", True), ("Closed", False)]:
                group = filt_task[filt_task["status"] == status_label].copy()
                if "_sort_key" in group.columns:
                    group = group.sort_values("_sort_key")
                if group.empty:
                    continue
                label = f"{status_label}  ({len(group)})"
                with st.expander(label, expanded=default_open):
                    render_task_cards(group)

        # ── Delete section ─────────────────────────────────────────────────────
        if not df_task.empty:
            st.markdown('<p class="section-title" style="margin-top:24px">Delete Tasks</p>', unsafe_allow_html=True)
            task_delete_options = {
                f"[{i}] {row['team']} | {str(row['issue_description'])[:50]} | {row['status']}": i
                for i, row in df_task.iterrows()
            }
            tasks_to_delete = st.multiselect(
                "Select task(s) to delete (multi-select supported)",
                options=list(task_delete_options.keys()),
                key="task_delete_select"
            )
            if tasks_to_delete:
                if st.button("🗑 DELETE SELECTED TASKS", key="task_delete_btn", use_container_width=True):
                    indices_to_drop = [task_delete_options[k] for k in tasks_to_delete]
                    st.session_state["task_data"] = df_task.drop(index=indices_to_drop).reset_index(drop=True)
                    save_task(st.session_state["task_data"])
                    st.session_state["flash"] = ("success", f"{len(indices_to_drop)} task(s) deleted.")
                    st.session_state["active_tab"] = "task"
                    st.rerun()



    with col_tr:
        st.markdown('<p class="section-title">Add Task Reminder</p>', unsafe_allow_html=True)

        t_team = st.selectbox("Team", TASK_TEAMS, key="t_team")
        t_desc = st.text_area("Description", height=80, key="t_desc",
                               placeholder="What needs to be done...")
        t_due  = st.date_input("Due Date", value=date.today(), key="t_due")
        t_type = st.selectbox("Task Type", TASK_TYPES, key="t_type")
        t_sev  = st.selectbox("Severity", SEVERITIES, key="t_sev")
        t_stat = st.selectbox("Status", STATUSES, key="t_stat")

        if st.button("ADD TASK", key="task_add_btn"):
            if t_desc.strip():
                new_task = {
                    "team":              t_team,
                    "issue_description": t_desc.strip(),
                    "due_date":          pd.Timestamp(t_due),
                    "task":              t_type,
                    "severity":          t_sev,
                    "status":            t_stat,
                }
                st.session_state["task_data"] = pd.concat(
                    [st.session_state["task_data"], pd.DataFrame([new_task])],
                    ignore_index=True
                )
                save_task(st.session_state["task_data"])
                st.session_state["flash"] = ("success", "Task reminder added.")
                st.session_state["active_tab"] = "task"
                st.rerun()
            else:
                st.error("Description cannot be empty.")

        if not df_task.empty:
            st.markdown('<p class="section-title" style="margin-top:24px">Update Task Status</p>', unsafe_allow_html=True)
            task_descs = df_task["issue_description"].str[:50].tolist()
            sel_task_desc = st.selectbox("Select Task", task_descs, key="upd_task_desc")
            new_task_status = st.selectbox("New Status", STATUSES, key="upd_task_stat")
            if st.button("UPDATE", key="upd_task_btn"):
                idx = df_task[df_task["issue_description"].str[:50] == sel_task_desc].index
                if len(idx) > 0:
                    st.session_state["task_data"].loc[idx[0], "status"] = new_task_status
                    save_task(st.session_state["task_data"])
                    st.session_state["flash"] = ("success", "Task status updated.")
                    st.session_state["active_tab"] = "task"
                    st.rerun()

        st.markdown("""
        <div class="bulk-panel bulk-panel-task">
            <div class="bulk-step"><b style="color:#ff9933">BULK UPLOAD</b> &middot; Task Reminders CSV</div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-title" style="margin-top:4px">Step 1 &mdash; Download Template</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:11px; color:#4a6080; margin-bottom:8px; font-family:'IBM Plex Mono',monospace;">
            <span style="color:#ff9933">Required columns:</span>
            team &middot; issue_description &middot; Due Date &middot; Task &middot; severity &middot; status<br>
            <span style="color:#4a6080">team: DP | BROKING | EAGLE | COMPLIANCE<br>
            severity: High | Medium | Low &nbsp;&middot;&nbsp; status: Open | In Progress | Closed<br>
            Date format: DD-MM-YYYY or YYYY-MM-DD</span>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "Download Task Template",
            data=make_task_template(),
            file_name="DELTA_OPS_task_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_task_tmpl"
        )

        st.markdown('<p class="section-title" style="margin-top:16px">Step 2 &mdash; Upload CSV</p>', unsafe_allow_html=True)

        uploaded_task = st.file_uploader(
            "Upload Task Reminders CSV",
            type=["csv"],
            key="bulk_task_upload",
        )

        if uploaded_task is not None:
            task_file_key = f"task_imported_{uploaded_task.name}_{uploaded_task.size}"
            try:
                raw_task = pd.read_csv(uploaded_task)
                st.markdown(
                    f'<div class="upload-result upload-ok">File: <b>{uploaded_task.name}</b> &nbsp;&middot;&nbsp; '
                    f'<b>{len(raw_task)}</b> rows detected</div>',
                    unsafe_allow_html=True
                )

                with st.expander("Preview uploaded rows", expanded=False):
                    st.dataframe(raw_task.head(10), use_container_width=True)

                clean_task, errs_task = validate_task_bulk(raw_task)

                if errs_task:
                    for e in errs_task:
                        st.markdown(f'<div class="upload-result upload-err">Error: {e}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="upload-result upload-warn">No data saved. Fix errors and re-upload.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="upload-result upload-ok">Validation passed: '
                        f'<b>{len(clean_task)}</b> tasks ready to import</div>',
                        unsafe_allow_html=True
                    )

                    with st.expander("Preview validated data", expanded=False):
                        st.dataframe(clean_task, use_container_width=True)

                    st.markdown('<p class="section-title" style="margin-top:12px">Step 3 &mdash; Import Mode</p>', unsafe_allow_html=True)

                    task_mode = st.radio(
                        "Import mode",
                        ["Append - add to existing", "Replace - clear all and import fresh"],
                        key="task_import_mode",
                        index=0
                    )

                    if "Replace" in task_mode:
                        st.markdown('<div class="upload-result upload-warn">Replace will permanently delete ALL current task data.</div>', unsafe_allow_html=True)

                    already_imported_task = st.session_state.get(task_file_key, False)
                    if already_imported_task:
                        st.markdown('<div class="upload-result upload-ok">This file has already been imported. Upload a new file to import again.</div>', unsafe_allow_html=True)
                    else:
                        if st.button("CONFIRM IMPORT", key="task_confirm_import", use_container_width=True):
                            existing_task = st.session_state["task_data"]
                            if "Replace" in task_mode:
                                merged_task = clean_task.copy()
                            else:
                                merged_task = pd.concat([existing_task, clean_task], ignore_index=True)
                            st.session_state["task_data"] = merged_task
                            save_task(merged_task)
                            st.session_state[task_file_key] = True
                            st.session_state["flash"] = (
                                "success",
                                f"{len(clean_task)} tasks imported ({'replaced' if 'Replace' in task_mode else 'appended'}). Total: {len(merged_task)} rows."
                            )
                            st.session_state["active_tab"] = "task"
                            st.rerun()

            except Exception as e:
                st.markdown(f'<div class="upload-result upload-err">Cannot read file: {e}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
