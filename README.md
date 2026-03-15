# Alpha Insight — 0DTE SPY Theta Scalper

Dashboard for 0DTE SPY credit spread trading in the last 90 minutes of the US session.

## Features

- **Pre-Trade Briefing** — Live VIX/SPY data, bias detection, macro notes
- **Strike Helper** — Bull Put / Bear Call spread calculator with entry verdict
- **Trade Calculator** — Theta decay table (sqrt-of-time model), stop-loss, countdowns
- **Trade Log** — Full trade journal with statistics and scaling phase tracking
- **Strategy Playbook** — Complete strategy reference in Polish

## Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/alpha-insight-dashboard.git
cd alpha-insight-dashboard

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Opens at `http://localhost:8501`

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **"New app"**
5. Select your repository, branch (`main`), and set **Main file path** to `app.py`
6. Click **"Deploy"**

The app will be live at `https://YOUR_APP_NAME.streamlit.app`

### Important notes for Streamlit Cloud

- `trades.json` is **not persistent** on Streamlit Cloud (ephemeral filesystem). Use the JSON export/import buttons in the Trade Log section to save your data locally.
- `.streamlit/config.toml` is included for the dark theme — it will be picked up automatically.
- Data refreshes every 30 seconds via `streamlit-autorefresh`.
- Market data comes from Yahoo Finance via `yfinance` (no API key needed).

## Quick GitHub Setup (from terminal)

```bash
cd streamlit-dashboard

git init
git add .
git commit -m "Initial commit: Alpha Insight 0DTE dashboard"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/alpha-insight-dashboard.git
git branch -M main
git push -u origin main
```

## File Structure

```
streamlit-dashboard/
  app.py                   # Main Streamlit application
  requirements.txt         # Python dependencies
  .streamlit/
    config.toml            # Dark theme configuration
  .gitignore               # Git ignore rules
  README.md                # This file
```
