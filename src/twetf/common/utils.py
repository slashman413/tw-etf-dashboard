#!/usr/bin/env python3
"""Shared utilities for all Taiwan market data scripts."""
from twetf.paths import CONFIG_PATH, REPORTS_DIR
import json
from pathlib import Path
from datetime import datetime

# HTTP client (TWSE/TPEx SSL bypass, headers) and number parsing live in the
# shared slashman-finance-utils package; re-exported under the old names.
from slashman_finance import fetch_json
from slashman_finance import to_float as sf
from slashman_finance.http import TWSE_SSL_CTX as CTX, DEFAULT_HEADERS as HEADERS

def latest_report_dir(base=REPORTS_DIR, require="grand_unified.json"):
    """Return the most recent dated report directory that contains `require`."""
    dirs = sorted(
        [d for d in Path(base).iterdir()
         if d.is_dir() and d.name[:4].isdigit() and (d / require).exists()],
        reverse=True,
    )
    if dirs:
        return dirs[0]
    # Fallback: any dated dir, newest first
    all_dirs = sorted(
        [d for d in Path(base).iterdir() if d.is_dir() and d.name[:4].isdigit()],
        reverse=True,
    )
    if all_dirs:
        return all_dirs[0]
    today = datetime.now().strftime("%Y-%m-%d")
    p = Path(base) / today
    p.mkdir(parents=True, exist_ok=True)
    return p

def today_report_dir(base=REPORTS_DIR):
    """Return (and create) today's report directory."""
    today = datetime.now().strftime("%Y-%m-%d")
    p = Path(base) / today
    p.mkdir(parents=True, exist_ok=True)
    return p

def load_config(path=CONFIG_PATH):
    cfg_path = Path(path)
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    return {}
