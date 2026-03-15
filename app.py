import streamlit as st
import yfinance as yf
import pandas as pd
import json
import math
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Alpha Insight — 0DTE SPY Theta Scalper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ET = ZoneInfo("America/New_York")
TRADES_FILE = "trades.json"


# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* ── Force dark theme on entire app ── */
    .stApp {
        background-color: #0a1628 !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Force all text to light color */
    .stApp p, .stApp span, .stApp li, .stApp td, .stApp th, .stApp label,
    .stApp .stMarkdown, .stApp div {
        color: #e2e8f0;
    }

    /* ── Expander sections ── */
    [data-testid="stExpander"] {
        background: #132137 !important;
        border: 1px solid #2d3e56 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] details {
        background: #132137 !important;
    }
    [data-testid="stExpander"] summary {
        color: #e2e8f0 !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p {
        color: #e2e8f0 !important;
    }
    /* Expander body content */
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #132137 !important;
    }

    /* ── Header bar ── */
    .header-bar {
        background: #0d1b2e;
        border-bottom: 1px solid #2d3e56;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 1rem -1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .header-bar h1 {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0;
        line-height: 1.2;
    }
    .header-bar .subtitle {
        font-size: 0.75rem;
        color: #64748b;
    }
    .clock {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        font-variant-numeric: tabular-nums;
        text-align: right;
    }
    .clock-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: right;
    }

    /* ── Badges ── */
    .badge-green { background: rgba(16,185,129,0.15); color: #10b981 !important; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
    .badge-red { background: rgba(239,68,68,0.15); color: #ef4444 !important; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
    .badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b !important; padding: 3px 10px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }

    /* ── Alert banners ── */
    .alert-banner {
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }
    .alert-green { background: rgba(16,185,129,0.12); color: #10b981 !important; border-left: 4px solid #10b981; }
    .alert-red { background: rgba(239,68,68,0.12); color: #ef4444 !important; border-left: 4px solid #ef4444; }
    .alert-yellow { background: rgba(245,158,11,0.12); color: #f59e0b !important; border-left: 4px solid #f59e0b; }
    .alert-grey { background: rgba(100,116,139,0.12); color: #94a3b8 !important; border-left: 4px solid #64748b; }

    /* ── Stop loss display ── */
    .stop-loss-box {
        text-align: center;
        padding: 16px;
        background: rgba(239,68,68,0.1);
        border: 2px solid #ef4444;
        border-radius: 6px;
        margin: 12px 0;
    }
    .stop-loss-box .sl-label { font-size: 0.8rem; color: #64748b !important; text-transform: uppercase; }
    .stop-loss-box .sl-value { font-size: 2rem; font-weight: 700; color: #ef4444 !important; }

    /* ── Verdict boxes ── */
    .verdict-enter {
        background: rgba(16,185,129,0.15); color: #10b981 !important; border: 2px solid #10b981;
        padding: 12px; border-radius: 6px; text-align: center; font-weight: 700; font-size: 1.1rem;
    }
    .verdict-no {
        background: rgba(239,68,68,0.15); color: #ef4444 !important; border: 2px solid #ef4444;
        padding: 12px; border-radius: 6px; text-align: center; font-weight: 700; font-size: 1.1rem;
    }

    /* ── Phase banner ── */
    .phase-banner {
        padding: 10px 16px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;
        margin-bottom: 12px; border-left: 4px solid #2d3e56; background: rgba(45,62,86,0.2); color: #e2e8f0 !important;
    }
    .phase-paused {
        border-left-color: #ef4444 !important; background: rgba(239,68,68,0.12) !important; color: #ef4444 !important;
    }

    /* ── Timer boxes ── */
    .timer-box {
        background: #0a1628; border: 1px solid #2d3e56; border-radius: 6px;
        padding: 12px; text-align: center;
    }
    .timer-label { font-size: 0.72rem; color: #64748b !important; text-transform: uppercase; margin-bottom: 4px; }
    .timer-value { font-size: 1.5rem; font-weight: 700; font-variant-numeric: tabular-nums; color: #e2e8f0 !important; }

    /* ── Highlight boxes for playbook ── */
    .highlight-box {
        background: #0a1628; border: 1px solid #2d3e56; border-radius: 6px;
        padding: 12px 16px; margin: 12px 0; font-size: 0.85rem; color: #94a3b8 !important;
    }
    .highlight-box strong { color: #e2e8f0 !important; }
    .highlight-box li { color: #94a3b8 !important; }
    .highlight-box.info { border-left: 4px solid #2563eb; }
    .highlight-box.warn { border-left: 4px solid #f59e0b; }
    .highlight-box.danger { border-left: 4px solid #ef4444; }

    /* ── Metric cards (VIX, SPY, BIAS, etc.) ── */
    [data-testid="stMetric"] {
        background: #0a1628 !important;
        border: 1px solid #2d3e56 !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] label,
    [data-testid="stMetricLabel"] span {
        color: #64748b !important;
    }
    [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #94a3b8 !important;
    }

    /* ── Form inputs ── */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: #0a1628 !important;
        color: #e2e8f0 !important;
        border-color: #2d3e56 !important;
    }
    .stSelectbox > div > div {
        background: #0a1628 !important;
        color: #e2e8f0 !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label, .stCheckbox label {
        color: #94a3b8 !important;
    }

    /* ── Buttons ── */
    .stButton button {
        background: #1e3a5f !important;
        color: #e2e8f0 !important;
        border: 1px solid #2d3e56 !important;
    }
    .stButton button:hover {
        background: #2563eb !important;
        border-color: #2563eb !important;
    }
    .stFormSubmitButton button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* ── Tables / DataFrames ── */
    .stDataFrame { font-variant-numeric: tabular-nums; }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: #0a1628 !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: #2d3e56 !important;
    }

    /* ── Streamlit info/success/error boxes ── */
    .stAlert {
        background: #132137 !important;
        color: #e2e8f0 !important;
    }

    /* ── Captions ── */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }
    [data-testid="stCaptionContainer"] p {
        color: #64748b !important;
    }

    /* ── Markdown tables inside expanders ── */
    [data-testid="stExpander"] table {
        background: #0a1628 !important;
    }
    [data-testid="stExpander"] table th {
        background: #1e3a5f !important;
        color: #e2e8f0 !important;
        border-color: #2d3e56 !important;
    }
    [data-testid="stExpander"] table td {
        background: #0a1628 !important;
        color: #e2e8f0 !important;
        border-color: #2d3e56 !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        color: #94a3b8 !important;
    }
    [data-testid="stFileUploader"] section {
        background: #0a1628 !important;
        border-color: #2d3e56 !important;
    }

    /* ── Download button ── */
    .stDownloadButton button {
        background: #1e3a5f !important;
        color: #e2e8f0 !important;
        border: 1px solid #2d3e56 !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# TIME HELPERS
# ──────────────────────────────────────────────
def get_et_now():
    return datetime.now(ET)


def get_et_date_str():
    return get_et_now().strftime("%Y-%m-%d")


def minutes_until_et(hour, minute):
    now = get_et_now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    diff = (target - now).total_seconds() / 60
    return diff


def format_countdown(total_minutes):
    if total_minutes <= 0:
        return "00:00"
    mins = int(total_minutes)
    secs = int((total_minutes - mins) * 60)
    return f"{mins:02d}:{secs:02d}"


# ──────────────────────────────────────────────
# DATA FETCHING
# ──────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_market_data():
    """Fetch VIX and SPY data from Yahoo Finance. Cached for 30 seconds."""
    result = {"vix": None, "spy": None, "spy_prev": None, "error": None, "timestamp": None, "market_time": None}
    try:
        spy = yf.Ticker("SPY")
        spy_info = spy.fast_info
        result["spy"] = round(spy_info.last_price, 2)
        result["spy_prev"] = round(spy_info.previous_close, 2)

        vix = yf.Ticker("^VIX")
        vix_info = vix.fast_info
        result["vix"] = round(vix_info.last_price, 2)

        result["timestamp"] = get_et_now().strftime("%d.%m.%Y %H:%M:%S ET")
        result["market_time"] = spy_info.last_price  # timestamp approximation
    except Exception as e:
        result["error"] = str(e)
    return result


# ──────────────────────────────────────────────
# TRADE LOG PERSISTENCE
# ──────────────────────────────────────────────
def get_trades_path():
    return os.path.join(os.path.dirname(__file__), TRADES_FILE)


def load_trades():
    if "trades" not in st.session_state:
        path = get_trades_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    st.session_state.trades = json.load(f)
            except (json.JSONDecodeError, IOError):
                st.session_state.trades = []
        else:
            st.session_state.trades = []
    return st.session_state.trades


def save_trades(trades):
    st.session_state.trades = trades
    try:
        path = get_trades_path()
        with open(path, "w") as f:
            json.dump(trades, f, indent=2)
    except IOError:
        pass


# ──────────────────────────────────────────────
# MACRO NOTES PERSISTENCE
# ──────────────────────────────────────────────
def get_macro_notes():
    today = get_et_date_str()
    if "macro_date" not in st.session_state or st.session_state.macro_date != today:
        st.session_state.macro_date = today
        st.session_state.macro_text = ""
    return st.session_state.macro_text


# ──────────────────────────────────────────────
# VIX STATUS LOGIC
# ──────────────────────────────────────────────
def get_vix_status(vix):
    if vix < 14:
        return "red", "NIE TRADUJ DZIS — VIX < 14 (premia zbyt niska)", "ZA NISKI"
    elif vix <= 26:
        return "green", "MOZNA TRADOWAC", "OK"
    elif vix <= 30:
        return "yellow", "UWAGA — strefa ostrzegawcza, redukuj rozmiar pozycji", "UWAGA"
    else:
        return "red", "NIE TRADUJ DZIS — VIX > 30", "ZA WYSOKI"


# ──────────────────────────────────────────────
# SCALING PHASE LOGIC
# ──────────────────────────────────────────────
def get_scaling_phase(trades):
    total = len(trades)
    if total == 0:
        return 1, "Phase 1 — Learning | Max 1 kontrakt", False

    # PAUSED check
    if total >= 20:
        last20 = trades[-20:]
        wr20 = sum(1 for t in last20 if t["pnlTotal"] > 0) / len(last20)
        if wr20 < 0.70:
            return 0, "STRATEGIA WSTRZYMANA — WYMAGANA ANALIZA (win rate < 70% z ostatnich 20)", True

    # Phase 4
    if total >= 40:
        last40 = trades[-40:]
        wr40 = sum(1 for t in last40 if t["pnlTotal"] > 0) / len(last40)
        if wr40 >= 0.75:
            return 4, f"Phase 4 — Full | Max 10 kontraktow | WR40: {wr40*100:.1f}%", False

    # Phase 3
    if total >= 20:
        last20 = trades[-20:]
        wr20 = sum(1 for t in last20 if t["pnlTotal"] > 0) / len(last20)
        if wr20 >= 0.70:
            return 3, f"Phase 3 — Scaling | Max 5 kontraktow | WR20: {wr20*100:.1f}%", False

    # Phase 2 — consecutive wins
    consecutive = 0
    for t in reversed(trades):
        if t["pnlTotal"] > 0:
            consecutive += 1
        else:
            break
    if consecutive >= 3:
        return 2, f"Phase 2 — Confirming | Max 2 kontrakty | {consecutive} winow z rzedu", False

    return 1, "Phase 1 — Learning | Max 1 kontrakt", False


# ──────────────────────────────────────────────
# THETA DECAY TABLE
# ──────────────────────────────────────────────
def build_decay_table(credit, entry_minutes, contracts):
    close_minutes = 15 * 60 + 50  # 15:50
    total_minutes = close_minutes - entry_minutes
    if total_minutes <= 0:
        return pd.DataFrame()

    rows = []
    cumulative_pnl = 0

    t = entry_minutes
    while t < close_minutes:
        block_end = min(t + 15, close_minutes)
        mins_remaining_start = close_minutes - t
        mins_remaining_end = close_minutes - block_end

        prem_start = credit * math.sqrt(mins_remaining_start / total_minutes)
        prem_end = credit * math.sqrt(mins_remaining_end / total_minutes) if mins_remaining_end > 0 else 0

        decay_block = prem_start - prem_end
        cumulative_pnl += decay_block * 100 * contracts

        t_h, t_m = divmod(t, 60)
        e_h, e_m = divmod(block_end, 60)
        time_label = f"{t_h:02d}:{t_m:02d} → {e_h:02d}:{e_m:02d}"

        rows.append({
            "Blok czasu": time_label,
            "Premium": f"${prem_end:.3f}",
            "Decay w bloku": f"+${decay_block:.3f}",
            "P&L skum. ($)": f"+${cumulative_pnl:.0f}",
        })
        t += 15

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# HEADER WITH CLOCK
# ──────────────────────────────────────────────
now_et = get_et_now()
clock_str = now_et.strftime("%H:%M:%S")

st.markdown(f"""
<div class="header-bar">
    <div>
        <h1>Alpha Insight</h1>
        <span class="subtitle">0DTE SPY Theta Scalper</span>
    </div>
    <div>
        <div class="clock">{clock_str}</div>
        <div class="clock-label">Eastern Time</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 30 seconds
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, limit=None, key="auto_refresh")
except ImportError:
    pass

# ──────────────────────────────────────────────
# TIME ALERTS
# ──────────────────────────────────────────────
et_mins = now_et.hour * 60 + now_et.minute
if et_mins >= 960:  # 16:00
    st.markdown('<div class="alert-banner alert-grey">Sesja zakonczona</div>', unsafe_allow_html=True)
elif et_mins >= 950:  # 15:50
    st.markdown('<div class="alert-banner alert-red">HARD CLOSE — BADZ FLAT TERAZ</div>', unsafe_allow_html=True)
elif et_mins >= 945:  # 15:45
    st.markdown('<div class="alert-banner alert-yellow">ZACZNIJ ZAMYKAC — 5 MINUT DO HARD CLOSE</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SECTION 1 — PRE-TRADE BRIEFING
# ══════════════════════════════════════════════
with st.expander("**1. Pre-Trade Briefing**", expanded=True):
    col_refresh, col_ts = st.columns([1, 3])
    with col_refresh:
        if st.button("Odswiez", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()

    data = fetch_market_data()

    with col_ts:
        if data["timestamp"]:
            st.caption(f"Ostatnie odswiezenie: {data['timestamp']}")
        else:
            st.caption("Brak danych")

    if data["error"]:
        st.error("Blad pobierania danych — sprawdz polaczenie")

    # VIX Banner
    if data["vix"] is not None:
        vix_color, vix_text, vix_badge = get_vix_status(data["vix"])
        st.markdown(f'<div class="alert-banner alert-{vix_color}">{vix_text}</div>', unsafe_allow_html=True)

    # Info cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if data["vix"] is not None:
            vix_color, _, vix_badge = get_vix_status(data["vix"])
            st.metric("VIX", f"{data['vix']:.2f}")
            st.markdown(f'<span class="badge-{vix_color}">{vix_badge}</span>', unsafe_allow_html=True)
        else:
            st.metric("VIX", "--")

    with c2:
        if data["spy"] is not None:
            st.metric("SPY", f"${data['spy']:.2f}")
        else:
            st.metric("SPY", "--")

    with c3:
        if data["spy"] is not None and data["spy_prev"] is not None:
            if data["spy"] > data["spy_prev"]:
                st.metric("Bias", "BULLISH")
                st.markdown('<span class="badge-green">BULLISH BIAS</span>', unsafe_allow_html=True)
            else:
                st.metric("Bias", "BEARISH")
                st.markdown('<span class="badge-red">BEARISH BIAS</span>', unsafe_allow_html=True)
        else:
            st.metric("Bias", "--")

    with c4:
        if data["spy"] is not None and data["spy_prev"] is not None:
            if data["spy"] > data["spy_prev"]:
                st.metric("Rekomendacja", "Bull Put Spread")
            else:
                st.metric("Rekomendacja", "Bear Call Spread")
        else:
            st.metric("Rekomendacja", "--")

    # Macro notes
    st.markdown("---")
    macro_val = get_macro_notes()
    new_macro = st.text_area(
        "Notatki makro (czysci sie nastepnego dnia)",
        value=macro_val,
        placeholder="Wpisz eventy makro na dzis (Fed, CPI, FOMC...)",
        key="macro_input",
    )
    if new_macro != st.session_state.get("macro_text", ""):
        st.session_state.macro_text = new_macro


# ══════════════════════════════════════════════
# SECTION 2 — STRIKE HELPER
# ══════════════════════════════════════════════
with st.expander("**2. Strike Helper**"):
    spy_prefill = data["spy"] if data["spy"] is not None else 0.0
    spy_input = st.number_input("SPY cena (z sekcji 1)", value=spy_prefill, step=0.01, key="sh_spy")

    put_col, call_col = st.columns(2)

    # PUT PANEL
    with put_col:
        st.markdown("#### Bull Put Spread")
        pc1, pc2 = st.columns(2)
        with pc1:
            put_short = st.number_input("Short put strike", value=0.0, step=1.0, key="put_short")
        with pc2:
            put_long_default = put_short - 1 if put_short > 0 else 0.0
            put_long = st.number_input("Long put strike", value=put_long_default, step=1.0, key="put_long")

        pc3, pc4 = st.columns(2)
        with pc3:
            put_bid = st.number_input("Short put BID", value=0.0, step=0.01, key="put_bid", format="%.2f")
        with pc4:
            put_ask = st.number_input("Short put ASK", value=0.0, step=0.01, key="put_ask", format="%.2f")

        pc5, pc6 = st.columns(2)
        with pc5:
            put_long_ask = st.number_input("Long put ASK", value=0.0, step=0.01, key="put_long_ask", format="%.2f")
        with pc6:
            put_delta = st.number_input("Short put DELTA", value=0.0, step=0.01, key="put_delta", format="%.2f")

        if st.button("Oblicz", key="calc_put"):
            if put_bid > 0 and put_long_ask >= 0 and put_delta > 0:
                net_credit = put_bid - put_long_ask
                ba_spread = put_ask - put_bid
                spread_width = abs(put_short - put_long)
                max_risk = (spread_width - max(net_credit, 0)) * 100

                credit_ok = round(net_credit * 100) >= 30
                spread_ok = round(ba_spread * 100) <= 3
                delta_ok = 0.08 <= put_delta <= 0.12
                enter = credit_ok and spread_ok and delta_ok

                st.markdown(f"**Net Credit:** {'🟢' if credit_ok else '🔴'} ${net_credit:.2f}")
                st.markdown(f"**Bid/Ask Spread:** {'✓' if spread_ok else '⚠️'} ${ba_spread:.2f}")
                st.markdown(f"**Delta:** {'🟢' if delta_ok else '⚠️'} {put_delta:.2f}")
                st.markdown(f"**Spread Width:** ${spread_width:.2f}")
                st.markdown(f"**Max Risk / spread:** :red[${max_risk:.0f}]")

                if enter:
                    st.markdown('<div class="verdict-enter">WCHODZIC</div>', unsafe_allow_html=True)
                else:
                    reasons = []
                    if not credit_ok:
                        reasons.append("credit < $0.30")
                    if not delta_ok:
                        reasons.append("delta poza 0.08-0.12")
                    if not spread_ok:
                        reasons.append("bid/ask > $0.03")
                    st.markdown(f'<div class="verdict-no">NIE WCHODZIC — {", ".join(reasons)}</div>', unsafe_allow_html=True)

    # CALL PANEL
    with call_col:
        st.markdown("#### Bear Call Spread")
        cc1, cc2 = st.columns(2)
        with cc1:
            call_short = st.number_input("Short call strike", value=0.0, step=1.0, key="call_short")
        with cc2:
            call_long_default = call_short + 1 if call_short > 0 else 0.0
            call_long = st.number_input("Long call strike", value=call_long_default, step=1.0, key="call_long")

        cc3, cc4 = st.columns(2)
        with cc3:
            call_bid = st.number_input("Short call BID", value=0.0, step=0.01, key="call_bid", format="%.2f")
        with cc4:
            call_ask = st.number_input("Short call ASK", value=0.0, step=0.01, key="call_ask", format="%.2f")

        cc5, cc6 = st.columns(2)
        with cc5:
            call_long_ask = st.number_input("Long call ASK", value=0.0, step=0.01, key="call_long_ask", format="%.2f")
        with cc6:
            call_delta = st.number_input("Short call DELTA", value=0.0, step=0.01, key="call_delta", format="%.2f")

        if st.button("Oblicz", key="calc_call"):
            if call_bid > 0 and call_long_ask >= 0 and call_delta > 0:
                net_credit = call_bid - call_long_ask
                ba_spread = call_ask - call_bid
                spread_width = abs(call_long - call_short)
                max_risk = (spread_width - max(net_credit, 0)) * 100

                credit_ok = round(net_credit * 100) >= 30
                spread_ok = round(ba_spread * 100) <= 3
                delta_ok = 0.08 <= call_delta <= 0.12
                enter = credit_ok and spread_ok and delta_ok

                st.markdown(f"**Net Credit:** {'🟢' if credit_ok else '🔴'} ${net_credit:.2f}")
                st.markdown(f"**Bid/Ask Spread:** {'✓' if spread_ok else '⚠️'} ${ba_spread:.2f}")
                st.markdown(f"**Delta:** {'🟢' if delta_ok else '⚠️'} {call_delta:.2f}")
                st.markdown(f"**Spread Width:** ${spread_width:.2f}")
                st.markdown(f"**Max Risk / spread:** :red[${max_risk:.0f}]")

                if enter:
                    st.markdown('<div class="verdict-enter">WCHODZIC</div>', unsafe_allow_html=True)
                else:
                    reasons = []
                    if not credit_ok:
                        reasons.append("credit < $0.30")
                    if not delta_ok:
                        reasons.append("delta poza 0.08-0.12")
                    if not spread_ok:
                        reasons.append("bid/ask > $0.03")
                    st.markdown(f'<div class="verdict-no">NIE WCHODZIC — {", ".join(reasons)}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# SECTION 3 — TRADE CALCULATOR
# ══════════════════════════════════════════════
with st.expander("**3. Trade Calculator**"):
    tc1, tc2, tc3 = st.columns(3)
    entry_times = {"2:30 PM": "14:30", "2:35 PM": "14:35", "2:40 PM": "14:40",
                   "2:45 PM": "14:45", "2:50 PM": "14:50", "2:55 PM": "14:55", "3:00 PM": "15:00"}

    with tc1:
        entry_label = st.selectbox("Entry time (ET)", list(entry_times.keys()), key="calc_entry")
    with tc2:
        calc_credit = st.number_input("Credit collected", value=0.0, step=0.01, key="calc_credit", format="%.2f")
    with tc3:
        calc_direction = st.selectbox("Spread direction", ["Bull Put Spread", "Bear Call Spread"], key="calc_dir")

    tc4, tc5 = st.columns(2)
    with tc4:
        calc_strike = st.number_input("Strike sold", value=0.0, step=1.0, key="calc_strike")
    with tc5:
        calc_contracts = st.number_input("Kontrakty (1-10)", min_value=1, max_value=10, value=1, key="calc_contracts")

    if st.button("Oblicz", key="calc_trade"):
        if calc_credit > 0:
            entry_str = entry_times[entry_label]
            entry_parts = entry_str.split(":")
            entry_minutes = int(entry_parts[0]) * 60 + int(entry_parts[1])

            # Stop-loss
            stop_loss = calc_credit * 1.5
            st.markdown(f"""
            <div class="stop-loss-box">
                <div class="sl-label">Stop-Loss Trigger (1.5x)</div>
                <div class="sl-value">${stop_loss:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Countdown timers
            t1, t2 = st.columns(2)
            entry_remaining = minutes_until_et(15, 0)
            close_remaining = minutes_until_et(15, 50)

            with t1:
                if entry_remaining <= 0:
                    st.markdown("""<div class="timer-box"><div class="timer-label">Do deadline wejscia 3:00 PM</div>
                    <div class="timer-value" style="color:#ef4444">ZAMKNIETY</div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="timer-box"><div class="timer-label">Do deadline wejscia 3:00 PM</div>
                    <div class="timer-value">{format_countdown(entry_remaining)}</div></div>""", unsafe_allow_html=True)

            with t2:
                if close_remaining <= 0:
                    st.markdown("""<div class="timer-box"><div class="timer-label">Do hard close 3:50 PM</div>
                    <div class="timer-value" style="color:#ef4444">00:00</div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="timer-box"><div class="timer-label">Do hard close 3:50 PM</div>
                    <div class="timer-value">{format_countdown(close_remaining)}</div></div>""", unsafe_allow_html=True)

            # Decay table
            df = build_decay_table(calc_credit, entry_minutes, calc_contracts)
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# SECTION 4 — TRADE LOG
# ══════════════════════════════════════════════
with st.expander("**4. Trade Log**"):
    trades = load_trades()

    # Phase banner
    phase, phase_text, is_paused = get_scaling_phase(trades)
    phase_class = "phase-banner phase-paused" if is_paused else "phase-banner"
    st.markdown(f'<div class="{phase_class}">{phase_text}</div>', unsafe_allow_html=True)

    # Statistics
    if trades:
        total = len(trades)
        last20 = trades[-20:]
        wins20 = sum(1 for t in last20 if t["pnlTotal"] > 0)
        wr20 = (wins20 / len(last20)) * 100 if last20 else 0
        stops = sum(1 for t in trades if t.get("stopLoss", False))
        avg_credit = sum(t["credit"] for t in trades) / total
        avg_pnl = sum(t["pnlTotal"] for t in trades) / total

        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            st.metric("Trades", total)
        with s2:
            st.metric("Win Rate (ost. 20)", f"{wr20:.1f}%")
        with s3:
            st.metric("Stop-Losses", stops)
        with s4:
            st.metric("Avg Credit", f"${avg_credit:.2f}")
        with s5:
            st.metric("Avg P&L", f"${avg_pnl:+.0f}")

    # Add trade form
    st.markdown("#### Dodaj trade")
    with st.form("add_trade_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            log_date = st.text_input("Data", value=get_et_date_str(), key="log_date")
        with f2:
            log_entry = st.selectbox("Entry time (ET)", list(entry_times.keys()), key="log_entry")
        with f3:
            log_dir = st.selectbox("Typ spreadu", ["Bull Put Spread", "Bear Call Spread"], key="log_dir")

        f4, f5, f6 = st.columns(3)
        with f4:
            log_strike = st.number_input("Strike sold", value=0.0, step=1.0, key="log_strike")
        with f5:
            log_credit = st.number_input("Credit collected", value=0.0, step=0.01, key="log_credit", format="%.2f")
        with f6:
            log_contracts = st.number_input("Kontrakty", min_value=1, max_value=10, value=1, key="log_contracts")

        f7, f8 = st.columns(2)
        with f7:
            log_exit_time = st.text_input("Exit time (HH:MM)", placeholder="15:45", key="log_exit_time")
        with f8:
            log_exit_price = st.number_input("Exit price", value=0.0, step=0.01, key="log_exit_price", format="%.2f")

        log_stoploss = st.checkbox("Stop-loss uruchomiony (1.5x trigger trafiony)", key="log_sl")
        log_notes = st.text_area("Notes", placeholder="Opcjonalne notatki...", key="log_notes")

        submitted = st.form_submit_button("Zapisz trade", type="primary")
        if submitted:
            if log_strike > 0 and log_credit > 0:
                pnl_spread = log_credit - log_exit_price
                pnl_total = pnl_spread * 100 * log_contracts
                direction = "bull_put" if log_dir == "Bull Put Spread" else "bear_call"

                new_trade = {
                    "id": f"t_{int(datetime.now().timestamp() * 1000)}",
                    "date": log_date,
                    "entryTime": entry_times[log_entry],
                    "direction": direction,
                    "strike": log_strike,
                    "contracts": log_contracts,
                    "credit": log_credit,
                    "exitTime": log_exit_time,
                    "exitPrice": log_exit_price,
                    "stopLoss": log_stoploss,
                    "notes": log_notes,
                    "pnlSpread": round(pnl_spread, 2),
                    "pnlTotal": round(pnl_total, 2),
                }
                trades.append(new_trade)
                save_trades(trades)
                st.success(f"Trade zapisany! P&L: ${pnl_total:+.0f}")
                st.rerun()
            else:
                st.error("Uzupelnij wymagane pola (strike, credit)")

    # Trade table
    if trades:
        display_trades = []
        for t in reversed(trades):
            dir_label = "Bull Put" if t["direction"] == "bull_put" else "Bear Call"
            display_trades.append({
                "Data": t["date"],
                "Entry": t["entryTime"],
                "Typ": dir_label,
                "Strike": t["strike"],
                "Kontr.": t["contracts"],
                "Credit": f"${t['credit']:.2f}",
                "Exit": t.get("exitTime", "--"),
                "Exit Price": f"${t['exitPrice']:.2f}",
                "P&L": f"${t['pnlSpread']:+.2f}",
                "P&L ($)": f"${t['pnlTotal']:+.0f}",
                "Stop?": "TAK" if t.get("stopLoss") else "--",
                "Notes": t.get("notes", ""),
            })

        df_trades = pd.DataFrame(display_trades)
        st.dataframe(df_trades, use_container_width=True, hide_index=True)

        # Delete trade
        st.markdown("---")
        trade_ids = [f"{t['date']} {t['entryTime']} {t['direction']} strike:{t['strike']}" for t in reversed(trades)]
        del_selection = st.selectbox("Wybierz trade do usuniecia", ["--"] + trade_ids, key="del_trade")
        if st.button("Usun trade", key="del_btn") and del_selection != "--":
            idx = trade_ids.index(del_selection)
            real_idx = len(trades) - 1 - idx
            trades.pop(real_idx)
            save_trades(trades)
            st.rerun()

        # Export
        st.download_button(
            "Eksportuj logi (JSON)",
            data=json.dumps(trades, indent=2),
            file_name="alpha_insight_trades.json",
            mime="application/json",
        )

    else:
        st.info("Brak zapisanych tradow")

    # Import trades
    uploaded = st.file_uploader("Importuj logi (JSON)", type=["json"], key="import_trades")
    if uploaded is not None:
        try:
            imported = json.load(uploaded)
            if isinstance(imported, list):
                save_trades(imported)
                st.success(f"Zaimportowano {len(imported)} tradow")
                st.rerun()
        except (json.JSONDecodeError, Exception) as e:
            st.error(f"Blad importu: {e}")


# ══════════════════════════════════════════════
# SECTION 5 — STRATEGY PLAYBOOK
# ══════════════════════════════════════════════
with st.expander("**5. Playbook Strategii**"):
    st.markdown("### Czym jest ta strategia?")
    st.markdown("""
    Sprzedajesz **credit spready 0DTE na SPY** (opcje wygasajace tego samego dnia) w ostatnich
    **90 minutach sesji** (14:30 – 16:00 ET). Zbierasz premie, ktora przyspiesza zanik (theta decay)
    w kierunku zera, gdy zbliza sie zamkniecie rynku.
    """)

    st.markdown("""
    <div class="highlight-box info">
        <strong>Dlaczego ostatnie 90 minut?</strong> Theta decay nie jest liniowy — przyspiesza wykladniczo.
        Ostatnie 90 minut odpowiada za 40–60% calodziennego zaniku premii. Sprzedajesz na najstromszym
        odcinku krzywej zaniku, zbierajac 2–3x wiecej theta niz sprzedawca poranny, bez ryzyka overnight/gap.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Jaki spread i kiedy?")
    st.markdown("""
    | Warunek | Akcja |
    |---------|-------|
    | SPY > previousClose | :green[**Bull Put Spread**] (sprzedaj put, kup put nizej) |
    | SPY < previousClose | :red[**Bear Call Spread**] (sprzedaj call, kup call wyzej) |

    - **Okno wejscia:** 14:30 – 15:00 ET. Nigdy nie otwieraj pozycji po 15:00.
    - **Short strike delta:** 0.08 – 0.12 (daleko OTM, ok. 1% od ceny SPY)
    - **Spread width:** $1 (short − long = 1 strike)
    - **Minimalny credit:** $0.30 (nie wchodzisz ponizej)
    - **Bid/ask spread:** max $0.03 na short leg (plynnosc)
    """)

    st.markdown("### Checklist przed wejsciem")
    st.markdown("""
    1. VIX w strefie 14–26? (Zielona strefa w Sekcji 1)
    2. Brak eventow makro w ciagu najblizszych 30 minut? (Fed, CPI, FOMC)
    3. SPY trend bias sprawdzony? (Sekcja 1)
    4. Strike wybrany z delta 0.08–0.12?
    5. Credit >= $0.30? Bid/ask <= $0.03?
    6. Position size zgodny z faza skalowania?
    7. Stop-loss ustawiony mentalnie na 1.5x credit?
    """)

    st.markdown("### Minuta po minucie — Timeline")
    st.markdown("""
    | Czas (ET) | Co robisz |
    |-----------|-----------|
    | **14:25** | Odswiez dashboard. Sprawdz VIX, SPY bias, eventy makro. Otworz TWS, przygotuj order. |
    | **14:30 – 14:45** | Szukaj optymalnego entry. Wpisz dane ze Strike Helpera (Sekcja 2). Jesli "WCHODZIC" — wykonaj trade w TWS. |
    | **14:45 – 15:00** | Ostatnia szansa na wejscie. Jesli nie ma dobrego setupu — nie wchodz. |
    | **15:00** | :red[DEADLINE] — koniec okna wejscia. Zadnych nowych pozycji. |
    | **15:00 – 15:45** | Monitoruj pozycje. Theta decay pracuje. Sprawdzaj tabele zaniku (Sekcja 3). |
    | **15:45** | :orange[ZACZNIJ ZAMYKAC] — 5 minut do hard close. Skladaj zlecenie zamkniecia. |
    | **15:50** | :red[HARD CLOSE] — badz flat. Zamknij wszystko po rynku jesli trzeba. |
    | **15:50 – 16:00** | Zapisz trade w logu (Sekcja 4). Przeanalizuj wynik. |
    """)

    st.markdown("### Zarzadzanie ryzykiem")
    st.markdown("""
    <div class="highlight-box danger">
        <strong>Stop-Loss: 1.5x zebranego creditu</strong><br>
        Jesli zebrales $0.40 — zamykasz pozycje gdy koszt zamkniecia osiagnie $0.60.
        BEZ WYJATKOW. Nigdy nie przesuwaj stop-lossa. Nigdy nie "czekaj na powrot".
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    | Regula | Szczegoly |
    |--------|-----------|
    | **Stop-loss** | 1.5x credit zebranego. Jesli credit = $0.40, zamknij przy $0.60. |
    | **Max dzienna strata** | 2x max zysk z jednego trade'a. Po osiagnieciu — koniec na dzis. |
    | **3 straty z rzedu** | Przerwa minimum 2 dni tradingowe. Analiza logow przed powrotem. |
    | **Hard close** | 15:50 ET. Badz flat. Bez wyjatkow. |
    """)

    st.markdown("### Gamma — Twoj wrog")
    st.markdown("""
    <div class="highlight-box warn">
        <strong>Gamma na 0DTE jest ekstremalnie wysokie.</strong> Przy delta 0.10 na short strike,
        ruch SPY o 1% w strone Twojego strike'a moze zmienic delta z 0.10 na 0.40–0.50 w ciagu minut.
        Po 15:30 ruch $0.90 na SPY moze calkowicie odwrocic zyskowna pozycje w &lt;5 minut.
        Dlatego dyscyplina position size jest kluczowa.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Kiedy tradowac, kiedy odpuscic")
    st.markdown("""
    | VIX | Akcja |
    |-----|-------|
    | :red[< 14] | NIE TRADUJ — premia zbyt niska |
    | :green[14 – 26] | ZIELONA STREFA — traduj normalnie |
    | :orange[26 – 30] | UWAGA — redukuj rozmiar pozycji o 50% |
    | :red[> 30] | NIE TRADUJ — za duza zmiennosc |

    **Dni bez tradingu:** FOMC decision day, CPI/NFP w ciagu 30 min przed Twoim oknem,
    triple witching, dzien po spadku >2% na SPY.
    """)

    st.markdown("### Model zaniku theta (Square Root of Time)")
    st.markdown("""
    <div class="highlight-box info">
        <strong>Wzor:</strong> remaining_premium(t) = credit × √(minutes_remaining / total_minutes)<br><br>
        Gdzie total_minutes = minuty od wejscia do 15:50 ET. Zanik NIE jest liniowy — ostatnie bloki
        15-minutowe maja 40–50% wiecej zaniku niz pierwsze. To jest Twoja przewaga matematyczna.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Fazy skalowania")
    st.markdown("""
    | Faza | Warunek | Max kontraktow |
    |------|---------|----------------|
    | **Phase 1 — Learning** | Start / <3 winy z rzedu | **1** |
    | **Phase 2 — Confirming** | 3+ winy z rzedu | **2** |
    | **Phase 3 — Scaling** | >=70% win rate (ost. 20 tradow) | **5** |
    | **Phase 4 — Full** | >=75% win rate (ost. 40 tradow) | **10** |
    | :red[**PAUSED**] | Win rate <70% po 20+ tradach | :red[**0 — STOP**] |
    """)

    st.markdown("### Oczekiwane wyniki")
    st.markdown("""
    Przy $0.40 credit, 2 kontraktach, 70% win rate, $0.20 avg win, $0.19 avg loss:
    - **EV na trade:** ~$17
    - **20 tradow/miesiac:** ~$340/miesiac (Phase 2)
    - **Phase 4 (10 kontraktow):** ~$1,700/miesiac

    To sa konserwatywne szacunki. Realna wariancja bedzie znaczna.
    Priorytet: nauka strategii, nie pogon za zyskami.
    """)

    st.markdown("### Najwieksze bledy 0DTE sellerow")
    st.markdown("""
    <div class="highlight-box danger">
        <ul>
            <li><strong>Przesuwanie stop-lossa</strong> — "jeszcze chwile" zamienia mala strate w katastrofe</li>
            <li><strong>Overtrading</strong> — wiecej tradow ≠ wiecej zysku. 1 dobry setup dziennie wystarczy.</li>
            <li><strong>Skalowanie za wczesnie</strong> — 2 winy nie oznaczaja, ze strategia dziala.</li>
            <li><strong>Trading przy wysokim VIX</strong> — gamma Cie zabije. VIX >30 = dzien wolny.</li>
            <li><strong>Brak logowania tradow</strong> — bez danych zgadujesz. Log jest najwazniejszym narzedziem.</li>
            <li><strong>Trzymanie pozycji po 15:50</strong> — gamma ryzyko rosnie eksponencjalnie. Badz flat.</li>
            <li><strong>Trading na eventach makro</strong> — FOMC/CPI = rosyjska ruletka. Odpusc.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <p style="text-align:center; color:#64748b; font-style:italic;">
        Sprzedaj spread. Respektuj stop. Zamknij do 15:50. Loguj wszystko. Skaluj gdy dane na to pozwalaja.
    </p>
    """, unsafe_allow_html=True)
