#!/usr/bin/env python3
"""Shared utilities for all Taiwan market data scripts."""
import json, ssl, urllib.request
from pathlib import Path
from datetime import datetime

# ── Shared SSL context (bypass self-signed certs on TWSE/TPEX) ──────────────
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None

def latest_report_dir(base="reports", require="grand_unified.json"):
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

def today_report_dir(base="reports"):
    """Return (and create) today's report directory."""
    today = datetime.now().strftime("%Y-%m-%d")
    p = Path(base) / today
    p.mkdir(parents=True, exist_ok=True)
    return p

def load_config(path="config.json"):
    cfg_path = Path(path)
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    return {}
