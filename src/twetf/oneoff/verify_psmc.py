#!/usr/bin/env python3
"""Quick PSMC anomaly check — inspect raw TWSE quarterly fields and compare to Yahoo Finance."""
import requests, json, time
import yfinance as yf

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

print("=== TWSE t187ap14_L raw fields for PSMC (6770) ===")
data = requests.get("https://openapi.twse.com.tw/v1/opendata/t187ap14_L", headers=HEADERS, timeout=25).json()
psmc = next((r for r in data if r.get("公司代號") == "6770"), None)
if psmc:
    for k, v in psmc.items():
        print(f"  {k}: {v}")
else:
    print("  Not found!")

print("\n=== Yahoo Finance PSMC quarterly financials (last 4Q) ===")
t = yf.Ticker("6770.TW")
qf = t.quarterly_financials
if qf is not None and not qf.empty:
    for col in list(qf.columns)[-4:]:
        rev = qf.loc["Total Revenue"][col] if "Total Revenue" in qf.index else "N/A"
        op  = qf.loc["Operating Income"][col] if "Operating Income" in qf.index else "N/A"
        net = qf.loc["Net Income"][col] if "Net Income" in qf.index else "N/A"
        print(f"  {col}: Rev={rev:,.0f} Op={op:,.0f} Net={net:,.0f}" if isinstance(rev, float) else f"  {col}: no data")
else:
    print("  No data returned")

print("\n=== Cross-check TSMC (2330) — known good anchor ===")
tsmc = next((r for r in data if r.get("公司代號") == "2330"), None)
if tsmc:
    print(f"  年度: {tsmc.get('年度')} | 季別: {tsmc.get('季別')}")
    print(f"  EPS: {tsmc.get('基本每股盈餘(元)')}")
    print(f"  Revenue: {tsmc.get('營業收入')}")
