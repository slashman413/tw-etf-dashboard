#!/usr/bin/env python3
"""
Build a StatementDog-style HTML dashboard from analysis JSON files.
Run: python build_dashboard.py
Output: dashboard.html (open in browser)
"""

import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

# ── Load data ─────────────────────────────────────────────────────────────────
composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
margin    = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
tech      = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))
portfolio  = json.loads((REPORT_DIR / "portfolio_data.json").read_text(encoding="utf-8"))
riskdata   = json.loads((REPORT_DIR / "risk_data.json").read_text(encoding="utf-8"))
ptargets   = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
etfconc    = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
divsustain = json.loads((REPORT_DIR / "dividend_sustainability.json").read_text(encoding="utf-8"))
convdata   = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))
aprdata    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
rebdata    = json.loads((REPORT_DIR / "etf_rebalance.json").read_text(encoding="utf-8"))
tradedata  = json.loads((REPORT_DIR / "trade_setups.json").read_text(encoding="utf-8"))
chaindata  = json.loads((REPORT_DIR / "ai_chain.json").read_text(encoding="utf-8"))
bwibbu2    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
momentum   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
marefresh  = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
dnasignals = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
granddata  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
backtest   = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
rsdata     = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
portopt    = json.loads((REPORT_DIR / "portfolio_optimizer.json").read_text(encoding="utf-8"))
sectordata  = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))
watchalerts = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))
maypreview    = json.loads((REPORT_DIR / "may_preview.json").read_text(encoding="utf-8"))
triplereports = json.loads((REPORT_DIR / "triple_reports.json").read_text(encoding="utf-8"))
etfcomp       = json.loads((REPORT_DIR / "etf_comparison.json").read_text(encoding="utf-8"))
catalyst_cal  = json.loads((REPORT_DIR / "catalyst_calendar.json").read_text(encoding="utf-8"))
sensitivity   = json.loads((REPORT_DIR / "score_sensitivity.json").read_text(encoding="utf-8"))
peercomp      = json.loads((REPORT_DIR / "peer_comparison.json").read_text(encoding="utf-8"))
earningsq     = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))
mondayplan    = json.loads((REPORT_DIR / "monday_plan.json").read_text(encoding="utf-8"))
possize       = json.loads((REPORT_DIR / "position_sizing.json").read_text(encoding="utf-8"))
secrotation   = json.loads((REPORT_DIR / "sector_rotation.json").read_text(encoding="utf-8"))
premarket     = json.loads((REPORT_DIR / "premarket_checklist.json").read_text(encoding="utf-8"))
scenarioa     = json.loads((REPORT_DIR / "scenario_analysis.json").read_text(encoding="utf-8"))
divincome     = json.loads((REPORT_DIR / "dividend_income.json").read_text(encoding="utf-8"))
instflows_raw = (REPORT_DIR / "institutional_flows.json")
instflows     = json.loads(instflows_raw.read_text(encoding="utf-8")) if instflows_raw.exists() else {}
smartmoney_raw = (REPORT_DIR / "smart_money_confluence.json")
smartmoney     = json.loads(smartmoney_raw.read_text(encoding="utf-8")) if smartmoney_raw.exists() else {}
q2fcst_raw     = (REPORT_DIR / "q2_eps_forecast.json")
q2fcst         = json.loads(q2fcst_raw.read_text(encoding="utf-8")) if q2fcst_raw.exists() else {}
actionsig_raw  = (REPORT_DIR / "action_signal.json")
actionsig      = json.loads(actionsig_raw.read_text(encoding="utf-8")) if actionsig_raw.exists() else {}
dnatrig_raw    = (REPORT_DIR / "dna_trigger_calc.json")
dnatrig        = json.loads(dnatrig_raw.read_text(encoding="utf-8")) if dnatrig_raw.exists() else {}
mos_raw        = (REPORT_DIR / "margin_of_safety.json")
mosdata        = json.loads(mos_raw.read_text(encoding="utf-8")) if mos_raw.exists() else {}
conviction_raw = (REPORT_DIR / "conviction_matrix.json")
conviction     = json.loads(conviction_raw.read_text(encoding="utf-8")) if conviction_raw.exists() else {}
secmacro_raw   = (REPORT_DIR / "sector_revenue_macro.json")
secmacro       = json.loads(secmacro_raw.read_text(encoding="utf-8")) if secmacro_raw.exists() else {}
fullmkt_raw    = (REPORT_DIR / "full_market.json")
fullmkt        = json.loads(fullmkt_raw.read_text(encoding="utf-8")) if fullmkt_raw.exists() else {}
etf4q_raw      = (REPORT_DIR / "etf_4q_report.json")
etf4q          = json.loads(etf4q_raw.read_text(encoding="utf-8")) if etf4q_raw.exists() else {}
trail_raw      = (REPORT_DIR / "trail_eps_estimates.json")
trail_data     = json.loads(trail_raw.read_text(encoding="utf-8")) if trail_raw.exists() else {}
otcanalysis_raw = (REPORT_DIR / "otc_analysis.json")
otcanalysis     = json.loads(otcanalysis_raw.read_text(encoding="utf-8")) if otcanalysis_raw.exists() else {}
dnafull_raw     = (REPORT_DIR / "dna_full_market.json")
dnafull_data    = json.loads(dnafull_raw.read_text(encoding="utf-8")) if dnafull_raw.exists() else {}
sop_bt_raw      = (REPORT_DIR / "backtest_sop_results.json")
sop_bt_data     = json.loads(sop_bt_raw.read_text(encoding="utf-8")) if sop_bt_raw.exists() else {}
taiex_raw       = Path(__file__).parent / "taiex_ohlc.json"
taiex_data      = json.loads(taiex_raw.read_text(encoding="utf-8")) if taiex_raw.exists() else {}
taiex_monthly_raw  = Path(__file__).parent / "taiex_monthly.json"
taiex_monthly_data = json.loads(taiex_monthly_raw.read_text(encoding="utf-8")) if taiex_monthly_raw.exists() else {}
taiex_capital_raw  = Path(__file__).parent / "taiex_capital.json"
taiex_capital_data = json.loads(taiex_capital_raw.read_text(encoding="utf-8")) if taiex_capital_raw.exists() else {}
import base64 as _b64
_qr_path = Path(__file__).parent / "donate_qr.png"
DONATE_QR_B64 = "data:image/png;base64," + _b64.b64encode(_qr_path.read_bytes()).decode() if _qr_path.exists() else ""
_pay_qr_path = Path(__file__).parent / "payment_qr.png"
PAYMENT_QR_B64 = "data:image/png;base64," + _b64.b64encode(_pay_qr_path.read_bytes()).decode() if _pay_qr_path.exists() else ""
# Extract series_map for separate file (avoids bloating dashboard.html)
_series_map     = dnafull_data.pop("series_map", {})
# Merge expansion OHLCV (stocks not in DNA bull-market universe) so K-line works for all dashboard stocks
_exp_ohlcv_path = Path(__file__).parent / "expansion_ohlcv.json"
if _exp_ohlcv_path.exists():
    _exp_ohlcv = json.loads(_exp_ohlcv_path.read_text(encoding="utf-8"))
    added = 0
    for code, data in _exp_ohlcv.items():
        if code not in _series_map:
            _series_map[code] = data
            added += 1
    if added:
        print(f"  series_map: merged {added} expansion stocks from expansion_ohlcv.json")
_sm_out         = Path(__file__).parent / "series_map.json"
_sm_out.write_text(json.dumps(_series_map, ensure_ascii=False), encoding="utf-8")
print(f"  series_map.json: {len(_series_map)} stocks → {_sm_out.stat().st_size//1024} KB")
exportmanifest_raw = (REPORT_DIR / "export_manifest.json")
exportmanifest = json.loads(exportmanifest_raw.read_text(encoding="utf-8")) if exportmanifest_raw.exists() else {}
# Add weekly digest to manifest if not already there
_digest_entry = {"name":"WEEKLY_DIGEST.html","rows":62,"cols":1,"desc":"自含式週報 — 可列印/分享，無需伺服器"}
if exportmanifest.get("files") and not any(f["name"]=="WEEKLY_DIGEST.html" for f in exportmanifest["files"]):
    exportmanifest["files"].insert(0, _digest_entry)

# Load per-stock report files generated by generate_stock_reports.py
stocks_dir = REPORT_DIR / "stocks"
stock_reports = []
if stocks_dir.exists():
    for f in sorted(stocks_dir.glob("*_report.json")):
        try:
            stock_reports.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass

# Derive display date from price_momentum data_date (ROC → Gregorian)
_mom_roc = momentum.get("data_date", "")
if _mom_roc and len(_mom_roc) == 7 and _mom_roc[:3].isdigit():
    PRICE_DATE = f"{int(_mom_roc[:3])+1911}-{_mom_roc[3:5]}-{_mom_roc[5:]}"
else:
    PRICE_DATE = TODAY

# Derive bwibbu valuation date
_bw_roc = str(bwibbu2.get("data_date", ""))
if _bw_roc and len(_bw_roc) == 7 and _bw_roc[:3].isdigit():
    BWIBBU_DATE = f"{int(_bw_roc[:3])+1911}-{_bw_roc[3:5]}-{_bw_roc[5:]}"
else:
    BWIBBU_DATE = PRICE_DATE

# Compute next revenue publication date dynamically
from datetime import timedelta as _td
_rev_ref = datetime.strptime(TODAY, "%Y-%m-%d")
_rev_d = _rev_ref.replace(day=10) if _rev_ref.day < 10 else (_rev_ref.replace(day=28) + _td(days=4)).replace(day=10)
while _rev_d.weekday() >= 5:
    _rev_d += _td(days=1)
REVENUE_DATE = _rev_d.strftime("%Y-%m-%d")
_rev_month = (_rev_d.replace(day=1) - _td(days=1))
REVENUE_MONTH_LABEL = f"{_rev_month.month}月"

# Build lookup maps
mom_price_map = {s["code"]: s.get("close") for s in momentum.get("all_momentum", [])}

# Merge composite + margin into master stock list
stocks = []
for s in composite:
    code = s["code"]
    m = margin.get(code, {})
    entry = {
        "code":       code,
        "name":       s["name"],
        "sector":     s.get("sector", "—"),
        "score":      s.get("score"),
        "verdict":    s.get("verdict", "—"),
        "fwd_pe":     s.get("fwd_pe"),
        "pb":         s.get("pb"),
        "div":        s.get("div_yield"),
        "q1_eps":     s.get("q1_eps"),
        "rev_yoy":    s.get("rev_yoy"),
        "op_margin":  s.get("op_margin"),
        "price":      s.get("price"),
        "eps_accel":  s.get("eps_accel"),
        "v_pts":      s.get("v_pts", 0),
        "g_pts":      s.get("g_pts", 0),
        "q_pts":      s.get("q_pts", 0),
        "i_pts":      s.get("i_pts", 0),
        "margin_sig": m.get("sig", "N/A"),
        "m_chg":      m.get("m_chg"),
        "s_chg":      m.get("s_chg"),
        "m_today":    m.get("m_today"),
        "s_today":    m.get("s_today"),
        "source":     "0050",
    }
    stocks.append(entry)

# Add expansion stocks (not in 0050)
for s in expansion:
    code = s["code"]
    m = margin.get(code, {})
    # Skip if already in main universe
    if any(x["code"] == code for x in stocks):
        continue
    entry = {
        "code":       code,
        "name":       s["name"],
        "sector":     "Financial" if s.get("is_fin") else "Various",
        "score":      None,
        "verdict":    s.get("conv", "WATCH"),
        "fwd_pe":     s.get("pe"),
        "pb":         s.get("pb"),
        "div":        s.get("div"),
        "q1_eps":     s.get("eps"),
        "rev_yoy":    s.get("yoy"),
        "op_margin":  s.get("op_margin"),
        "price":      s.get("price") or mom_price_map.get(code),
        "eps_accel":  None,
        "v_pts":      None,
        "g_pts":      None,
        "q_pts":      None,
        "i_pts":      None,
        "margin_sig": m.get("sig", "N/A"),
        "m_chg":      m.get("m_chg"),
        "s_chg":      m.get("s_chg"),
        "m_today":    m.get("m_today"),
        "s_today":    m.get("s_today"),
        "source":     "+".join(s.get("etfs", [])),
    }
    stocks.append(entry)

# Compute stats
scored = [s for s in stocks if s["score"] is not None]
buys   = [s for s in scored if s["verdict"] in ("STRONG BUY", "BUY")]
avg_score = sum(s["score"] for s in scored) / len(scored) if scored else 0
bullish_margin = sum(1 for s in stocks if s["margin_sig"] == "BULLISH")
bearish_margin = sum(1 for s in stocks if s["margin_sig"] == "BEARISH")

# Market movers (hardcoded from DASHBOARD.md data)
top_decliners = [
    {"code": "2327", "name": "國巨 Yageo", "chg": -9.39, "score": 68},
    {"code": "2376", "name": "技嘉 Gigabyte", "chg": -6.27, "score": 77},
    {"code": "2317", "name": "鴻海 Foxconn", "chg": -5.18, "score": 72},
    {"code": "2357", "name": "華碩 ASUS", "chg": -4.19, "score": 70},
    {"code": "2303", "name": "聯電 UMC", "chg": -4.21, "score": 60},
    {"code": "3711", "name": "日月光 ASE", "chg": -4.05, "score": 60},
]
top_gainers = [
    {"code": "2882", "name": "國泰金 Cathay", "chg": 2.83},
    {"code": "2892", "name": "第一金 First", "chg": 1.90},
    {"code": "2395", "name": "研華 Advantech", "chg": 1.75},
]

# Sector averages
sector_map = {}
for s in scored:
    sec = s["sector"]
    sector_map.setdefault(sec, []).append(s["score"])
sector_avgs = sorted(
    [{"sector": k, "avg": sum(v)/len(v), "count": len(v)} for k, v in sector_map.items()],
    key=lambda x: -x["avg"]
)

stocks_json    = json.dumps(stocks,          ensure_ascii=False)
movers_json    = json.dumps(top_decliners,  ensure_ascii=False)
gainers_json   = json.dumps(top_gainers,    ensure_ascii=False)
sectors_json   = json.dumps(sector_avgs,    ensure_ascii=False)
tech_json      = json.dumps(tech,           ensure_ascii=False)
portfolio_json = json.dumps(portfolio,      ensure_ascii=False)
riskdata_json  = json.dumps(riskdata,       ensure_ascii=False)
ptargets_json  = json.dumps(ptargets,       ensure_ascii=False)
etfconc_json   = json.dumps(etfconc,        ensure_ascii=False)
divsustain_json= json.dumps(divsustain,     ensure_ascii=False)
convdata_json  = json.dumps(convdata,       ensure_ascii=False)
aprdata_json   = json.dumps(aprdata,        ensure_ascii=False)
rebdata_json   = json.dumps(rebdata,        ensure_ascii=False)
tradedata_json = json.dumps(tradedata,      ensure_ascii=False)
chaindata_json = json.dumps(chaindata,      ensure_ascii=False)
bwibbu2_json   = json.dumps(bwibbu2,        ensure_ascii=False)
momentum_json  = json.dumps(momentum,       ensure_ascii=False)
marefresh_json = json.dumps(marefresh,     ensure_ascii=False)
dnasignals_json= json.dumps(dnasignals,    ensure_ascii=False)
granddata_json = json.dumps(granddata,     ensure_ascii=False)
backtest_json  = json.dumps(backtest,      ensure_ascii=False)
rsdata_json    = json.dumps(rsdata,        ensure_ascii=False)
portopt_json   = json.dumps(portopt,       ensure_ascii=False)
sectordata_json  = json.dumps(sectordata,    ensure_ascii=False)
watchalerts_json = json.dumps(watchalerts,  ensure_ascii=False)
maypreview_json    = json.dumps(maypreview,     ensure_ascii=False)
triplereports_json = json.dumps(triplereports, ensure_ascii=False)
etfcomp_json       = json.dumps(etfcomp,       ensure_ascii=False)
stockreports_json  = json.dumps(stock_reports, ensure_ascii=False)
catalyst_json      = json.dumps(catalyst_cal,  ensure_ascii=False)
sensitivity_json   = json.dumps(sensitivity,   ensure_ascii=False)
peercomp_json      = json.dumps(peercomp,      ensure_ascii=False)
earningsq_json     = json.dumps(earningsq,     ensure_ascii=False)
mondayplan_json    = json.dumps(mondayplan,    ensure_ascii=False)
possize_json       = json.dumps(possize,       ensure_ascii=False)
secrotation_json   = json.dumps(secrotation,   ensure_ascii=False)
premarket_json     = json.dumps(premarket,     ensure_ascii=False)
scenarioa_json     = json.dumps(scenarioa,     ensure_ascii=False)
divincome_json     = json.dumps(divincome,     ensure_ascii=False)
instflows_json     = json.dumps(instflows,     ensure_ascii=False)
smartmoney_json    = json.dumps(smartmoney,    ensure_ascii=False)
q2fcst_json        = json.dumps(q2fcst,        ensure_ascii=False)
actionsig_json     = json.dumps(actionsig,     ensure_ascii=False)
dnatrig_json       = json.dumps(dnatrig,       ensure_ascii=False)
mosdata_json       = json.dumps(mosdata,       ensure_ascii=False)
conviction_json    = json.dumps(conviction,    ensure_ascii=False)
secmacro_json      = json.dumps(secmacro,      ensure_ascii=False)
fullmkt_json       = json.dumps(fullmkt,        ensure_ascii=False)
etf4q_json         = json.dumps(etf4q,          ensure_ascii=False)
trail_json         = json.dumps(trail_data,      ensure_ascii=False)
otcanalysis_json   = json.dumps(otcanalysis,     ensure_ascii=False)
dnafull_json       = json.dumps(dnafull_data,   ensure_ascii=False)
sop_bt_json        = json.dumps(sop_bt_data,    ensure_ascii=False)
taiex_json         = json.dumps(taiex_data,        ensure_ascii=False)
taiex_monthly_json = json.dumps(taiex_monthly_data, ensure_ascii=False)
taiex_capital_json = json.dumps(taiex_capital_data, ensure_ascii=False)
exportmanifest_json= json.dumps(exportmanifest, ensure_ascii=False)

# ── HTML template ──────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>台灣 ETF 分析 Dashboard — {TODAY}</title>
<style>
  /* ── Reset & Base ── */
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans TC', sans-serif;
    background: #f4f6f9;
    color: #1a2332;
    font-size: 14px;
    line-height: 1.5;
  }}
  a {{ text-decoration: none; color: inherit; }}

  /* ── Layout ── */
  .app-header {{
    background: #fff;
    border-bottom: 1px solid #e2e8f0;
    position: sticky; top: 0; z-index: 100;
    padding: 0 24px;
    display: flex; align-items: center; gap: 32px; height: 56px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }}
  .logo {{
    font-size: 18px; font-weight: 700; color: #1a2332;
    display: flex; align-items: center; gap: 8px;
  }}
  .logo-badge {{
    background: #2563eb; color: #fff;
    border-radius: 4px; padding: 2px 7px; font-size: 11px; font-weight: 700;
  }}
  .nav-tabs {{
    display: flex; gap: 2px; flex: 1; align-items: center;
  }}
  .nav-tab {{
    padding: 7px 13px; border-radius: 6px; cursor: pointer;
    font-weight: 500; color: #64748b; transition: all .15s;
    border: none; background: none; font-size: 13px; white-space: nowrap;
  }}
  .nav-tab:hover {{ background: #f1f5f9; color: #1a2332; }}
  .nav-tab.active {{ background: #eff6ff; color: #2563eb; font-weight: 700; }}
  /* Sub-tab navigation within a merged page */
  .sub-tab-bar {{ display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px;padding-bottom:12px;border-bottom:2px solid #e2e8f0; }}
  .sub-tab {{ padding:7px 16px;border:none;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;background:#f1f5f9;color:#475569;transition:all .15s; }}
  .sub-tab.active {{ background:#7c3aed;color:#fff;box-shadow:0 2px 8px rgba(124,58,237,0.3); }}
  .sub-tab:hover:not(.active) {{ background:#e2e8f0;color:#1e293b; }}
  .sub-panel {{ display:none; }}
  .sub-panel.active {{ display:block; }}
  .strat-panel {{ display:none; }}
  .strat-panel.active {{ display:block; }}
  /* ── Dropdown nav groups ── */
  .nav-group {{ position: relative; display: inline-block; }}
  .nav-group-btn {{
    padding: 7px 12px; border-radius: 6px; cursor: pointer;
    font-weight: 600; color: #374151; transition: all .15s;
    border: none; background: none; font-size: 13px;
    display: flex; align-items: center; gap: 3px; white-space: nowrap;
  }}
  .nav-group-btn:hover {{ background: #f1f5f9; color: #1a2332; }}
  .nav-group-btn.active {{ background: #eff6ff; color: #2563eb; }}
  .nav-arrow {{ font-size: 9px; opacity: .6; }}
  .nav-dropdown {{
    display: none; position: absolute; top: calc(100% + 4px); left: 0;
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,.12);
    min-width: 170px; z-index: 300; padding: 6px;
  }}
  .nav-group:hover .nav-dropdown,
  .nav-group.open  .nav-dropdown {{ display: block; }}
  .nav-dropdown .nav-tab {{
    display: block; width: 100%; text-align: left;
    padding: 8px 12px; border-radius: 6px; font-size: 13px;
    color: #374151;
  }}
  .nav-dropdown .nav-tab:hover {{ background: #f8fafc; color: #1a2332; }}
  .nav-dropdown .nav-tab.active {{ background: #eff6ff; color: #2563eb; font-weight: 700; }}
  .nav-sep {{ width: 1px; height: 20px; background: #e2e8f0; margin: 0 2px; }}
  .header-meta {{ font-size: 12px; color: #94a3b8; white-space: nowrap; }}
  /* ── Paywall ── */
  .pw-overlay {{ position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:9999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px); }}
  .pw-modal {{ background:#fff;border-radius:20px;padding:40px 36px;max-width:500px;width:92%;box-shadow:0 20px 60px rgba(0,0,0,.35);text-align:center;position:relative; }}
  .pw-lock-icon {{ font-size:52px;margin-bottom:12px; }}
  .pw-title {{ font-size:22px;font-weight:800;color:#1a2332;margin-bottom:6px; }}
  .pw-price {{ display:inline-block;background:#fef3c7;border:1.5px solid #f59e0b;color:#92400e;font-weight:800;font-size:20px;padding:6px 20px;border-radius:30px;margin:10px 0 16px; }}
  .pw-features {{ text-align:left;background:#f8fafc;border-radius:10px;padding:14px 18px;margin-bottom:20px;font-size:14px;color:#374151;line-height:1.9; }}
  .pw-input {{ width:100%;box-sizing:border-box;padding:12px 16px;border:2px solid #e2e8f0;border-radius:10px;font-size:16px;margin-bottom:10px;outline:none;transition:border .2s; }}
  .pw-input:focus {{ border-color:#2563eb; }}
  .pw-btn {{ width:100%;padding:13px;background:#2563eb;color:#fff;font-size:16px;font-weight:700;border:none;border-radius:10px;cursor:pointer;margin-bottom:8px;transition:background .15s; }}
  .pw-btn:hover {{ background:#1d4ed8; }}
  .pw-btn-close {{ background:none;border:none;color:#94a3b8;font-size:13px;cursor:pointer;text-decoration:underline; }}
  .pw-error {{ color:#dc2626;font-size:13px;margin:4px 0 8px;display:none; }}
  .pw-contact {{ font-size:12px;color:#94a3b8;margin-top:12px; }}
  .pw-nav-lock {{ font-size:10px;opacity:.7;margin-left:3px; }}
  .pw-unlocked-banner {{ font-size:11px;background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:10px;margin-left:6px;font-weight:600; }}

  .main {{ max-width: 1400px; margin: 0 auto; padding: 24px 16px; overflow-x: hidden; }}
  body {{ overflow-x: hidden; }}
  .page {{ display: none; }}
  .page.active {{ display: block; }}
  .two-col-grid {{ display:grid; grid-template-columns:1fr 340px; gap:16px; margin-bottom:20px; }}

  /* ── Alert banner ── */
  .alert-banner {{
    background: linear-gradient(135deg, #fef3c7, #fff7ed);
    border: 1px solid #fbbf24; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 20px;
    display: flex; align-items: flex-start; gap: 12px;
  }}
  .alert-icon {{ font-size: 20px; flex-shrink: 0; }}
  .alert-title {{ font-weight: 700; color: #92400e; font-size: 15px; }}
  .alert-sub {{ color: #78350f; font-size: 13px; margin-top: 2px; }}

  /* ── KPI cards ── */
  .kpi-row {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
    margin-bottom: 20px;
  }}
  @media (max-width: 900px) {{ .kpi-row {{ grid-template-columns: repeat(2, 1fr); }} }}
  .kpi-card {{
    background: #fff; border-radius: 10px; padding: 16px 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
  }}
  .kpi-label {{ font-size: 12px; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }}
  .kpi-value {{ font-size: 28px; font-weight: 700; margin-top: 4px; line-height: 1; }}
  .kpi-sub {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
  .kpi-value.green {{ color: #16a34a; }}
  .kpi-value.red   {{ color: #dc2626; }}
  .kpi-value.blue  {{ color: #2563eb; }}
  .kpi-value.amber {{ color: #d97706; }}

  /* ── Section headings ── */
  .section-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
  }}
  .section-title {{
    font-size: 16px; font-weight: 700; color: #1a2332;
    display: flex; align-items: center; gap: 8px;
  }}
  .section-count {{
    font-size: 12px; background: #f1f5f9; color: #64748b;
    border-radius: 10px; padding: 2px 8px; font-weight: 600;
  }}

  /* ── Card ── */
  .card {{
    background: #fff; border-radius: 10px; border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,.04); margin-bottom: 20px; overflow: hidden;
  }}
  .card-pad {{ padding: 16px 20px; }}

  /* ── Tables ── */
  .tbl-wrap {{ overflow-x: auto; }}
  table {{
    width: 100%; border-collapse: collapse; font-size: 13px;
  }}
  thead th {{
    background: #f8fafc; color: #64748b; font-weight: 600;
    padding: 9px 12px; text-align: left;
    border-bottom: 2px solid #e2e8f0;
    white-space: nowrap; cursor: pointer; user-select: none;
    font-size: 12px; text-transform: uppercase; letter-spacing: .04em;
  }}
  thead th:hover {{ background: #f1f5f9; color: #1a2332; }}
  thead th.sorted-asc::after  {{ content: " ▲"; font-size: 10px; color: #2563eb; }}
  thead th.sorted-desc::after {{ content: " ▼"; font-size: 10px; color: #2563eb; }}
  tbody tr {{ border-bottom: 1px solid #f1f5f9; transition: background .1s; }}
  tbody tr:hover {{ background: #f8fafc; }}
  tbody td {{ padding: 8px 12px; white-space: nowrap; }}
  tbody tr:last-child {{ border-bottom: none; }}

  /* ── Badges ── */
  .badge {{
    display: inline-block; border-radius: 5px; padding: 2px 7px;
    font-size: 11px; font-weight: 700; letter-spacing: .02em;
  }}
  .badge-strong-buy {{ background: #dbeafe; color: #1d4ed8; }}
  .badge-buy        {{ background: #dcfce7; color: #15803d; }}
  .badge-hold       {{ background: #fef9c3; color: #854d0e; }}
  .badge-reduce     {{ background: #fee2e2; color: #b91c1c; }}
  .badge-avoid      {{ background: #4b0082; color: #e9d5ff; }}
  .badge-watch      {{ background: #fff7ed; color: #c2410c; }}
  .badge-psmc       {{ background: #fde8d8; color: #9a3412; }}
  .badge-bullish    {{ background: #d1fae5; color: #065f46; }}
  .badge-bearish    {{ background: #fee2e2; color: #991b1b; }}
  .badge-mixed      {{ background: #e0e7ff; color: #3730a3; }}
  .badge-unwinding  {{ background: #f3f4f6; color: #374151; }}
  .badge-neutral    {{ background: #f3f4f6; color: #6b7280; }}
  .badge-confirmed  {{ background: #14532d; color: #bbf7d0; }}
  .badge-signal     {{ background: #166534; color: #d1fae5; }}
  .badge-divergence {{ background: #7c2d12; color: #fed7aa; }}

  /* ── Score bar ── */
  .score-bar-wrap {{ display: flex; align-items: center; gap: 8px; }}
  .score-num {{ font-weight: 700; min-width: 28px; text-align: right; }}
  .score-bar {{ height: 6px; border-radius: 3px; background: #e2e8f0; flex: 1; min-width: 60px; }}
  .score-fill {{ height: 100%; border-radius: 3px; }}
  .score-fill.s90 {{ background: #1d4ed8; }}
  .score-fill.s70 {{ background: #16a34a; }}
  .score-fill.s50 {{ background: #f59e0b; }}
  .score-fill.s30 {{ background: #dc2626; }}

  /* ── Trend chips ── */
  .trend-accel  {{ color: #15803d; font-weight: 700; }}
  .trend-stable {{ color: #64748b; }}
  .trend-decel  {{ color: #dc2626; }}

  /* ── Pct coloring ── */
  .pos {{ color: #16a34a; font-weight: 600; }}
  .neg {{ color: #dc2626; font-weight: 600; }}

  /* ── Filter bar ── */
  .filter-bar {{
    display: flex; gap: 10px; flex-wrap: wrap; padding: 14px 16px;
    background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  }}
  .filter-bar input, .filter-bar select {{
    border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px;
    font-size: 13px; background: #fff; color: #1a2332; outline: none;
  }}
  .filter-bar input:focus, .filter-bar select:focus {{ border-color: #2563eb; }}
  .filter-bar label {{ font-size: 12px; color: #64748b; align-self: center; }}

  /* ── Movers grid ── */
  .movers-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;
  }}
  @media (max-width: 700px) {{ .movers-grid {{ grid-template-columns: 1fr; }} }}
  .mover-row {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 0; border-bottom: 1px solid #f1f5f9;
  }}
  .mover-row:last-child {{ border-bottom: none; }}
  .mover-code {{ font-weight: 700; font-size: 13px; }}
  .mover-name {{ font-size: 12px; color: #64748b; }}
  .mover-chg  {{ font-weight: 700; font-size: 15px; }}

  /* ── Bar chart ── */
  .bar-chart {{ padding: 12px 0; }}
  .bar-row {{
    display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
  }}
  .bar-label {{ width: 100px; font-size: 13px; text-align: right; color: #475569; }}
  .bar-track {{ flex: 1; background: #f1f5f9; border-radius: 4px; height: 22px; }}
  .bar-fill {{
    height: 100%; border-radius: 4px;
    display: flex; align-items: center; padding-left: 8px;
    font-size: 12px; font-weight: 700; color: #fff; white-space: nowrap;
    transition: width .4s;
  }}
  .bar-count {{ font-size: 12px; color: #94a3b8; width: 40px; }}

  /* ── Score breakdown mini-chart ── */
  .score-breakdown {{
    display: flex; gap: 2px; height: 8px; border-radius: 4px; overflow: hidden;
    min-width: 80px;
  }}
  .score-v {{ background: #3b82f6; }}
  .score-g {{ background: #22c55e; }}
  .score-q {{ background: #a855f7; }}
  .score-i {{ background: #f59e0b; }}

  /* ── Margin signal icons ── */
  .sig-icon {{ font-size: 16px; }}

  /* ── Source pills ── */
  .src-pill {{
    display: inline-block; border-radius: 10px; padding: 1px 6px;
    font-size: 10px; font-weight: 700; background: #e0e7ff; color: #3730a3;
    margin-right: 2px;
  }}

  /* ── Squeeze highlight ── */
  .squeeze-high {{ background: linear-gradient(90deg, #fff7ed, #fff); }}
  .squeeze-pct {{ font-size: 13px; font-weight: 700; color: #ea580c; }}

  /* ── Footer ── */
  .footer {{
    text-align: center; color: #94a3b8; font-size: 12px;
    padding: 24px 0 16px;
  }}

  /* ── Responsive / Mobile ── */
  /* 900px catches landscape phones (iPhone 14/15 landscape ~896px) */
  @media (max-width: 900px) {{
    .app-header {{ flex-wrap: wrap; height: auto; padding: 8px 12px; gap: 8px; }}
    .nav-tabs {{ overflow-x: auto; -webkit-overflow-scrolling: touch; flex-wrap: nowrap;
                 padding-bottom: 4px; scrollbar-width: none; }}
    .nav-tabs::-webkit-scrollbar {{ display: none; }}
    .nav-group {{ flex-shrink: 0; }}
    .nav-tab, .nav-group-btn {{ font-size: 13px; padding: 6px 10px; white-space: nowrap; }}
    .header-meta {{ display: none; }}
    .logo {{ font-size: 15px; }}
    .main {{ padding: 10px 8px; overflow-x: hidden; }}
    .card-pad {{ padding: 12px 14px; }}
    table {{ font-size: 13px; }}
    table th, table td {{ padding: 5px 7px; white-space: nowrap; }}
    .table-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  }}
  /* 768px portrait phones — collapse 2-column grids */
  @media (max-width: 768px) {{
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
    .two-col-grid {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 600px) {{
    .app-header {{ padding: 8px 10px; }}
    .kpi-row {{ grid-template-columns: 1fr 1fr; gap: 6px; }}
    .main {{ padding: 8px 6px; }}
    .logo-badge {{ display: none; }}
    .nav-tab, .nav-group-btn {{ font-size: 12px; padding: 5px 8px; }}
  }}

  /* ── Global responsive grid overrides ─────────────────────────────────── */
  /* 4-5 fixed columns → 2 columns on medium screens */
  @media (max-width: 900px) {{
    div[style*="grid-template-columns:repeat(4,1fr)"],
    div[style*="grid-template-columns:repeat(5,1fr)"] {{
      grid-template-columns: repeat(2,1fr) !important;
    }}
    div[style*="grid-template-columns:1fr 1fr 1fr"],
    div[style*="grid-template-columns:repeat(3,1fr)"] {{
      grid-template-columns: repeat(auto-fit,minmax(min(100%,260px),1fr)) !important;
    }}
  }}
  /* Below 640px: all fixed-column inline grids collapse to 1 column */
  @media (max-width: 640px) {{
    div[style*="grid-template-columns"]:not([style*="auto-fill"]):not([style*="auto-fit"]):not([style*="minmax"]) {{
      grid-template-columns: 1fr !important;
    }}
    div[style*="grid-template-columns"][style*="auto-fill"],
    div[style*="grid-template-columns"][style*="auto-fit"] {{
      grid-template-columns: repeat(auto-fill,minmax(min(100%,220px),1fr)) !important;
    }}
    .tbl-wrap, .table-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    /* modal content */
    #dsModal > div {{ margin: 0 !important; border-radius: 0 !important; min-height: 100vh; }}
  }}
  /* Prevent overflow — exclude canvas (ECharts manages its own dimensions) */
  *, *::before, *::after {{ box-sizing: border-box; }}
  img, svg {{ max-width: 100%; height: auto; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
</head>
<body>

<!-- ── Header ── -->
<header class="app-header">
  <div class="logo">
    <span>財報分析</span>
    <span class="logo-badge">ETF</span>
  </div>
  <nav class="nav-tabs" id="navTabs">

    <!-- Standalone -->
    <button class="nav-tab active" onclick="showPage('overview',this)">🏠 總覽</button>
    <button class="nav-tab" onclick="showPage('fullmarket',this)">🌐 全市場</button>

    <div class="nav-sep"></div>

    <!-- 精選推薦 -->
    <div class="nav-group">
      <button class="nav-group-btn" id="premiumNavBtn2">⭐ 精選推薦 <span id="premiumLockIcon2" class="pw-nav-lock">🔒</span><span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('actionsig',this)" style="color:#dc2626;font-weight:800">🎯 綜合行動信號</button>
        <button class="nav-tab" onclick="showPage('conviction',this)">⭐ 推薦排名</button>
        <button class="nav-tab" onclick="showPage('triplereport',this)">💎 TRIPLE精析</button>
        <button class="nav-tab" onclick="showPage('mondayplan',this)" style="color:#be123c;font-weight:700">🗓 週一行動</button>
        <button class="nav-tab" onclick="showPage('premarket',this)" style="color:#0369a1;font-weight:700">📋 開盤行動卡</button>
        <button class="nav-tab" onclick="showPage('watchalerts',this)">🔔 監控警示</button>
        <button class="nav-tab" onclick="showPage('instflows',this)" style="color:#7c3aed;font-weight:700">🏦 法人買賣超</button>
        <button class="nav-tab" onclick="showPage('smartmoney',this)" style="color:#b45309;font-weight:700">🧲 智慧資金匯合</button>
      </div>
    </div>

    <!-- 財務分析 -->
    <div class="nav-group">
      <button class="nav-group-btn">📊 財務分析 <span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('screener',this)">🔎 選股器</button>
        <button class="nav-tab" onclick="showPage('aprevenue',this)">📈 4月營收</button>
        <button class="nav-tab" onclick="showPage('maypreview',this)">📅 5月預告</button>
        <button class="nav-tab" onclick="showPage('earningsq',this)">📊 盈利品質</button>
        <button class="nav-tab" onclick="showPage('dividend',this)">💰 股息日曆</button>
        <button class="nav-tab" onclick="showPage('divsafe',this)">🛡 股息安全</button>
        <button class="nav-tab" onclick="showPage('divincome',this)" style="color:#15803d;font-weight:700">💵 股息收入預測</button>
        <button class="nav-tab" onclick="showPage('q2forecast',this)" style="color:#0369a1;font-weight:700">🔮 Q2預估EPS</button>
      </div>
    </div>

    <!-- 技術DNA -->
    <div class="nav-group">
      <button class="nav-group-btn" id="premiumNavBtn">🧬 技術DNA <span id="premiumLockIcon" class="pw-nav-lock">🔒</span><span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('strategy',this)" style="color:#7c3aed;font-weight:700">🎯 策略系統</button>
        <button class="nav-tab" onclick="showPage('dnascreen',this)" style="color:#c2410c;font-weight:700">🧬 大飆股DNA</button>
        <button class="nav-tab" onclick="showPage('dnatrigger',this)" style="color:#0369a1;font-weight:700">⚡ 升評觸發計算</button>
        <button class="nav-tab" onclick="showPage('backtest',this)">🔬 回測驗證</button>
        <button class="nav-tab" onclick="showPage('sopbacktest',this)" style="color:#f59e0b;font-weight:700">📈 SOP三年回測</button>
        <button class="nav-tab" onclick="showPage('relstrength',this)">📡 相對強度</button>
        <button class="nav-tab" onclick="showPage('momentum',this)">📊 價格動能</button>
        <button class="nav-tab" onclick="showPage('technical',this)">📉 技術分析</button>
      </div>
    </div>

    <!-- 估值分析 -->
    <div class="nav-group">
      <button class="nav-group-btn">💰 估值分析 <span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('valrefresh',this)">📡 估值更新</button>
        <button class="nav-tab" onclick="showPage('targets',this)">🎯 目標價</button>
        <button class="nav-tab" onclick="showPage('peercomp',this)">🔍 同業比較</button>
        <button class="nav-tab" onclick="showPage('sensitivity',this)">🔑 升評路徑</button>
        <button class="nav-tab" onclick="showPage('risk',this)">⚠ 風險/PEG</button>
        <button class="nav-tab" onclick="showPage('mos',this)" style="color:#15803d;font-weight:700">🛡 安全邊際</button>
      </div>
    </div>

    <!-- 組合管理 -->
    <div class="nav-group">
      <button class="nav-group-btn">🏦 組合管理 <span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('possize',this)" style="color:#0369a1;font-weight:700">📐 倉位計算</button>
        <button class="nav-tab" onclick="showPage('portopt',this)">🎯 組合優化</button>
        <button class="nav-tab" onclick="showPage('portfolio',this)">📁 投資組合</button>
        <button class="nav-tab" onclick="showPage('margin',this)">📐 融資融券</button>
        <button class="nav-tab" onclick="showPage('tradesetup',this)">📋 交易設置</button>
        <button class="nav-tab" onclick="showPage('scenario',this)" style="color:#7c3aed;font-weight:700">🎲 情境分析</button>
      </div>
    </div>

    <!-- 產業ETF -->
    <div class="nav-group">
      <button class="nav-group-btn">🏭 產業ETF <span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('sectors',this)" style="color:#c2410c;font-weight:700">🏭 產業資訊</button>
        <button class="nav-tab" onclick="showPage('etfconc',this)">🗂 ETF集中度</button>
        <button class="nav-tab" onclick="showPage('etfcompare',this)">🗂 ETF比較</button>
        <button class="nav-tab" onclick="showPage('otcanalysis',this)" style="color:#16a34a;font-weight:700">🟢 上櫃分析</button>
        <button class="nav-tab" onclick="showPage('rebalance',this)">🔄 成分調整</button>
        <button class="nav-tab" onclick="showPage('aichain',this)">🤖 AI供應鏈</button>
      </div>
    </div>

    <!-- 個股 -->
    <div class="nav-group">
      <button class="nav-group-btn">📋 個股 <span class="nav-arrow">▾</span></button>
      <div class="nav-dropdown">
        <button class="nav-tab" onclick="showPage('stockdetail',this)">📋 個股詳情</button>
        <button class="nav-tab" onclick="showPage('catalyst',this)">📅 催化劑</button>
      </div>
    </div>

    <div class="nav-sep"></div>

    <!-- Export -->
    <button class="nav-tab" onclick="showPage('export',this)" style="color:#0369a1;font-weight:600">📁 匯出</button>

    <!-- Donate — pushed to far right -->
    <span style="flex:1"></span>
    <button class="nav-tab" onclick="showPage('donate',this)" style="color:#d97706;font-weight:700;background:linear-gradient(135deg,#fffbeb,#fef3c7);border:1.5px solid #f59e0b;border-radius:8px">☕ 贊助</button>

  </nav>
  <div class="header-meta">更新: {TODAY} | 62 支股票</div>
</header>

<!-- ═══════════════════════ PAYWALL MODAL ══════════════════════════════════ -->
<div id="paywallOverlay" class="pw-overlay" style="display:none" onclick="if(event.target===this)closePaywall()">
  <div class="pw-modal">
    <div class="pw-lock-icon">🔒</div>
    <div class="pw-title">訂閱會員專區</div>
    <div class="pw-price">NT$ 168 / 月</div>
    <div class="pw-features">
      <b style="color:#2563eb">⭐ 精選推薦</b><br>
      🎯 綜合行動信號 &nbsp;⭐ 推薦排名 &nbsp;💎 TRIPLE精析<br>
      🗓 週一行動 &nbsp;📋 開盤行動卡 &nbsp;🔔 監控警示<br>
      🏦 法人買賣超 &nbsp;🧲 智慧資金匯合<br>
      <br>
      <b style="color:#c2410c">🧬 技術DNA（🔬回測驗證 / 📈SOP回測 免費）</b><br>
      🧬 大飆股DNA &nbsp;🎯 策略系統 &nbsp;⚡ 升評觸發計算<br>
      📡 相對強度 &nbsp;📊 價格動能 &nbsp;📉 技術分析
    </div>
    {'<div style="margin:14px 0 10px;"><img src="' + PAYMENT_QR_B64 + '" alt="付款QR碼" style="width:160px;height:160px;border-radius:10px;display:block;margin:0 auto 8px;box-shadow:0 2px 10px rgba(0,0,0,.15)"><div style="font-size:13px;font-weight:700;color:#1a2332">掃碼轉帳 NT$168</div><div style="font-size:12px;color:#e53e3e;font-weight:600;margin-top:4px">⚠️ 轉帳時請備註您的 Email，以便收取授權碼</div></div>' if PAYMENT_QR_B64 else '<div style="font-size:13px;color:#e53e3e;margin:12px 0">轉帳 NT$168，備註 Email 以收取授權碼</div>'}
    <input id="pwCodeInput" class="pw-input" type="text" placeholder="請輸入授權碼 (e.g. TW168-XXXX)" autocomplete="off"
      onkeydown="if(event.key==='Enter')verifyCode()">
    <div id="pwError" class="pw-error">❌ 授權碼不正確，請確認後再試</div>
    <button class="pw-btn" onclick="verifyCode()">🔓 驗證並解鎖</button>
    <button class="pw-btn-close" onclick="closePaywall()">✕ 關閉</button>
    <div class="pw-contact">付款後請等候授權碼發送至您的 Email</div>
  </div>
</div>

<div class="main">

<!-- ═══════════════════════════════════════════════════════ OVERVIEW ═══ -->
<div id="page-overview" class="page active">

  <!-- Market Alert -->
  <div class="alert-banner">
    <div class="alert-icon">⚠️</div>
    <div>
      <div class="alert-title">市場動態 — {PRICE_DATE} 收盤</div>
      <div class="alert-sub">最新收盤行情 | 動能分析 | TRIPLE CONFIRMED: {len(granddata.get("triple_confirmed",[]))} 支 | 強買: {len(granddata.get("strong_buy",[]))} 支</div>
    </div>
  </div>

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">分析標的</div>
      <div class="kpi-value blue">{len(stocks)}</div>
      <div class="kpi-sub">0050 + 0056 / 00878 / 00713</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">買進信號</div>
      <div class="kpi-value green">{len(buys)}</div>
      <div class="kpi-sub">強烈買進 + 買進</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均綜合分</div>
      <div class="kpi-value amber">{avg_score:.0f}<span style="font-size:16px;color:#94a3b8">/100</span></div>
      <div class="kpi-sub">49 支 0050 成分股</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">融資多空</div>
      <div class="kpi-value">{bullish_margin}<span style="font-size:14px;color:#94a3b8"> / {bearish_margin}</span></div>
      <div class="kpi-sub" style="color:#16a34a">多頭 / 空頭流向</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">頁面瀏覽</div>
      <div class="kpi-value" id="kpi-pageviews" style="color:#a78bfa">—</div>
      <div class="kpi-sub">累計訪客次數</div>
    </div>
  </div>

  <!-- Two-column layout: picks + movers -->
  <div class="two-col-grid">
  <div style="min-width:0">

  <!-- Top Conviction Picks -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🏆 高信心投資標的</div>
    </div>
    <div class="tbl-wrap">
      <table id="tblPicks">
        <thead><tr>
          <th>代號</th><th>名稱</th><th>評級</th><th>綜合分</th>
          <th>股價</th><th>預估P/E</th><th>收入 YoY</th><th>EPS Q1</th><th>融資信號</th>
        </tr></thead>
        <tbody id="tbodyPicks"></tbody>
      </table>
    </div>
  </div>

  </div>
  <div>

  <!-- Market Movers -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📉 今日領跌 ({PRICE_DATE})</div>
    </div>
    <div class="card-pad" id="declinersList"></div>
  </div>

  <div class="card" style="margin-top:14px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📈 今日強勢</div>
    </div>
    <div class="card-pad" id="gainersList"></div>
  </div>

  </div>
  </div>

  <!-- Revenue momentum -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🚀 收入動能強 (Apr 2026 YoY)</div>
    </div>
    <div class="tbl-wrap">
      <table id="tblMomentum">
        <thead><tr>
          <th>代號</th><th>名稱</th><th>收入 YoY</th><th>累計 YoY</th>
          <th>Q1 EPS</th><th>預估P/E</th><th>評級</th>
        </tr></thead>
        <tbody id="tbodyMomentum"></tbody>
      </table>
    </div>
  </div>

</div><!-- /overview -->

<!-- Bollinger Bands modal (overview click) -->
<div id="bbModal" onclick="if(event.target===this)closeBBModal()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:9100;overflow-y:auto;padding:24px 12px">
  <div style="max-width:900px;margin:0 auto;background:#0f172a;border:1px solid #3b82f6;border-radius:12px;padding:22px;position:relative">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <div id="bbModalTitle" style="font-size:18px;font-weight:700;color:#60a5fa"></div>
      <button onclick="closeBBModal()" style="background:#334155;color:#e2e8f0;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:15px">✕</button>
    </div>
    <div id="bbChartEl" style="width:100%;height:460px;background:#0c1220;border-radius:8px"></div>
    <div id="bbInfo" style="margin-top:10px;font-size:12px;color:#64748b;text-align:center">布林通道 BB(20,2) · 蠟燭圖 · 成交量</div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════ SCREENER ═══ -->
<div id="page-screener" class="page">
  <div class="card">
    <div class="filter-bar">
      <label>搜尋:</label>
      <input id="searchBox" type="text" placeholder="代號 / 名稱..." style="width:180px" oninput="renderScreener()">
      <label>評級:</label>
      <select id="filterVerdict" onchange="renderScreener()">
        <option value="">全部</option>
        <option>STRONG BUY</option><option>BUY</option><option>HOLD</option>
        <option>REDUCE</option><option>AVOID</option><option>WATCH</option>
      </select>
      <label>產業:</label>
      <select id="filterSector" onchange="renderScreener()">
        <option value="">全部</option>
      </select>
      <label>融資:</label>
      <select id="filterMargin" onchange="renderScreener()">
        <option value="">全部</option>
        <option>BULLISH</option><option>BEARISH</option>
        <option>MIXED</option><option>UNWINDING</option>
      </select>
    </div>
    <div class="tbl-wrap">
      <table id="tblScreener">
        <thead><tr>
          <th data-col="code">代號</th>
          <th data-col="name">名稱</th>
          <th data-col="sector">產業</th>
          <th data-col="score">綜合分</th>
          <th data-col="verdict">評級</th>
          <th data-col="price">股價</th>
          <th data-col="fwd_pe">預估P/E</th>
          <th data-col="pb">P/B</th>
          <th data-col="div">殖利率</th>
          <th data-col="rev_yoy">收入YoY</th>
          <th data-col="q1_eps">Q1 EPS</th>
          <th data-col="op_margin">營業利益率</th>
          <th data-col="margin_sig">融資信號</th>
          <th data-col="source">ETF</th>
        </tr></thead>
        <tbody id="tbodyScreener"></tbody>
      </table>
    </div>
    <div style="padding:10px 16px;font-size:12px;color:#94a3b8" id="screenerCount"></div>
  </div>
</div><!-- /screener -->

<!-- ═══════════════════════════════════════════════════════ MARGIN ═══ -->
<div id="page-margin" class="page">

  <!-- Legend -->
  <div class="alert-banner" style="background:linear-gradient(135deg,#eff6ff,#f0fdf4);border-color:#93c5fd">
    <div class="alert-icon">📊</div>
    <div>
      <div class="alert-title" style="color:#1e40af">融資融券解讀指南</div>
      <div class="alert-sub" style="color:#1e3a5f">
        <strong>融資 (Margin)</strong> = 散戶槓桿多頭。<strong>融券 (Short)</strong> = 空頭部位。<br>
        🟢 多頭: 融資↑ + 融券↓ &nbsp;|&nbsp; 🔴 空頭: 融資↓ + 融券↑ &nbsp;|&nbsp;
        🟡 混合: 皆升 &nbsp;|&nbsp; ⚪ 解除: 皆降
      </div>
    </div>
  </div>

  <!-- Confirmed BUY -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">✅ 確認買進：強基本面 + 多頭融資流向</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>代號</th><th>名稱</th><th>綜合分</th>
          <th>融資信號</th><th>融資變化</th><th>融券變化</th><th>組合判斷</th>
        </tr></thead>
        <tbody id="tbodyConfirmed"></tbody>
      </table>
    </div>
  </div>

  <!-- Divergence -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⚠️ 背離警示：基本面佳但融資看空</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>代號</th><th>名稱</th><th>綜合分</th><th>融資信號</th><th>細節</th>
        </tr></thead>
        <tbody id="tbodyDivergence"></tbody>
      </table>
    </div>
  </div>

  <!-- Short squeeze -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🎯 軋空候選：融券餘額 &gt; 15% of 融資</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>代號</th><th>名稱</th><th>融券/融資 %</th>
          <th>融券餘額</th><th>融資餘額</th><th>綜合分</th>
        </tr></thead>
        <tbody id="tbodySqueeze"></tbody>
      </table>
    </div>
  </div>

  <!-- Full margin snapshot -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 融資融券全覽 (依綜合分排序)</div>
    </div>
    <div class="tbl-wrap">
      <table id="tblMarginFull">
        <thead><tr>
          <th data-col="score">綜合分</th>
          <th data-col="code">代號</th>
          <th data-col="name">名稱</th>
          <th data-col="margin_sig">融資信號</th>
          <th data-col="m_today">融資餘額</th>
          <th data-col="m_chg">融資變化</th>
          <th data-col="s_today">融券餘額</th>
          <th data-col="s_chg">融券變化</th>
        </tr></thead>
        <tbody id="tbodyMarginFull"></tbody>
      </table>
    </div>
  </div>

</div><!-- /margin -->

<!-- ════════════════════════════ 推薦排名 (合併) ═══ -->
<div id="page-conviction" class="page">
  <!-- Sub-tab bar -->
  <div class="sub-tab-bar">
    <button class="sub-tab active" onclick="showSubTab(this,'sub-conv-sb')">🔥 最強推薦</button>
    <button class="sub-tab" onclick="showSubTab(this,'sub-conv-mx')">📐 確信矩陣</button>
    <button class="sub-tab" onclick="showSubTab(this,'sub-conv-gu')">🏆 綜合排名</button>
  </div>
  <div id="sub-conv-sb" class="sub-panel active">
  <!-- Hero KPIs -->
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card" style="background:linear-gradient(135deg,#7c3aed,#6d28d9);color:#fff">
      <div class="kpi-label" style="color:#ddd6fe">🔥 最強推薦</div>
      <div class="kpi-value" id="kpiStrongBuy" style="color:#fff"></div>
      <div class="kpi-sub" style="color:#c4b5fd">信念分 ≥ 65</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(135deg,#16a34a,#15803d);color:#fff">
      <div class="kpi-label" style="color:#bbf7d0">✅ 買進</div>
      <div class="kpi-value" id="kpiBuyConv" style="color:#fff"></div>
      <div class="kpi-sub" style="color:#86efac">信念分 45–64</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均信念分</div>
      <div class="kpi-value blue" id="kpiAvgConv"></div>
      <div class="kpi-sub">全宇宙 49 支</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">❌ 迴避</div>
      <div class="kpi-value red" id="kpiAvoidConv"></div>
      <div class="kpi-sub">信念分 &lt; 10</div>
    </div>
  </div>

  <!-- Methodology explainer -->
  <div class="alert-banner" style="background:linear-gradient(135deg,#fef3c7,#fffbeb);border-color:#fbbf24">
    <div class="alert-title" style="color:#92400e">📐 信念評分方法 (滿分 100)</div>
    <div class="alert-sub" style="color:#78350f">
      基本面(+30) · 低於30日線均值回歸(+20) · 目標價上漲空間(+20) · 低風險(+15) · 融資多頭(+10) · PEG低估(+5) · 三重確認(+5)
    </div>
  </div>

  <!-- Strong buys -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:linear-gradient(135deg,#faf5ff,#f5f3ff)">
      <div class="section-title" style="color:#6d28d9">🔥 最強推薦 — 高信念買進</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>信念分</th><th>代號</th><th>名稱</th><th>產業</th>
        <th>綜合分</th><th>風險</th><th>目標漲幅</th><th>PEG</th>
        <th>vs 30日線</th><th>融資</th><th>三重</th>
      </tr></thead>
      <tbody id="tbodyStrongBuy"></tbody>
      </table>
    </div>
  </div>

  <!-- Buys + Watch grid -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:#f0fdf4">
      <div class="section-title" style="color:#15803d">✅ 買進 (信念分 45–64)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>信念分</th><th>代號</th><th>名稱</th><th>綜合分</th><th>漲幅</th><th>融資</th>
      </tr></thead>
      <tbody id="tbodyBuyConv"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">👀 觀察 (信念分 25–44)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>信念分</th><th>代號</th><th>名稱</th><th>綜合分</th><th>漲幅</th>
      </tr></thead>
      <tbody id="tbodyWatchConv"></tbody>
      </table>
    </div>
  </div>
  </div>

  <!-- Full ranked list -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 全部信念排行榜</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>信念分</th><th>代號</th><th>名稱</th><th>產業</th>
        <th>評級</th><th>綜合分</th><th>風險</th><th>目標漲幅</th><th>融資</th>
      </tr></thead>
      <tbody id="tbodyConvFull"></tbody>
      </table>
    </div>
  </div>

  <!-- Conviction detail modal -->
  <div id="convDetailModal" style="display:none;position:fixed;inset:0;z-index:9000;background:rgba(15,23,42,0.6);align-items:center;justify-content:center" onclick="if(event.target===this){{this.style.display='none'}}">
    <div style="background:#fff;border-radius:14px;padding:24px;max-width:500px;width:92%;max-height:88vh;overflow-y:auto;position:relative;box-shadow:0 20px 60px rgba(0,0,0,0.3)">
      <button onclick="document.getElementById('convDetailModal').style.display='none'" style="position:absolute;top:12px;right:14px;background:none;border:none;font-size:22px;cursor:pointer;color:#94a3b8;line-height:1">✕</button>
      <div id="convDetailContent"></div>
    </div>
  </div>
  </div><!-- /sub-conv-sb -->

  <!-- 確信矩陣 sub-panel -->
  <div id="sub-conv-mx" class="sub-panel">
  <div class="alert-banner" style="background:linear-gradient(135deg,#faf5ff,#ede9fe);border-color:#7c3aed;color:#4c1d95">
    <b>🔥 確信矩陣</b> — 整合 Grand Score + 智慧資金 + 行動信號 + 安全邊際 + Q2 EPS + DNA 的最終確信排名
  </div>
  <div class="kpi-row" id="convKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card">
      <div class="card-pad">
        <div class="section-title" style="color:#7c3aed;margin-bottom:10px">🔥 TIER 1 核心倉位 (≥85分)</div>
        <div id="convTier1"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-pad">
        <div class="section-title" style="color:#2563eb;margin-bottom:10px">💎 TIER 2 主力倉位 (72–84分)</div>
        <div id="convTier2"></div>
      </div>
    </div>
  </div>
  <div class="card">
    <div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📊 全排名確信矩陣</div>
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0">
              <th style="text-align:left;padding:6px 8px">代號</th>
              <th style="text-align:left;padding:6px 8px">名稱</th>
              <th style="text-align:right;padding:6px 8px">確信分</th>
              <th style="text-align:right;padding:6px 8px">F1 Grand</th>
              <th style="text-align:right;padding:6px 8px">F2 資金</th>
              <th style="text-align:right;padding:6px 8px">F3 行動</th>
              <th style="text-align:right;padding:6px 8px">F4 MoS</th>
              <th style="text-align:right;padding:6px 8px">F5 Q2</th>
              <th style="text-align:right;padding:6px 8px">F6 DNA</th>
              <th style="text-align:right;padding:6px 8px">加成</th>
              <th style="text-align:left;padding:6px 8px">評級</th>
              <th style="text-align:left;padding:6px 8px">倉位建議</th>
            </tr>
          </thead>
          <tbody id="convAllBody"></tbody>
        </table>
      </div>
    </div>
  </div>
  </div><!-- /sub-conv-mx -->

  <!-- 綜合排名 sub-panel -->
  <div id="sub-conv-gu" class="sub-panel">
  <div class="alert-banner" style="background:linear-gradient(135deg,#1e3a5f,#1e40af);border-color:#3b82f6">
    <div class="alert-title" style="color:#fff">🏆 綜合排名 — 基本面 + 技術面 + 估值 + 動能</div>
    <div class="alert-body" style="color:#bfdbfe">28個分析流整合 | 滿分100分 | 基本面25 + 技術DNA25 + 估值25 + 動能25</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px" id="grandMetaCards"></div>
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🚀 TRIPLE CONFIRMED + STRONG BUY (所有維度對齊)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>現價</th>
        <th title="綜合分數">總分</th>
        <th title="基本面25分">基本面</th>
        <th title="技術DNA25分">技術DNA</th>
        <th title="估值25分">估值</th>
        <th title="動能25分">動能</th>
        <th>P/E</th><th>殖利率</th><th>漲跌%</th><th>DNA跡象</th><th>判定</th>
      </tr></thead>
      <tbody id="tbodyGrandTop"></tbody>
    </table></div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 全部62支股票綜合排名</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>#</th><th>代號</th><th>名稱</th>
        <th>總分</th><th>基本</th><th>技術</th><th>估值</th><th>動能</th>
        <th>P/E</th><th>殖利率</th><th>判定</th>
      </tr></thead>
      <tbody id="tbodyGrandAll"></tbody>
    </table></div>
  </div>
  </div><!-- /sub-conv-gu -->

</div><!-- /page-conviction -->

<!-- ═══════════════════════════════════════════════════ 產業資訊 (合併) ═══ -->
<div id="page-sectors" class="page">
  <!-- Sub-tab bar -->
  <div class="sub-tab-bar">
    <button class="sub-tab active" onclick="showSubTab(this,'sub-sec-1')">📊 產業分析</button>
    <button class="sub-tab" onclick="showSubTab(this,'sub-sec-2')">🏭 產業熱圖</button>
    <button class="sub-tab" onclick="showSubTab(this,'sub-sec-3')">🔄 板塊輪動</button>
    <button class="sub-tab" onclick="showSubTab(this,'sub-sec-4')">🌐 產業總覽</button>
  </div>

  <!-- 產業分析 -->
  <div id="sub-sec-1" class="sub-panel active">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🏭 各產業綜合分排行</div>
    </div>
    <div class="card-pad">
      <div class="bar-chart" id="sectorChart"></div>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 各產業詳細列表</div>
    </div>
    <div class="tbl-wrap">
      <table id="tblSectorDetail">
        <thead><tr>
          <th>產業</th><th>股票數</th><th>平均分</th>
          <th>最佳評級</th><th>最高分股票</th>
        </tr></thead>
        <tbody id="tbodySectorDetail"></tbody>
      </table>
    </div>
  </div>
  </div><!-- /sub-sec-1 -->

  <!-- 產業熱圖 -->
  <div id="sub-sec-2" class="sub-panel">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fef9c3,#fefce8);border-color:#fde047;color:#713f12">
    <b>🏭 產業熱圖</b> — 按產業聚合：信念分、DNA訊號、相對強度、估值
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-bottom:20px"
       id="sectorGrid"></div>
  <div class="card">
    <div class="card-title">📊 產業比較總表</div>
    <table class="data-table">
      <thead><tr>
        <th>產業</th><th>股數</th><th>平均信念分</th><th>平均DNA</th>
        <th>60日超額RS</th><th>平均PE</th><th>平均殖利率</th>
        <th>飆股數</th><th>產業信號</th>
      </tr></thead>
      <tbody id="tbodySectors"></tbody>
    </table>
  </div>
  <div class="card" style="margin-top:16px" id="sectorDetail" style="display:none">
    <div class="card-title" id="sectorDetailTitle">選擇產業查看個股</div>
    <table class="data-table">
      <thead><tr>
        <th>代碼</th><th>名稱</th><th>信念分</th><th>DNA訊號</th>
        <th>60日RS</th><th>PE</th><th>殖利率</th><th>建議</th>
      </tr></thead>
      <tbody id="tbodySectorStocks"></tbody>
    </table>
  </div>
  </div><!-- /sub-sec-2 -->

  <!-- 板塊輪動 -->
  <div id="sub-sec-3" class="sub-panel">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🔄 板塊輪動信號</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">
    基於RS(20/60/120日)、價格動能與營收加速度，識別哪些板塊正在領漲或落後。</p>
  <div class="kpi-row" id="srKpis"></div>
  <div id="srMatrix" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-bottom:16px"></div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">🔀 輪動交易建議</div>
    <div id="srTrades"></div>
  </div></div>
  </div><!-- /sub-sec-3 -->

  <!-- 產業總覽 -->
  <div id="sub-sec-4" class="sub-panel">
  <div class="alert-banner" style="background:linear-gradient(135deg,#ecfeff,#cffafe);border-color:#0891b2;color:#164e63">
    <b>🌐 產業總覽</b> — 1,078 家上市公司 · 4月2026營收 · 33個產業中位數成長 · 持倉 vs 產業Alpha分析
  </div>
  <div class="kpi-row" id="smKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card">
      <div class="card-pad">
        <div class="section-title" style="color:#16a34a;margin-bottom:10px">🔥 Top 產業 (中位YoY最高)</div>
        <div id="smTop5"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-pad">
        <div class="section-title" style="color:#dc2626;margin-bottom:10px">❌ 弱勢產業 (中位YoY最低)</div>
        <div id="smBot5"></div>
      </div>
    </div>
  </div>
  <div class="card">
    <div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📊 持倉 vs 產業中位 Alpha排名</div>
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0">
              <th style="text-align:left;padding:6px 8px">代號</th><th style="text-align:left;padding:6px 8px">名稱</th>
              <th style="text-align:left;padding:6px 8px">產業</th>
              <th style="text-align:right;padding:6px 8px">4月YoY</th>
              <th style="text-align:right;padding:6px 8px">產業中位</th>
              <th style="text-align:right;padding:6px 8px">vs產業</th>
              <th style="text-align:right;padding:6px 8px">Grand</th>
              <th style="text-align:left;padding:6px 8px">評級</th>
            </tr>
          </thead>
          <tbody id="smAlphaBody"></tbody>
        </table>
      </div>
    </div>
  </div>
  <div class="card" style="margin-top:12px">
    <div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📈 全產業排名 (33個產業)</div>
      <div id="smAllSectors"></div>
    </div>
  </div>
  </div><!-- /sub-sec-4 -->

</div><!-- /page-sectors -->

<!-- ══════════════════════════════════════════════════ ETF CONC ═══ -->
<div id="page-etfconc" class="page">
  <!-- KPIs -->
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">0050 HHI</div>
      <div class="kpi-value" id="kpiHHI0050" style="color:#dc2626"></div>
      <div class="kpi-sub">高度集中</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">4-ETF 混合 HHI</div>
      <div class="kpi-value green" id="kpiHHIBlend"></div>
      <div class="kpi-sub">分散改善</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">台積電 0050佔比</div>
      <div class="kpi-value" id="kpiTsmc0050" style="color:#dc2626"></div>
      <div class="kpi-sub">單一股票集中</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">台積電 混合佔比</div>
      <div class="kpi-value green" id="kpiTsmcBlend"></div>
      <div class="kpi-sub">4-ETF 混合後</div>
    </div>
  </div>

  <div class="alert-banner" style="background:linear-gradient(135deg,#fef3c7,#fffbeb);border-color:#fbbf24">
    <div class="alert-title" style="color:#92400e">⚠️ ETF集中度說明</div>
    <div class="alert-sub" style="color:#78350f">
      HHI (赫芬達爾-赫希曼指數): &lt;1500=分散 | 1500–2500=中等 | &gt;2500=高度集中。
      混合組合假設等額投入 0050 + 0056 + 00878 + 00713 各25%。
      006208 與 0050 高度重疊，同時持有不增加分散效果。
    </div>
  </div>

  <!-- 0050 Top Holdings -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 0050 前15大持股 (市值加權)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>0050佔比</th><th>混合佔比</th><th>持有ETF數</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbody0050Top"></tbody>
      </table>
    </div>
  </div>

  <!-- ETF Overlap -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🔗 多ETF重疊股票 (3+ ETFs)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>ETF</th><th>重疊數</th><th>混合佔比</th>
      </tr></thead>
      <tbody id="tbodyOverlap"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">💡 投資組合建議</div>
    </div>
    <div class="card-pad">
      <table style="width:100%"><thead><tr>
        <th>目標</th><th>建議配置</th>
      </tr></thead>
      <tbody>
        <tr><td><strong>成長</strong></td><td>100% 0050 — 最純粹大型股曝險</td></tr>
        <tr><td><strong>收益</strong></td><td>60% 0050 + 40% 0056 — 高殖利率傾斜</td></tr>
        <tr><td><strong>均衡</strong></td><td>50% 0050 + 25% 00878 + 25% 00713 — ESG+低波動</td></tr>
        <tr><td><strong>全混合</strong></td><td>25/25/25/25 — 仍以台積電為主</td></tr>
        <tr><td style="color:#dc2626"><strong>避免</strong></td><td style="color:#dc2626">0050+006208 — 近乎重複，無分散效益</td></tr>
      </tbody>
      </table>
      <div style="margin-top:16px;padding:12px;background:#f0f9ff;border-radius:8px;font-size:12px;color:#0369a1">
        <strong>關鍵洞察：</strong> 同時持有4檔ETF，台積電實際曝險從
        <span id="tsmc0050Inline" style="color:#dc2626;font-weight:700"></span>
        降至 <span id="tsmcBlendInline" style="color:#16a34a;font-weight:700"></span>。
        金融股在0056+00713中比重高，4ETF組合的金融板塊曝險約為純0050的2倍。
      </div>
    </div>
  </div>
  </div>

  <!-- Blended Top 20 -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🎯 4-ETF混合組合前20大實際曝險</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>有效佔比</th><th>持有ETF</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbodyBlendTop"></tbody>
      </table>
    </div>
  </div>
</div><!-- /etfconc -->

<!-- ══════════════════════════════════════════════════ DIV SAFETY ══ -->
<div id="page-divsafe" class="page">

  <!-- KPIs -->
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">配息股票數</div>
      <div class="kpi-value blue" id="kpiDivTotal"></div>
      <div class="kpi-sub">共62支宇宙中</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">安全/穩健</div>
      <div class="kpi-value green" id="kpiDivSafe"></div>
      <div class="kpi-sub">配息率 ≤ 80%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">偏緊/高風險</div>
      <div class="kpi-value" id="kpiDivRisk" style="color:#dc2626"></div>
      <div class="kpi-sub">配息率 > 80%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">質優收益標的</div>
      <div class="kpi-value" id="kpiDivQuality" style="color:#7c3aed"></div>
      <div class="kpi-sub">殖利率≥4.5%+安全</div>
    </div>
  </div>

  <div class="alert-banner" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#86efac">
    <div class="alert-title" style="color:#14532d">📖 配息可持續性說明</div>
    <div class="alert-sub" style="color:#166534">
      配息率 = 年度每股股息 ÷ 年化EPS (Q1×4)。覆蓋率 = EPS ÷ 每股股息。
      ✅ SAFE: 配息率≤50% | 🟢 MODERATE: 50–80% | 🟡 TIGHT: 80–100% | 🔴 AT RISK: >100%。
      金融股因有資本準備金，配息率略高於100%屬正常現象。
      ⚠️ 力積電(6770)Q1為一次性業外收入，配息率數據不具代表性。
    </div>
  </div>

  <!-- Quality income picks -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⭐ 質優收益標的 (殖利率≥4.5% + 配息率≤80%)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>產業</th><th>殖利率</th><th>每股股息</th>
        <th>年化EPS</th><th>配息率</th><th>覆蓋率</th><th>安全等級</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbodyDivQuality"></tbody>
      </table>
    </div>
  </div>

  <!-- At risk + full table side by side -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🔴 配息率偏高警示 (>100%)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>殖利率</th><th>配息率</th><th>說明</th>
      </tr></thead>
      <tbody id="tbodyDivRisk"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 ETF配息分佈統計</div>
    </div>
    <div class="card-pad">
      <div id="divYieldDist"></div>
    </div>
  </div>
  </div>

  <!-- Full table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 全部配息股票安全評估 (依殖利率排序)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>殖利率</th><th>配息率</th><th>覆蓋率</th>
        <th>安全等級</th><th>質量</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbodyDivFull"></tbody>
      </table>
    </div>
  </div>
</div><!-- /divsafe -->

<!-- ═══════════════════════════════════════════════ APR REVENUE ═══ -->
<div id="page-aprevenue" class="page">
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">資料期間</div>
      <div class="kpi-value blue" style="font-size:20px">2026/04</div>
      <div class="kpi-sub">Jan–Apr 累計YoY</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">高成長 (&gt;+20%)</div>
      <div class="kpi-value green" id="kpiAprHigh"></div>
      <div class="kpi-sub">累計YoY</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">加速成長</div>
      <div class="kpi-value" id="kpiAprAccel" style="color:#7c3aed"></div>
      <div class="kpi-sub">vs Q1基準改善</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">衰退 (&lt;0%)</div>
      <div class="kpi-value red" id="kpiAprNeg"></div>
      <div class="kpi-sub">累計YoY</div>
    </div>
  </div>

  <div class="alert-banner" style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#93c5fd">
    <div class="alert-title" style="color:#1e3a8a">📊 2026年1–4月累計營收 (最新TWSE資料)</div>
    <div class="alert-sub" style="color:#1e40af">
      累計YoY = Jan–Apr 2026 vs Jan–Apr 2025。加速 = 累計YoY > Q1 YoY (趨勢改善)。
      ⚠️ 金融股受IFRS 17影響，YoY數字失真，請以P/B+殖利率評估而非收入成長。
      5月數據預計2026/06/10後公布。
    </div>
  </div>

  <!-- Top growers -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🚀 累計YoY最高 — 前20名</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>產業</th><th>4月YoY</th><th>累計YoY</th><th>月環比(MoM)</th><th>趨勢</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbodyAprTop"></tbody>
      </table>
    </div>
  </div>

  <!-- Contracting + Accelerating side by side -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:#fef2f2">
      <div class="section-title" style="color:#dc2626">📉 累計營收衰退股 (YoY &lt; 0)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>累計YoY</th><th>4月YoY</th><th>綜合分</th>
      </tr></thead>
      <tbody id="tbodyAprNeg"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:#f5f3ff">
      <div class="section-title" style="color:#7c3aed">⬆⬆ 加速成長股 (vs Q1改善)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>累計YoY</th><th>Q1 YoY</th><th>差異</th>
      </tr></thead>
      <tbody id="tbodyAprAccel"></tbody>
      </table>
    </div>
  </div>
  </div>

  <!-- Full table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 全部股票4月營收數據</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>4月營收(B)</th><th>累計(B)</th><th>4月YoY</th><th>累計YoY</th><th>MoM</th><th>趨勢</th>
      </tr></thead>
      <tbody id="tbodyAprFull"></tbody>
      </table>
    </div>
  </div>
</div><!-- /aprevenue -->

<!-- ══════════════════════════════════════════════════ REBALANCE ═══ -->
<div id="page-rebalance" class="page">
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">下次調整</div>
      <div class="kpi-value blue" style="font-size:16px">2026/07</div>
      <div class="kpi-sub">季度再平衡</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">最弱成分</div>
      <div class="kpi-value red" id="kpiWeakest" style="font-size:18px"></div>
      <div class="kpi-sub" id="kpiWeakestName"></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">高風險股 (排名48–49)</div>
      <div class="kpi-value red" id="kpiAtRisk"></div>
      <div class="kpi-sub">可能被剔除</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">邊緣股 (排名44–49)</div>
      <div class="kpi-value" id="kpiBorderline" style="color:#f59e0b"></div>
      <div class="kpi-sub">需要觀察</div>
    </div>
  </div>

  <div class="alert-banner" style="background:linear-gradient(135deg,#fef3c7,#fffbeb);border-color:#fbbf24">
    <div class="alert-title" style="color:#92400e">⚙️ 0050季度再平衡機制</div>
    <div class="alert-sub" style="color:#78350f">
      6月30日收盤後以自由流通市值排名，前50名留在指數，其餘剔除。
      預計7月7–10日公告，7月14–17日生效。被納入股票受到0050 ETF強制買盤支撐(AUM≈4000億)。
      ⚠️ 市值估算為代理值(0050權重×AUM)，非實際總市值。相對排名準確，絕對金額僅供參考。
    </div>
  </div>

  <!-- Borderline at-risk -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:#fef2f2">
      <div class="section-title" style="color:#dc2626">🔴 邊緣成分股 — 調整風險 (排名44–49)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>估算市值</th><th>今日漲跌</th><th>累計YoY</th><th>風險</th>
      </tr></thead>
      <tbody id="tbodyBorderline"></tbody>
      </table>
    </div>
  </div>

  <!-- Core top 10 + full ranking side by side -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9;background:#f0fdf4">
      <div class="section-title" style="color:#15803d">✅ 核心前10名 — 安全</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>估算市值</th><th>今日</th>
      </tr></thead>
      <tbody id="tbodyCore10"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 再平衡日曆</div>
    </div>
    <div class="card-pad">
      <table style="width:100%"><thead><tr><th>事件</th><th>預計日期</th></tr></thead>
      <tbody>
        <tr><td>Q2收盤快照</td><td><strong>2026/06/30</strong></td></tr>
        <tr><td>FTSE Russell公告</td><td>2026/07/07–10</td></tr>
        <tr><td>新成分生效</td><td>2026/07/14–17</td></tr>
        <tr><td>ETF強制買賣</td><td>生效當週</td></tr>
        <tr><td>下次季度調整</td><td>2026/10</td></tr>
      </tbody>
      </table>
      <div style="margin-top:12px;padding:10px;background:#fef2f2;border-radius:8px;font-size:12px;color:#991b1b">
        <strong>投資含義：</strong>被納入股票通常在公告後+3–5%；
        被剔除股票通常-2–4%。在公告前布局可捕捉此Alpha。
      </div>
    </div>
  </div>
  </div>

  <!-- Full ranking table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 0050全部成分排名 (今日收盤後調整)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>估算市值(B)</th><th>今日</th><th>累計YoY</th><th>狀態</th>
      </tr></thead>
      <tbody id="tbodyRebFull"></tbody>
      </table>
    </div>
  </div>
</div><!-- /rebalance -->

<!-- ══════════════════════════════════════════════ TRADE SETUP ═══ -->
<div id="page-tradesetup" class="page">
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card" style="background:linear-gradient(135deg,#fef2f2,#fff5f5)">
      <div class="kpi-label" style="color:#991b1b">交易設置數</div>
      <div class="kpi-value" id="kpiTradeCount" style="color:#dc2626"></div>
      <div class="kpi-sub">STRONG BUY 標的</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均風險/報酬</div>
      <div class="kpi-value green" id="kpiAvgRR"></div>
      <div class="kpi-sub">每1元風險獲X元報酬</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">總建議倉位</div>
      <div class="kpi-value blue" id="kpiTotalPos"></div>
      <div class="kpi-sub">剩餘現金緩衝</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">最佳R/R</div>
      <div class="kpi-value" id="kpiBestRR" style="color:#7c3aed"></div>
      <div class="kpi-sub" id="kpiBestRRName"></div>
    </div>
  </div>

  <div class="alert-banner" style="background:#fef2f2;border-color:#fca5a5">
    <div class="alert-title" style="color:#991b1b">⚠️ 免責聲明</div>
    <div class="alert-sub" style="color:#7f1d1d">
      以下交易設置為研究分析輸出，非投資建議。倉位基於1%組合風險法則（最大虧損=1%×停損幅度）。
      投資前請自行評估風險承受能力，並諮詢合格財務顧問。過去績效不代表未來結果。
    </div>
  </div>

  <!-- Summary table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 交易設置總覽</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>評級</th><th>代號</th><th>名稱</th><th>現價</th><th>目標價</th>
        <th>上漲空間</th><th>停損</th><th>風險/報酬</th><th>建議倉位</th><th>預計持有</th>
      </tr></thead>
      <tbody id="tbodyTradeSummary"></tbody>
      </table>
    </div>
  </div>

  <!-- Trade cards grid -->
  <div id="tradeCardsGrid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px"></div>

  <!-- Portfolio construction note -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🏗️ 組合建構原則</div>
    </div>
    <div class="card-pad">
      <table style="width:100%"><thead><tr><th>規則</th><th>建議</th></tr></thead>
      <tbody>
        <tr><td>單一股票上限</td><td>≤ 10% 投資組合</td></tr>
        <tr><td>科技/半導體板塊</td><td>≤ 50%</td></tr>
        <tr><td>金融板塊</td><td>≤ 30%</td></tr>
        <tr><td>現金緩衝</td><td>≥ 20% (用於回調加碼)</td></tr>
        <tr><td>停損紀律</td><td>跌破停損位無條件執行，不等反彈</td></tr>
        <tr><td>定期檢視</td><td>每季財報後重新評估持有理由</td></tr>
      </tbody>
      </table>
    </div>
  </div>
</div><!-- /tradesetup -->

<!-- ═══════════════════════════════════════════════════ AI CHAIN ═══ -->
<div id="page-aichain" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#93c5fd">
    <div class="alert-title" style="color:#1d4ed8">🤖 Taiwan AI/HPC 供應鏈地圖</div>
    <div class="alert-sub" style="color:#1e40af">
      全球AI基礎建設需求流經台灣完整供應鏈 — 從晶圓代工到AI伺服器系統。
      以下分析每一層的投資吸引力、估值與風險。
    </div>
  </div>

  <!-- Layer KPI matrix -->
  <div id="chainKpiGrid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px"></div>

  <!-- Chain bar chart (horizontal layers) -->
  <div class="card" style="margin-bottom:20px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">各層級平均綜合分數 vs 目標上漲空間</div>
    </div>
    <div id="chainBarChart" style="padding:16px"></div>
  </div>

  <!-- Per-layer detail cards -->
  <div id="chainLayerCards"></div>

  <!-- Investment view summary -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📌 投資策略摘要</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:16px;font-size:13px;color:#475569">
      <div>
        <p><strong style="color:#059669">✅ 最佳層級 — L3 記憶體</strong><br>
        南亞科(2408)累計YoY +624%，目標上漲+156%。DRAM週期復甦力道最強，風險分最低(12)。</p>
        <p style="margin-top:12px"><strong style="color:#2563eb">🏛️ 核心持倉 — L1 台積電</strong><br>
        AI算力絕對瓶頸。任何AI需求必然流經台積電。護城河無與倫比，適合長期持有。</p>
        <p style="margin-top:12px"><strong style="color:#7c3aed">📈 高彈性 — L6 AI伺服器</strong><br>
        廣達(2382)技嘉(2376)直接吃到雲端資本支出。毛利薄但收入能見度高。</p>
      </div>
      <div>
        <p><strong style="color:#dc2626">⚠️ 謹慎 — L4 IC設計</strong><br>
        聯發科累計YoY為負；手機市場疲弱抵銷AI受益。本層分化，需個股篩選。</p>
        <p style="margin-top:12px"><strong style="color:#d97706">💡 被低估 — L7 關鍵零組件</strong><br>
        大立光光學+台達電散熱 — AI伺服器散熱需求被市場忽視；留意本層潛力。</p>
        <p style="margin-top:12px"><strong style="color:#64748b">⭕ AI間接受益 — 金融股</strong><br>
        AI主題帶動企業放款需求與資本市場活躍，利好台灣銀行股但非直接受益。</p>
      </div>
    </div>
  </div>
</div><!-- /aichain -->

<!-- ═══════════════════════════════════════════════════ VAL REFRESH ═══ -->
<div id="page-valrefresh" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#86efac">
    <div class="alert-title" style="color:#15803d">📡 估值更新 — {BWIBBU_DATE} 收盤數據</div>
    <div class="alert-sub" style="color:#166534">
      BWIBBU_ALL 最新 P/E、P/B、殖利率 vs 本次分析起始值。
      P/E膨脹 = 股價漲幅超過盈利增速（偏貴）；P/E收縮 = 盈利改善或股價下跌（潛在機會）。
    </div>
  </div>

  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card" style="background:linear-gradient(135deg,#f0fdf4,#f8fff9)">
      <div class="kpi-label" style="color:#15803d">覆蓋股票數</div>
      <div class="kpi-value" id="kpiBwibbuCount" style="color:#16a34a"></div>
      <div class="kpi-sub">BWIBBU匹配</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">高殖利率 (≥4.5%)</div>
      <div class="kpi-value" id="kpiHighDiv"></div>
      <div class="kpi-sub">股票數</div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(135deg,#fef9c3,#fffef0)">
      <div class="kpi-label" style="color:#854d0e">P/E膨脹最大</div>
      <div class="kpi-value" id="kpiPeExpand" style="font-size:18px;color:#d97706"></div>
      <div class="kpi-sub" id="kpiPeExpandName"></div>
    </div>
    <div class="kpi-card" style="background:linear-gradient(135deg,#eff6ff,#f0f9ff)">
      <div class="kpi-label" style="color:#1d4ed8">P/E收縮最大 (機會)</div>
      <div class="kpi-value" id="kpiPeContract" style="font-size:18px;color:#2563eb"></div>
      <div class="kpi-sub" id="kpiPeContractName"></div>
    </div>
  </div>

  <!-- Signal table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🔑 重大估值信號</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>信號</th><th>代號</th><th>名稱</th><th>前P/E</th><th>新P/E</th><th>變化</th><th>殖利率</th><th>說明</th>
      </tr></thead>
      <tbody id="tbodyValSignals"></tbody>
      </table>
    </div>
  </div>

  <!-- High div table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">💰 高殖利率股票 (≥4.5%)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>殖利率</th><th>P/E</th><th>P/B</th><th>評分</th>
      </tr></thead>
      <tbody id="tbodyHighDiv"></tbody>
      </table>
    </div>
  </div>

  <!-- Cheap PE table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">💎 最便宜非金融股 (P/E &lt; 15x)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>P/E</th><th>前P/E</th><th>變化</th><th>殖利率</th>
      </tr></thead>
      <tbody id="tbodyCheapPE"></tbody>
      </table>
    </div>
  </div>
</div><!-- /valrefresh -->

<!-- ═══════════════════════════════════════════════════ MOMENTUM ═══ -->
<div id="page-momentum" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fdf4ff,#f3e8ff);border-color:#d8b4fe">
    <div class="alert-title" style="color:#7e22ce">📊 價格動能分析 — {PRICE_DATE} 收盤</div>
    <div class="alert-body">與原始分析基準(Iteration 10)比較漲跌幅 | 30日均線 | 強烈訊號篩選</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px" id="momSignalCards"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">🚀 最大漲幅 (自基準)</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>基準價</th><th>現價</th><th>漲跌</th><th>vs 30MA</th><th>訊號</th></tr></thead><tbody id="tbodyGainers"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">💥 最大跌幅 (自基準)</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>基準價</th><th>現價</th><th>漲跌</th><th>vs 30MA</th><th>訊號</th></tr></thead><tbody id="tbodyLosers"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">✅ 強烈推薦追蹤 — 建倉機會?</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>分析價</th><th>現價</th><th>漲跌</th><th>vs 30MA</th><th>論點效力</th></tr></thead><tbody id="tbodyConvMom"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">📈 站上30MA (動能 >+5%)</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>現價</th><th>30MA</th><th>高出%</th><th>訊號</th></tr></thead><tbody id="tbodyAboveMA"></tbody></table></div>
    </div>
  </div>
</div><!-- /momentum -->

<!-- ═══════════════════════════════════════════════════ DNA SCREEN ═══ -->
<div id="page-dnascreen" class="page">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
    <h2 style="margin:0;color:#c2410c">🧬 大飆股DNA篩選 — 全市場</h2>
    <span id="dnaScreenDate" style="font-size:12px;color:#94a3b8"></span>
  </div>
  <!-- Signal legend -->
  <div style="background:#1e1a10;border:1px solid #92400e;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px">
    <b style="color:#fb923c">5項訊號：</b>
    <span style="color:#fde68a">①營收YoY&gt;30%</span> &nbsp;
    <span style="color:#fde68a">②W%R(50)&lt;20</span> &nbsp;
    <span style="color:#fde68a">③RSI(60)&gt;57</span> &nbsp;
    <span style="color:#fde68a">④Q1 EPS&gt;0</span> &nbsp;
    <span style="color:#fde68a">⑤毛利率&gt;30%</span>
    &nbsp;|&nbsp; <span style="color:#94a3b8">資料來源：yfinance 6個月日線 + TWSE/TPEX Q1財報</span>
  </div>
  <!-- KPIs -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:16px">
    <div class="kpi-card" style="border-color:#c2410c"><div class="kpi-label">全市場分析</div><div class="kpi-value" id="dsTotal">—</div></div>
    <div class="kpi-card"><div class="kpi-label">有價格數據</div><div class="kpi-value" id="dsWithPrice">—</div></div>
    <div class="kpi-card" style="border-color:#22c55e"><div class="kpi-label">🚀 強力買進(5訊)</div><div class="kpi-value" style="color:#22c55e" id="dsStrong">—</div></div>
    <div class="kpi-card"><div class="kpi-label">📈 買進(3-4訊)</div><div class="kpi-value" style="color:#86efac" id="dsBull">—</div></div>
    <div class="kpi-card"><div class="kpi-label">📉 弱勢</div><div class="kpi-value" style="color:#f87171" id="dsWeak">—</div></div>
  </div>
  <!-- Sector DNA Heatmap -->
  <div style="margin-bottom:14px">
    <div class="card-title" style="margin-bottom:8px">產業DNA熱圖 (平均訊號數，點擊篩選產業)</div>
    <div id="dnaSecHeat" style="display:flex;flex-wrap:wrap;gap:6px"></div>
  </div>
  <!-- Filter bar -->
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
    <select id="dsMktFilter" onchange="renderDnaScreen()" style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px">
      <option value="all">全部市場</option><option value="TSE">TSE上市</option><option value="OTC">OTC上櫃</option>
    </select>
    <select id="dsSignalFilter" onchange="renderDnaScreen()" style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px">
      <option value="all">全部評級</option><option value="6">6訊號 🚀</option><option value="5">5訊號</option><option value="4">4訊號</option>
      <option value="3" selected>3訊號以上 📈</option><option value="weak">弱勢 📉</option>
    </select>
    <select id="dsSectorFilter" onchange="renderDnaScreen()" style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px">
      <option value="all">全部產業</option>
    </select>
    <input id="dsSearch" type="text" placeholder="代號/名稱搜尋" oninput="renderDnaScreen()"
      style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px;width:140px"/>
    <button onclick="dsResetFilters()" style="padding:4px 10px;border-radius:4px;background:#334155;color:#e2e8f0;border:none;cursor:pointer;font-size:12px">重置</button>
    <span id="dsCount" style="font-size:12px;color:#94a3b8"></span>
  </div>
  <!-- Main table -->
  <div class="card" style="overflow-x:auto;padding:8px">
    <table class="data-table" style="font-size:12px;min-width:900px">
      <thead>
        <tr>
          <th>#</th><th>代號</th><th>名稱</th><th>市場</th><th>產業</th>
          <th onclick="dsSort('bull_signs')" style="cursor:pointer">訊號▼</th>
          <th onclick="dsSort('mo_di1')"  style="cursor:pointer">月+DI(1)</th>
          <th onclick="dsSort('mo_rsi4')" style="cursor:pointer">月RSI(4)</th>
          <th onclick="dsSort('wr50')"    style="cursor:pointer">日W%R(50)</th>
          <th onclick="dsSort('rsi60')"   style="cursor:pointer">日RSI(60)</th>
          <th onclick="dsSort('wk_vr2')"  style="cursor:pointer">週VR(2)</th>
          <th onclick="dsSort('mo_vr2')"  style="cursor:pointer">月VR(2)</th>
          <th>評級</th>
        </tr>
      </thead>
      <tbody id="tbodyDnaScreen"></tbody>
    </table>
  </div>
</div><!-- /dnascreen -->

<!-- ═══════════════════════════════════════════════════ STRATEGY SYSTEM ═ -->
<div id="page-strategy" class="page">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
    <h2 style="margin:0;color:#7c3aed">🎯 操作策略系統</h2>
    <span id="stratDate" style="font-size:12px;color:#94a3b8"></span>
  </div>

  <!-- Sub-tabs -->
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px;border-bottom:1px solid #334155;padding-bottom:10px">
    <button class="sub-tab active" onclick="showStratTab(this,'strat-n2')">① 大盤轉折 N2</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-macd')">② MACD 4箭頭</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-capital')">③ 資金配置</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-sector')">④ 族群訊號</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-rocket')">⑤ 飆股訊號</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-entry')">⑥ 進場訊號</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-buy')">⑦ 買進模組</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-sell')">⑧ 出場訊號</button>
    <button class="sub-tab" onclick="showStratTab(this,'strat-crisis')">⑨ 危機出場</button>
  </div>

  <!-- ① 大盤轉折 N2 -->
  <div id="strat-n2" class="strat-panel active">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:20px">
      <div class="kpi-card" style="border-color:#7c3aed">
        <div class="kpi-label">TAIEX 最新收盤</div>
        <div class="kpi-value" id="stN2Close" style="color:#e2e8f0">—</div>
        <div class="kpi-sub" id="stN2Date">—</div>
      </div>
      <div class="kpi-card" style="border-color:#7c3aed">
        <div class="kpi-label">N2 轉折點</div>
        <div class="kpi-value" id="stN2Val" style="color:#a78bfa">—</div>
        <div class="kpi-sub">2個月高低點中線</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">待機區間</div>
        <div class="kpi-value" id="stN2Standby" style="color:#fbbf24">—</div>
        <div class="kpi-sub">N2 − 100 點</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">多空判定</div>
        <div class="kpi-value" id="stN2Trend" style="color:#22c55e">—</div>
        <div class="kpi-sub" id="stN2Zone">—</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">2個月最高</div>
        <div class="kpi-value" id="stN2High" style="color:#f87171">—</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">2個月最低</div>
        <div class="kpi-value" id="stN2Low" style="color:#34d399">—</div>
      </div>
    </div>
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:10px">N2 計算說明</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.7">
        <b style="color:#a78bfa">N2公式：</b>N2 = (近2個月TAIEX最高點 + 近2個月最低點) ÷ 2<br>
        <b style="color:#fbbf24">待機區：</b>N2 − 100 ~ N2 之間為待機區，等待訊號進場<br>
        <b style="color:#22c55e">多頭確認：</b>大盤收盤 > N2 → 多頭格局，可積極操作<br>
        <b style="color:#f87171">空頭警示：</b>大盤收盤 &lt; N2 → 空頭格局，保守觀望<br>
        <b style="color:#60a5fa">進場時機：</b>收盤進入待機區且有其他訊號配合 → 分批買進
      </div>
    </div>
    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:8px">近60日 TAIEX 走勢 (含N2/待機區)</div>
      <canvas id="stTaiexChart" style="width:100%;height:220px;display:block"></canvas>
    </div>
  </div>

  <!-- ② MACD 4箭頭 -->
  <div id="strat-macd" class="strat-panel">
    <!-- Live TAIEX MACD status -->
    <div id="stratMacdStatus" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:16px"></div>
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">MACD 4箭頭系統說明</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div style="background:#1e0a3c;border:1px solid #7c3aed;border-radius:8px;padding:14px">
          <div style="color:#a78bfa;font-weight:700;margin-bottom:8px">📊 短線 MACD (9/12/26)</div>
          <div style="font-size:13px;color:#e2e8f0;line-height:1.8">
            <span style="color:#22c55e">↑ 箭頭①：</span>DIF 由下往上穿越0軸<br>
            <span style="color:#86efac">↑ 箭頭②：</span>DIF 上穿 DEA (金叉)<br>
            <span style="color:#f87171">↓ 箭頭③：</span>DIF 由上往下穿越0軸<br>
            <span style="color:#fca5a5">↓ 箭頭④：</span>DIF 下穿 DEA (死叉)
          </div>
        </div>
        <div style="background:#1e0a3c;border:1px solid #4c1d95;border-radius:8px;padding:14px">
          <div style="color:#c4b5fd;font-weight:700;margin-bottom:8px">📈 長線 MACD (200/209/210)</div>
          <div style="font-size:13px;color:#e2e8f0;line-height:1.8">
            <span style="color:#22c55e">↑ 箭頭①：</span>DIF210 由下往上穿越0軸 (重要!)<br>
            <span style="color:#86efac">↑ 箭頭②：</span>DIF210 上穿 DEA210 (金叉)<br>
            <span style="color:#f87171">↓ 箭頭③：</span>DIF210 由上往下穿越0軸<br>
            <span style="color:#fca5a5">↓ 箭頭④：</span>DIF210 下穿 DEA210 (死叉)
          </div>
        </div>
      </div>
      <div style="margin-top:14px;padding:12px;background:#0f1a0a;border:1px solid #166534;border-radius:8px">
        <div style="color:#4ade80;font-weight:700;margin-bottom:6px">🌀 螺旋式攻擊 (DIF210)</div>
        <div style="font-size:12px;color:#94a3b8;line-height:1.6">
          DIF210 形成「螺旋式攻擊」：每波底部(谷)逐漸升高，且DIF值持續上升向正值。<br>
          此形態出現時為最強飆股訊號，搭配ADX300>25可確認多頭強度。
        </div>
      </div>
    </div>
  </div>

  <!-- ③ 資金配置 -->
  <div id="strat-capital" class="strat-panel">
    <!-- Live W%R gauges -->
    <div id="stratCapitalGauges" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px"></div>
    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:12px">月威廉W%R(3) 資金配置準則</div>
      <div style="overflow-x:auto">
        <table class="data-table" style="font-size:12px">
          <thead><tr><th>指數/類型</th><th>W%R(3)範圍</th><th>強度判定</th><th>資金配置</th></tr></thead>
          <tbody>
            <tr><td>大型股 (0050/006208)</td><td style="color:#f87171">&gt; −20</td><td style="color:#f87171">強勢/超買</td><td>減倉，部分獲利了結</td></tr>
            <tr><td>大型股 (0050/006208)</td><td style="color:#fbbf24">−20 ~ −50</td><td style="color:#fbbf24">中性</td><td>標準倉，持有觀察</td></tr>
            <tr><td>大型股 (0050/006208)</td><td style="color:#22c55e">−50 ~ −80</td><td style="color:#22c55e">偏弱</td><td>可加碼，逢低分批</td></tr>
            <tr><td>大型股 (0050/006208)</td><td style="color:#86efac">&lt; −80</td><td style="color:#86efac">超賣</td><td>重倉買進</td></tr>
            <tr style="background:#0f1a0a"><td>中小型股</td><td style="color:#86efac">&lt; −80</td><td style="color:#86efac">超賣</td><td>積極買進，≤5%單筆</td></tr>
            <tr style="background:#0f1a0a"><td>金融股 (0055)</td><td style="color:#86efac">&lt; −80</td><td style="color:#86efac">超賣</td><td>買進 (需月RSI4&gt;50)</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ④ 族群訊號 -->
  <div id="strat-sector" class="strat-panel">
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">族群訊號確認</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:14px">
        進場個股前，需確認所屬族群亦出現多頭訊號，族群強度決定持倉比重。
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div style="padding:12px;background:#0f172a;border:1px solid #1e40af;border-radius:8px">
          <div style="color:#60a5fa;font-weight:700;margin-bottom:6px">族群多頭條件</div>
          <div style="font-size:13px;color:#e2e8f0;line-height:1.7">
            ✅ 族群ETF DIF (9,12,26) 箭頭①或②<br>
            ✅ 族群月RSI(4) &gt; 77<br>
            ✅ 族群中≥3支個股有②飆股訊號<br>
            → 族群強度 HIGH，滿倉操作
          </div>
        </div>
        <div style="padding:12px;background:#0f172a;border:1px solid #334155;border-radius:8px">
          <div style="color:#94a3b8;font-weight:700;margin-bottom:6px">族群弱勢條件</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.7">
            ❌ 族群ETF DIF 箭頭③或④<br>
            ❌ 族群月RSI(4) &lt; 50<br>
            ❌ 族群中&lt;1支個股有飆股訊號<br>
            → 族群強度 LOW，觀望或空手
          </div>
        </div>
      </div>
    </div>
    <!-- Sector heatmap using existing DNA data -->
    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:8px">產業族群 月RSI(4) 排行</div>
      <div id="stratSectorTable" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- ⑤ 飆股訊號 -->
  <div id="strat-rocket" class="strat-panel">
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">飆股訊號 — 螺旋攻擊 + ADX確認</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
        <div style="background:#1a0a3c;border:1px solid #7c3aed;border-radius:8px;padding:14px">
          <div style="color:#a78bfa;font-weight:700;margin-bottom:8px">🌀 DIF210 螺旋攻擊</div>
          <div style="font-size:13px;color:#e2e8f0;line-height:1.7">
            每次回調DIF210高點逐漸上升<br>
            DIF210 同時收斂向上 (區間縮小)<br>
            最後突破前高 → 飆股啟動<br>
            <span style="color:#fbbf24">通常在EPS加速成長期出現</span>
          </div>
        </div>
        <div style="background:#0f1a0a;border:1px solid #166534;border-radius:8px;padding:14px">
          <div style="color:#4ade80;font-weight:700;margin-bottom:8px">📐 ADX300 螺旋</div>
          <div style="font-size:13px;color:#e2e8f0;line-height:1.7">
            ADX(300) &gt; 25 → 趨勢確立<br>
            +DI(300) &gt; −DI(300) → 多頭排列<br>
            螺旋條件：ADX持續上升 + +DI擴張<br>
            <span style="color:#fbbf24">配合DIF210螺旋勝率最高</span>
          </div>
        </div>
      </div>
    </div>
    <!-- Top rocket candidates using existing DNA data -->
    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:8px">飆股候選 (6訊號 + 高月RSI)</div>
      <div id="stratRocketTable" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- ⑥ 進場訊號 -->
  <div id="strat-entry" class="strat-panel">
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">進場訊號 — 4種觸發條件</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px">
        <div style="padding:12px;background:#0f172a;border:1px solid #0369a1;border-radius:8px">
          <div style="color:#38bdf8;font-weight:700;margin-bottom:6px">A. 60分RSI(60)觸底</div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.6">
            60分鐘RSI(60) &lt; 34 → 短線超賣<br>
            搭配日線訊號確認<br>
            適合短波段操作 1-3日
          </div>
        </div>
        <div style="padding:12px;background:#0f172a;border:1px solid #0369a1;border-radius:8px">
          <div style="color:#38bdf8;font-weight:700;margin-bottom:6px">B. 週線轉折點</div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.6">
            週K出現底部反轉K線型態<br>
            週RSI(4) 從低點回升 &gt; 30<br>
            適合中波段 2-4週
          </div>
        </div>
        <div style="padding:12px;background:#0f172a;border:1px solid #0369a1;border-radius:8px">
          <div style="color:#38bdf8;font-weight:700;margin-bottom:6px">C. 日線MACD頂底</div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.6">
            日線MACD(9,12,26) 底部背離<br>
            DIF &gt; DEA (金叉)<br>
            適合波段操作 1-3個月
          </div>
        </div>
        <div style="padding:12px;background:#0f172a;border:1px solid #0369a1;border-radius:8px">
          <div style="color:#38bdf8;font-weight:700;margin-bottom:6px">D. 月線黑K+6K買點</div>
          <div style="font-size:12px;color:#94a3b8;line-height:1.6">
            月K出現黑K(陰線)後，下月轉紅<br>
            搭配6K線(6個月MA)支撐<br>
            長線佈局，持有3-12個月
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ⑦ 買進模組 -->
  <div id="strat-buy" class="strat-panel">
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
      <select id="stratBuyMin" onchange="renderStratBuy()" style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px">
        <option value="3">3條件以上</option>
        <option value="4">4條件以上</option>
        <option value="5">5條件以上</option>
        <option value="6">6條件以上</option>
      </select>
      <input id="stratBuySearch" type="text" placeholder="代號/名稱" oninput="renderStratBuy()"
        style="padding:4px 8px;border-radius:4px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:12px;width:120px"/>
      <button onclick="document.getElementById('stratBuyMin').value=3;document.getElementById('stratBuySearch').value='';renderStratBuy()"
        style="padding:4px 10px;border-radius:4px;background:#334155;color:#e2e8f0;border:none;cursor:pointer;font-size:12px">重置</button>
      <span id="stratBuyCount" style="font-size:12px;color:#94a3b8"></span>
    </div>
    <div class="card" style="padding:8px;overflow-x:auto">
      <table class="data-table" style="font-size:11px;min-width:900px">
        <thead>
          <tr>
            <th>#</th><th>代號</th><th>名稱</th>
            <th title="月+DI(1)>50">①月+DI</th>
            <th title="月RSI(4)>77">②月RSI</th>
            <th title="日W%R(50)<20">③日W%R</th>
            <th title="日RSI(60)>57">④日RSI</th>
            <th title="週VR(2)≥150">⑤週VR</th>
            <th title="月VR(2)≥150">⑥月VR</th>
            <th title="DIF210螺旋 (計算中)">⑦DIF210</th>
            <th title="ADX300螺旋 (計算中)">⑧ADX300</th>
            <th title="進場確認條件">⑨進場</th>
            <th>條件</th><th>評級</th>
          </tr>
        </thead>
        <tbody id="tbodyStratBuy"></tbody>
      </table>
    </div>
  </div>

  <!-- ⑧ 出場訊號 -->
  <div id="strat-sell" class="strat-panel">
    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">⑧ 出場訊號系統</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:16px">
        <div style="padding:12px;background:#1a0404;border:1px solid #991b1b;border-radius:8px">
          <div style="color:#f87171;font-weight:700;margin-bottom:6px">賣出條件一</div>
          <div style="font-size:12px;color:#fca5a5;line-height:1.6">
            月威廉W%R(3) &gt; −50<br>
            (月線接近超買區域)
          </div>
        </div>
        <div style="padding:12px;background:#1a0404;border:1px solid #991b1b;border-radius:8px">
          <div style="color:#f87171;font-weight:700;margin-bottom:6px">賣出條件二</div>
          <div style="font-size:12px;color:#fca5a5;line-height:1.6">
            月RSI(4) &lt; 77 且從高點回落<br>
            (月RSI超買後轉折向下)
          </div>
        </div>
        <div style="padding:12px;background:#1a0404;border:1px solid #991b1b;border-radius:8px">
          <div style="color:#f87171;font-weight:700;margin-bottom:6px">賣出條件三</div>
          <div style="font-size:12px;color:#fca5a5;line-height:1.6">
            DIF210 由正轉負 (箭頭③)<br>
            (長線趨勢終止)
          </div>
        </div>
        <div style="padding:12px;background:#1a0404;border:1px solid #991b1b;border-radius:8px">
          <div style="color:#f87171;font-weight:700;margin-bottom:6px">9K線賣出</div>
          <div style="font-size:12px;color:#fca5a5;line-height:1.6">
            9個月均線出現死叉<br>
            或月K跌破9K支撐
          </div>
        </div>
      </div>
    </div>
    <!-- Stocks approaching sell signal -->
    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:8px">接近出場訊號個股 (月RSI>70 高位)</div>
      <div id="stratSellTable" style="overflow-x:auto"></div>
    </div>
  </div>

  <!-- ⑨ 危機出場 -->
  <div id="strat-crisis" class="strat-panel">
    <!-- 6K/9K Live Count Banner -->
    <div id="strat6k9kBanner" style="margin-bottom:14px"></div>

    <div class="card" style="padding:16px;margin-bottom:14px">
      <div class="card-title" style="margin-bottom:12px">大盤月線 6K/9K 計數</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:14px">
        <div class="kpi-card" id="strat6kCard">
          <div class="kpi-label">連續紅K計數</div>
          <div class="kpi-value" id="strat6kCount" style="color:#fbbf24">—</div>
          <div class="kpi-sub">目前有效紅K數</div>
        </div>
        <div class="kpi-card" id="strat6kSigCard">
          <div class="kpi-label">6K 賣出訊號</div>
          <div class="kpi-value" id="strat6kSig" style="color:#94a3b8">—</div>
          <div class="kpi-sub">≥6根 → 清倉</div>
        </div>
        <div class="kpi-card" id="strat9kSigCard">
          <div class="kpi-label">9K 賣出訊號</div>
          <div class="kpi-value" id="strat9kSig" style="color:#94a3b8">—</div>
          <div class="kpi-sub">≥9根 → 強制出場</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">下跌型黑K計數</div>
          <div class="kpi-value" id="stratBlack6kCount" style="color:#22c55e">—</div>
          <div class="kpi-sub">≥6根 → 探底買點</div>
        </div>
      </div>

      <!-- 6K Rules -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
        <div style="background:#1a0a00;border:1px solid #c2410c;border-radius:8px;padding:12px">
          <div style="color:#fb923c;font-weight:700;margin-bottom:6px">6K/9K 計數規則</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.7">
            ✅ 第一根紅K突破下降K線最高點<br>
            ✅ 每根紅K收盤 > 前有效K最高點<br>
            ✅ 6K：每根紅K漲幅 > 300點<br>
            ✅ 9K：無漲幅限制<br>
            ❌ 內含K無效 (高&lt;=前高 且 低>=前低)<br>
            ❌ 任何K跌破前K低點 → 重算<br>
            🔴 黑K不計入，但監控低點
          </div>
        </div>
        <div style="background:#0f1a0a;border:1px solid #166534;border-radius:8px;padding:12px">
          <div style="color:#4ade80;font-weight:700;margin-bottom:6px">下跌型黑6K (買點)</div>
          <div style="font-size:11px;color:#94a3b8;line-height:1.7">
            ✅ 第一根黑K跌破上升K最低點<br>
            ✅ 每根黑K收盤 &lt; 前有效K最低點<br>
            ✅ 每根黑K跌幅 > 300點<br>
            ❌ 內含K無效<br>
            ❌ 任何K突破前K高點 → 重算<br>
            🟢 第6根黑K成立 → 逢低分批買進
          </div>
        </div>
      </div>

      <!-- Monthly K-line chart -->
      <div class="card-title" style="margin-bottom:6px">近24個月 TAIEX 月線圖 (紅鏈標記)</div>
      <canvas id="strat6kChart" style="width:100%;height:200px;display:block;background:#0f172a;border-radius:8px"></canvas>
    </div>

    <div class="card" style="padding:16px">
      <div class="card-title" style="margin-bottom:8px">大盤危機監測 (N2防線)</div>
      <div style="font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:12px">
        TAIEX 目前在 N2 <span id="stratCrisisAbove" style="color:#22c55e">之上</span>，整體多頭格局完整。<br>
        監測重點：①TAIEX跌破N2 → 待機；②跌破N2-300 → 防禦；③跌破N2-600 → 危機出場
      </div>
      <div id="strat-n2-crisis" style="padding:12px;border-radius:8px;margin-bottom:12px"></div>
      <div id="stratCrisisLevels" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px"></div>
    </div>
  </div>
</div><!-- /strategy -->

<!-- DNA Screen modal overlay -->
<div id="dsModal" onclick="if(event.target===this)closeDsModal()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:9000;overflow-y:auto;padding:24px 12px">
  <div style="max-width:900px;margin:0 auto;background:#1a0a00;border:1px solid #c2410c;border-radius:12px;padding:22px;position:relative">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
      <div id="dsDetailHeader" style="font-size:18px;font-weight:700;color:#fb923c;flex:1;padding-right:12px"></div>
      <button onclick="closeDsModal()" style="background:#334155;color:#e2e8f0;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:15px;flex-shrink:0">✕</button>
    </div>
    <div id="dsDetailBody"></div>
  </div>
</div>

<!-- ════════════════════════ DNA TRIGGER CALCULATOR ════════════════════ -->
<div id="page-dnatrigger" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">⚡ DNA升評觸發計算</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">4/6和5/6股票升評至6/6(TRIPLE)所需的觸發條件與目標價位。S3觸發最易靠價格行動實現。</p>
  <div class="kpi-row" id="dtKpis"></div>
  <div class="card" style="margin-bottom:12px"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px;color:#dc2626">🔥 P1 — 周一重點監控 (接近TRIPLE / 即將升評)</div>
    <p style="font-size:12px;color:#94a3b8;margin-bottom:10px">S3信號差距 ≤ 2% — 周一任何正面開盤即可觸發</p>
    <div id="dtP1List"></div>
  </div></div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全部 4/6 + 5/6 升評路徑</div>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th>
        <th style="text-align:center">現在</th><th>缺失信號</th>
        <th style="text-align:right">S3觸發價</th><th style="text-align:right">需漲%</th>
        <th>難度</th><th>周一優先</th><th>Grand</th>
      </tr></thead>
      <tbody id="dtAllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /dnatrigger -->


<!-- ═══════════════════════════════════════════════════ BACKTEST ═══ -->
<div id="page-backtest" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#134e4a,#065f46);border-color:#34d399">
    <div class="alert-title" style="color:#fff">🔬 大飆股DNA 回測驗證 — 2年歷史數據</div>
    <div class="alert-body" style="color:#a7f3d0">702次觸發訊號 | 進場條件: bull_signs≥2 + MACD/MA core≥1 | 最小間隔20交易日</div>
  </div>

  <!-- Aggregate stats -->
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px" id="btAggCards"></div>

  <!-- Per-stock backtest table -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 各股DNA訊號回測績效 (按20日平均報酬排序)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>#</th><th>代號</th><th>名稱</th><th>訊號次數</th>
        <th>10日均報</th><th>10日勝率</th>
        <th>20日均報</th><th>20日勝率</th>
        <th>60日均報</th><th>60日勝率</th>
        <th>目前狀態</th>
      </tr></thead>
      <tbody id="tbodyBacktest"></tbody>
    </table></div>
  </div>

  <!-- Highlight: stocks currently signaling with strong backtest -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🎯 現在發出訊號 × 歷史高勝率 (最佳進場時機)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>歷史20日均報</th><th>歷史勝率</th><th>訊號次數</th><th>目前DNA</th>
      </tr></thead>
      <tbody id="tbodyBtNow"></tbody>
    </table></div>
  </div>
</div><!-- /backtest -->

<!-- ═══════════════════════════════════════════ SOP BACKTEST ═══ -->
<div id="page-sopbacktest" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#78350f,#92400e);border-color:#fbbf24">
    <div class="alert-title" style="color:#fef3c7">📈 DNA 大飆股 SOP — 三年回測模擬 (2023-01-01 → {TODAY})</div>
    <div class="alert-body" style="color:#fde68a">進場: TAIEX N2候補區 + 日W%R(50)&lt;20 + 日RSI(60)&gt;57 + MACD多頭 | 出場: 月W%R(3)&gt;50全出 / 月RSI(4)&lt;77減倉50%×2</div>
  </div>

  <!-- Capital toggle -->
  <div style="display:flex;gap:8px;margin-bottom:16px;align-items:center">
    <span style="color:#94a3b8;font-size:13px">顯示資金:</span>
    <button id="sopCapBtn1m" onclick="sopShowCap('1m')" class="btn btn-sm" style="background:#1e40af;color:#fff;border:none;padding:6px 16px;border-radius:6px;cursor:pointer">初始 100萬</button>
    <button id="sopCapBtn2m" onclick="sopShowCap('2m')" class="btn btn-sm" style="background:#1e293b;color:#94a3b8;border:1px solid #334155;padding:6px 16px;border-radius:6px;cursor:pointer">初始 200萬</button>
    <span id="sopDisclaimer" style="font-size:11px;color:#64748b;margin-left:8px"></span>
  </div>

  <!-- KPI cards -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px" id="sopKpiCards"></div>

  <!-- Equity chart -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #1e293b">
      <div class="section-title">📊 資金曲線</div>
    </div>
    <div id="sopChartEl" style="width:100%;height:300px;background:#0c1220;border-radius:0 0 8px 8px"></div>
  </div>

  <!-- Gap analysis -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #1e293b">
      <div class="section-title">🔍 策略差異對比 — 現行DNA系統 vs SOP進出場規範</div>
    </div>
    <div id="sopGapTable" style="padding:12px"></div>
  </div>

  <!-- Signal compatibility -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #1e293b">
      <div class="section-title">✅ 信號對應分析</div>
    </div>
    <div id="sopMatchTable" style="padding:12px"></div>
  </div>

  <!-- Monthly returns heatmap -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #1e293b">
      <div class="section-title">📅 月度損益</div>
    </div>
    <div id="sopMonthlyGrid" style="padding:12px;display:flex;flex-wrap:wrap;gap:6px"></div>
  </div>

  <!-- Trade log -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #1e293b">
      <div class="section-title">📋 交易明細 (最近100筆)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>進場日</th><th>進場價</th>
        <th>出場日</th><th>出場價</th><th>股數</th><th>損益(TWD)</th><th>損益%</th><th>出場原因</th>
      </tr></thead>
      <tbody id="sopTradesTbody"></tbody>
    </table></div>
  </div>
</div><!-- /sopbacktest -->

<!-- ═══════════════════════════════════════════════════ REL STRENGTH ═══ -->
<div id="page-relstrength" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#4c1d95,#5b21b6);border-color:#a78bfa">
    <div class="alert-title" style="color:#fff">📡 相對強度 vs 加權指數 (TAIEX)</div>
    <div class="alert-body" style="color:#ddd6fe">60日超額報酬 | DNA訊號疊加 | 個股相關性矩陣 (持倉集中風險)</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px" id="rsMetaCards"></div>

  <!-- DNA + RS combo — best setup -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🎯 DNA訊號 + 正相對強度 (最佳進場組合)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>60日報酬</th><th>60日超額RS</th><th>20日超額</th>
        <th>DNA跡象</th><th>52週高點距離</th><th>判定</th>
      </tr></thead>
      <tbody id="tbodyDnaRs"></tbody></table>
    </div>
  </div>

  <!-- Full RS table -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📊 全部股票相對強度排名 (60日)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>#</th><th>代號</th><th>名稱</th><th>股票60日</th><th>指數60日</th>
        <th>超額RS</th><th>20日超額</th><th>52週高%</th><th>綜合排名</th>
      </tr></thead>
      <tbody id="tbodyAllRs"></tbody></table>
    </div>
  </div>

  <!-- Correlation warning -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⚠️ 高相關股票對 (持倉集中風險 r > 0.70)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>股票A</th><th>名稱A</th><th>股票B</th><th>名稱B</th><th>相關係數</th><th>風險提示</th>
      </tr></thead>
      <tbody id="tbodyCorrPairs"></tbody></table>
    </div>
  </div>
</div><!-- /relstrength -->

<!-- ═══════════════════════════════════════════════════ PORT OPT ═══ -->
<div id="page-portopt" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#0f172a,#1e3a5f);border-color:#38bdf8">
    <b>🎯 最佳化投資組合</b> — 50,000次蒙地卡羅模擬 × 20支優選標的 | 均值-變異數最佳化
  </div>

  <!-- Strategy Selector -->
  <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap" id="portStratBtns"></div>

  <!-- KPI cards -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px" id="portKpiCards"></div>

  <!-- Efficient Frontier chart -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">📉 效率前緣 (Efficient Frontier)</div>
    <div style="height:200px;position:relative" id="efChart">
      <canvas id="efCanvas" style="width:100%;height:200px"></canvas>
    </div>
  </div>

  <!-- Allocation table -->
  <div class="card">
    <div class="card-title">📊 持股比重建議</div>
    <table class="data-table">
      <thead><tr>
        <th>代碼</th><th>名稱</th><th>建議比重</th><th>預期報酬</th>
        <th>波動率</th><th>信念分</th><th>DNA訊號</th><th>建議</th>
      </tr></thead>
      <tbody id="tbodyPortAlloc"></tbody>
    </table>
  </div>

  <!-- Concentration risk -->
  <div class="card" style="margin-top:16px">
    <div class="card-title">⚠️ 集中度風險 (r&gt;0.7 同組標的)</div>
    <table class="data-table">
      <thead><tr><th>標的A</th><th>名稱</th><th>標的B</th><th>名稱</th><th>相關係數</th><th>風險提示</th></tr></thead>
      <tbody id="tbodyPortRisk"></tbody>
    </table>
  </div>
</div><!-- /portopt -->


<!-- ═══════════════════════════════════════════════════ WATCH ALERTS ═══ -->
<div id="page-watchalerts" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#fb7185;color:#881337">
    <b>🔔 監控警示</b> — 即將突破 · 一步之遙 · 動能轉折 · 52週高點突破
  </div>

  <!-- Summary chips -->
  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px" id="alertChips"></div>

  <!-- A: Almost TRIPLE -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">🚀 即將達成 TRIPLE CONFIRMED（差距 &lt;8分）</div>
    <table class="data-table">
      <thead><tr><th>代碼</th><th>名稱</th><th>信念分</th><th>差距</th><th>DNA</th><th>PE</th><th>殖利率</th><th>現況</th><th>達標條件</th></tr></thead>
      <tbody id="tbodyAlmostTriple"></tbody>
    </table>
  </div>

  <!-- B: DNA 5/6 -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">🧬 DNA 5/6 訊號（差一個就滿分）</div>
    <table class="data-table">
      <thead><tr><th>代碼</th><th>名稱</th><th>DNA</th><th>缺少訊號</th><th>信念分</th><th>現況</th></tr></thead>
      <tbody id="tbodyDna5of6"></tbody>
    </table>
  </div>

  <!-- C: MA Crossing -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">📈 突破月均線 — 動能由空轉多</div>
    <table class="data-table">
      <thead><tr><th>代碼</th><th>名稱</th><th>收盤</th><th>月均</th><th>距均線</th><th>趨勢</th><th>信念分</th><th>現況</th></tr></thead>
      <tbody id="tbodyMaCross"></tbody>
    </table>
  </div>

  <!-- D: Near 52w High -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">🏔 創52週新高 + 強勢相對強度</div>
    <table class="data-table">
      <thead><tr><th>代碼</th><th>名稱</th><th>距52週高</th><th>60日RS</th><th>60日漲幅</th><th>DNA</th><th>信念分</th><th>現況</th></tr></thead>
      <tbody id="tbodyNear52w"></tbody>
    </table>
  </div>

  <!-- E: TRIPLE upside -->
  <div class="card">
    <div class="card-title">💎 TRIPLE CONFIRMED — 基本面快照</div>
    <table class="data-table">
      <thead><tr><th>代碼</th><th>名稱</th><th>信念分</th><th>DNA</th><th>PE</th><th>殖利率</th><th>RS60</th><th>目標上漲空間</th></tr></thead>
      <tbody id="tbodyTripleSnap"></tbody>
    </table>
  </div>
</div><!-- /watchalerts -->

<!-- ═══════════════════════════════════════════════════ MAY PREVIEW ═══ -->
<div id="page-maypreview" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#ecfdf5,#f0fdf4);border-color:#34d399;color:#064e3b">
    <b>📅 {REVENUE_MONTH_LABEL}營收預告</b> — 基於前月數據推算 | 預計發布日期: {REVENUE_DATE}
  </div>

  <!-- Summary chips -->
  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px" id="mayChips"></div>

  <!-- TRIPLE CONFIRMED preview spotlight -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">💎 TRIPLE CONFIRMED — 5月營收展望</div>
    <table class="data-table">
      <thead><tr>
        <th>代碼</th><th>名稱</th><th>4月YoY</th><th>累積YoY</th><th>月增率</th>
        <th>加速趨勢</th><th>5月預估(億)</th><th>展望</th>
      </tr></thead>
      <tbody id="tbodyTriplePreview"></tbody>
    </table>
  </div>

  <!-- Beat candidates -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">🔥 超預期強勢候選 (score ≥ 4)</div>
    <table class="data-table">
      <thead><tr>
        <th>代碼</th><th>名稱</th><th>4月YoY</th><th>月增率</th><th>加速趨勢</th>
        <th>信念分</th><th>DNA</th><th>展望</th>
      </tr></thead>
      <tbody id="tbodyBeatCandidates"></tbody>
    </table>
  </div>

  <!-- Miss risks -->
  <div class="card">
    <div class="card-title">⚠️ 注意衰退風險</div>
    <table class="data-table">
      <thead><tr>
        <th>代碼</th><th>名稱</th><th>4月YoY</th><th>月增率</th><th>加速趨勢</th>
        <th>信念分</th><th>展望</th>
      </tr></thead>
      <tbody id="tbodyMissRisks"></tbody>
    </table>
  </div>
</div><!-- /maypreview -->

<!-- ═══════════════════════════════════════════════════ TRIPLE REPORT ═══ -->
<div id="page-triplereport" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#7f1d1d,#991b1b);border-color:#f87171;color:#fef2f2">
    <b>💎 TRIPLE CONFIRMED 精析</b> — 綜合得分 ≥70 × DNA訊號 ≥3 × 全方位盡職調查
  </div>
  <div id="tripleCardsContainer"></div>
</div><!-- /triplereport -->

<!-- ═══════════════════════════════════════════════════ ETF COMPARE ═══ -->
<div id="page-etfcompare" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#e0f2fe,#f0f9ff);border-color:#38bdf8;color:#0c4a6e">
    <b>🗂 ETF比較分析</b> — 0050 / 0056 / 006208 / 00713 / 00878 — 基於個股信念分加權計算
  </div>

  <!-- ETF scorecards -->
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-bottom:20px"
       id="etfScorecards"></div>

  <!-- Comparison table -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">📊 ETF綜合比較</div>
    <table class="data-table">
      <thead><tr>
        <th>ETF</th><th>名稱</th><th>主題</th><th>成分數</th>
        <th>加權信念分</th><th>加權DNA</th><th>加權PE</th><th>加權殖利率</th>
        <th>RS60</th><th>均線上方%</th><th>TRIPLE數</th><th>評級</th>
      </tr></thead>
      <tbody id="tbodyEtfCompare"></tbody>
    </table>
  </div>

  <!-- Selected ETF holdings -->
  <div class="card" id="etfHoldingsCard" style="display:none">
    <div class="card-title" id="etfHoldingsTitle">點擊ETF查看成分股</div>
    <table class="data-table">
      <thead><tr>
        <th>權重</th><th>代碼</th><th>名稱</th><th>信念分</th>
        <th>DNA</th><th>PE</th><th>殖利率</th><th>建議</th>
      </tr></thead>
      <tbody id="tbodyEtfHoldings"></tbody>
    </table>
  </div>

  <!-- Q1 2026 Financial Report -->
  <div class="card" style="margin-bottom:16px;margin-top:20px">
    <div class="card-title">📈 Q1 2026 財務報告比較</div>
    <table class="data-table">
      <thead><tr>
        <th>ETF</th><th>成分數</th><th>EPS涵蓋</th><th>平均Q1 EPS</th>
        <th>平均PE</th><th>平均殖利率</th><th>平均營收YoY</th><th>TRIPLE數</th><th>BUY數</th>
      </tr></thead>
      <tbody id="tbodyEtfQ1"></tbody>
    </table>
  </div>

  <!-- Q1 Top Performers per ETF -->
  <div id="etfQ1TopGrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin-bottom:20px"></div>
</div><!-- /etfcompare -->

<!-- ══════════════════════════════════════════════════ OTC ANALYSIS ═══ -->
<div id="page-otcanalysis" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#22c55e;color:#14532d">
    <b>🟢 上櫃市場分析 (OTC)</b> — 887 家 TPEX 上櫃公司 Q1 2026 財務報告
    · 資料來源: TPEX t187ap14_O + t187ap06_O_ci + t187ap05_O
  </div>

  <!-- KPIs -->
  <div class="kpi-row" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr));margin-bottom:16px" id="otcKpis"></div>

  <!-- Sector table -->
  <div class="card" style="margin-bottom:16px">
    <div class="card-title">📊 上櫃產業別 Q1 2026（按中位EPS排序）</div>
    <table class="data-table">
      <thead><tr>
        <th>產業</th><th>家數</th><th>獲利家數</th><th>獲利率</th>
        <th>中位Q1 EPS</th><th>中位營收YoY</th><th>中位毛利率</th><th>代表股票</th>
      </tr></thead>
      <tbody id="tbodyOtcSectors"></tbody>
    </table>
  </div>

  <!-- Top performers grid -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px;margin-bottom:16px">
    <div class="card card-pad">
      <div class="card-title">🏆 Q1 EPS Top 15</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>#</th><th>代號</th><th>名稱</th><th>EPS</th><th>毛利率</th></tr></thead>
        <tbody id="tbodyOtcTopEps"></tbody>
      </table>
    </div>
    <div class="card card-pad">
      <div class="card-title">💹 毛利率 Top 15（營收>5000萬）</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>#</th><th>代號</th><th>名稱</th><th>毛利率</th><th>EPS</th></tr></thead>
        <tbody id="tbodyOtcTopGm"></tbody>
      </table>
    </div>
    <div class="card card-pad">
      <div class="card-title">📈 4月營收YoY Top 15</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>#</th><th>代號</th><th>名稱</th><th>YoY%</th><th>EPS</th></tr></thead>
        <tbody id="tbodyOtcTopYoy"></tbody>
      </table>
    </div>
  </div>
</div><!-- /otcanalysis -->


<!-- ══════════════════════════════════════════════════ STOCK DETAIL ═══ -->
<div id="page-stockdetail" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border-color:#8b5cf6;color:#4c1d95">
    <b>📋 個股詳情</b> — 62 支 ETF 成分股完整分析報告 · 包含基本面、技術DNA、相對強度、回測驗證
  </div>
  <div class="card" style="margin-bottom:16px">
    <div class="card-pad" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;background:#f8fafc">
      <input id="sdSearch" placeholder="搜尋股票代號或名稱…" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px;width:200px"/>
      <select id="sdSelect" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px;min-width:200px"></select>
      <span style="font-size:12px;color:#94a3b8">← 選擇股票後顯示完整報告</span>
    </div>
  </div>
  <div id="sdPanel">
    <div style="text-align:center;color:#94a3b8;padding:40px">載入中…</div>
  </div>
</div><!-- /stockdetail -->

<!-- ══════════════════════════════════════════════════ CATALYST ═══ -->
<div id="page-catalyst" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fff8f1,#fff7ed);border-color:#fb923c;color:#9a3412">
    <b>📅 催化劑日曆</b> — 30 支股票 · 52 個個股事件 · 13 個總體事件 | 追蹤未來觸發點
  </div>

  <!-- KPI strip -->
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px" id="catKpis"></div>

  <!-- Filter -->
  <div class="card" style="margin-bottom:12px">
    <div class="filter-bar">
      <label>篩選</label>
      <select id="catFilter">
        <option value="all">全部</option>
        <option value="stock">個股催化劑</option>
        <option value="macro">總體事件</option>
        <option value="CRITICAL">🚀 CRITICAL</option>
        <option value="HIGH">⚠️ HIGH</option>
        <option value="revenue">營收事件</option>
      </select>
      <label>月份</label>
      <select id="catMonth">
        <option value="all">全部月份</option>
        <option value="2026-06">6月</option>
        <option value="2026-07">7月</option>
        <option value="2026-08">8月以後</option>
      </select>
    </div>
  </div>

  <div id="catTimeline"></div>
</div><!-- /catalyst -->

<!-- ═══════════════════════════════════════════════════ SENSITIVITY ═══ -->
<div id="page-sensitivity" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fdf4ff,#fae8ff);border-color:#c084fc;color:#6b21a8">
    <b>🔑 升評路徑分析</b> — 每支股票距下一評級缺口、關鍵槓桿點、觸發條件
  </div>
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px" id="senKpis"></div>
  <div class="filter-bar card" style="margin-bottom:12px">
    <select id="senFilter" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px">
      <option value="near">🔥 近升評 (≤5pts)</option>
      <option value="range">📊 全部可升 (≤10pts)</option>
      <option value="all">所有股票</option>
      <option value="triple">升至TRIPLE路徑</option>
    </select>
    <select id="senLever" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px">
      <option value="all">所有槓桿</option>
      <option value="估值">估值槓桿</option>
      <option value="技術DNA">技術DNA槓桿</option>
      <option value="動能">動能槓桿</option>
      <option value="基本面">基本面槓桿</option>
      <option value="殖利率">殖利率槓桿</option>
    </select>
  </div>
  <div id="senList"></div>
</div><!-- /sensitivity -->

<!-- ══════════════════════════════════════════════════ PEER COMP ═══ -->
<div id="page-peercomp" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#f0f9ff,#e0f2fe);border-color:#38bdf8;color:#075985">
    <b>🔍 同業比較</b> — 8 個產業 · 股票相對行業中位估值排名 · 識別行業最佳價值個股
  </div>
  <div class="filter-bar card" style="margin-bottom:12px">
    <select id="pcSector" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px;min-width:160px">
      <option value="all">所有產業</option>
    </select>
    <select id="pcSort" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px">
      <option value="peer_rank">同業排名分</option>
      <option value="grand">信念分</option>
      <option value="pe_rel">相對PE (低→高)</option>
      <option value="dy">殖利率</option>
      <option value="rev_yoy">營收YoY</option>
    </select>
  </div>
  <!-- Sector overview cards -->
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin-bottom:16px" id="pcSectorCards"></div>
  <!-- Detail table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title" id="pcTableTitle">同業詳細比較</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>代號</th><th>名稱</th><th>產業</th><th>信念分</th>
          <th>PE</th><th>vs行業中位</th><th>殖利率</th><th>4月YoY</th>
          <th>60日RS</th><th>DNA</th><th>評級</th>
        </tr></thead>
        <tbody id="tbodyPeer"></tbody>
      </table>
    </div>
  </div>
</div><!-- /peercomp -->

<!-- ══════════════════════════════════════════════════ EARNINGS Q ═══ -->
<div id="page-earningsq" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#4ade80;color:#14532d">
    <b>📊 Q4 2025 + Q1 2026 盈利品質分析</b> — 10項指標評分 · EPS加速/營益率/股息覆蓋率/前瞻改善度
  </div>
  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px" id="eqKpis"></div>

  <!-- Grade filter -->
  <div class="filter-bar card" style="margin-bottom:12px">
    <select id="eqGrade" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px">
      <option value="all">全部評級</option>
      <option value="A+">A+ 最優質 (9-10分)</option>
      <option value="A">A  優質 (7-8分)</option>
      <option value="B">B  良好 (5-6分)</option>
      <option value="CD">C/D 普通以下</option>
    </select>
    <select id="eqSort" style="border:1px solid #cbd5e1;border-radius:6px;padding:7px 12px;font-size:13px">
      <option value="eq">盈利品質分</option>
      <option value="grand">信念分</option>
      <option value="accel">EPS加速</option>
      <option value="margin">營業利益率</option>
    </select>
    <span style="font-size:12px;color:#94a3b8;align-self:center">台積電為唯一10/10滿分股票</span>
  </div>

  <!-- Methodology legend -->
  <div class="card card-pad" style="margin-bottom:12px;background:#f8fafc">
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;font-size:11px">
      <div><b>EQ1</b> EPS &gt; 0</div>
      <div><b>EQ2</b> EPS加速 &gt; 0</div>
      <div><b>EQ3</b> EPS強勁 &gt;10%</div>
      <div><b>EQ4</b> 營收YoY &gt; 0</div>
      <div><b>EQ5</b> 營收ACCELERATING</div>
      <div><b>EQ6</b> 營業利益率健康</div>
      <div><b>EQ7</b> 淨利率品質 ≥60%</div>
      <div><b>EQ8</b> 前瞻PE &lt; 歷史PE</div>
      <div><b>EQ9</b> 股息有EPS覆蓋</div>
      <div><b>EQ10</b> Q1改善Q4</div>
    </div>
  </div>

  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title" id="eqTableTitle">盈利品質排名</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>代號</th><th>名稱</th><th>EQ</th><th>等級</th>
          <th>EPS加速</th><th>營業利益率</th><th>淨利率</th>
          <th>前瞻PE</th><th>殖利率</th><th>信念分</th><th>評級</th>
          <th colspan="10" style="font-size:10px;background:#f8fafc">EQ指標 1→10</th>
        </tr></thead>
        <tbody id="tbodyEQ"></tbody>
      </table>
    </div>
  </div>
</div><!-- /earningsq -->

<!-- ═══════════════════════════════════════════════════ MONDAY PLAN ═══ -->
<div id="page-mondayplan" class="page">
  <div class="alert-banner" style="background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#f43f5e;color:#be123c">
    <div class="alert-icon">🗓</div>
    <div>
      <div class="alert-title">開盤行動計畫 — {mondayplan.get('date', TODAY)}</div>
      <div class="alert-sub">整合 33 層分析 → 6 大類別優先清單 · 計時行動事項 · S3日W%R為最大觸發因子</div>
    </div>
  </div>
  <div class="kpi-row" style="grid-template-columns:repeat(6,1fr);margin-bottom:16px" id="mpKpis"></div>

  <!-- Checklist -->
  <div class="card" style="margin-bottom:14px">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⏱ 計時行動清單 — {mondayplan.get('date', TODAY)}</div>
    </div>
    <div id="mpChecklist" class="card-pad"></div>
  </div>

  <!-- Category accordions -->
  <div id="mpCategories"></div>
</div><!-- /mondayplan -->

<!-- ═══════════════════════════════════════════════════ EXPORT ═══ -->
<div id="page-export" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:16px">📁 資料匯出</h2>
  <p style="color:#64748b;margin-bottom:20px">以下為本次分析結果的CSV匯出檔，可用Excel直接開啟（UTF-8 BOM格式）。</p>
  <div id="exportFiles"></div>
  <div style="margin-top:24px;padding:16px;background:#f8fafc;border-radius:10px;border:1px solid #e2e8f0">
    <div style="font-weight:700;margin-bottom:8px;color:#374151">📊 分析摘要</div>
    <div id="exportSummary"></div>
  </div>
</div><!-- /export -->

<!-- ═══════════════════════════════════════════════════ DONATE ═══ -->
<div id="page-donate" class="page">
  <div style="max-width:400px;margin:40px auto;text-align:center;padding:32px 28px;background:linear-gradient(135deg,#fffbeb,#fef3c7);border-radius:18px;border:2px solid #f59e0b;box-shadow:0 4px 24px rgba(245,158,11,0.18)">
    <div style="font-size:36px;margin-bottom:8px">☕</div>
    <h2 style="font-size:22px;font-weight:800;color:#92400e;margin-bottom:6px">支持開發者</h2>
    <p style="font-size:14px;color:#78350f;line-height:1.8;margin-bottom:24px">覺得這個儀表板好用嗎？<br>歡迎請我喝杯咖啡，支持我繼續開發與維護！</p>
    {'<img src="' + DONATE_QR_B64 + '" alt="收款QR碼" style="width:220px;height:220px;border-radius:12px;display:block;margin:0 auto 20px;box-shadow:0 2px 12px rgba(0,0,0,0.12)">' if DONATE_QR_B64 else ''}
    <p style="font-size:12px;color:#a16207;margin:0">手機掃描 QR Code 即可付款 🙏</p>
  </div>
</div><!-- /donate -->

<!-- ═══════════════════════════════════════════════════ POSSIZE ═══ -->
<div id="page-possize" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">📐 倉位計算 — Kelly Criterion</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">以100萬TWD為參考組合，結合回測勝率、Grand評分、盈利品質與技術信號計算建議倉位。</p>
  <div class="kpi-row" id="psKpis"></div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 建議持倉表</div>
    <div style="overflow-x:auto"><table class="data-table" id="psTable">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>產業</th><th>評級</th>
        <th>建議%</th><th>金額(萬)</th><th>張數</th>
        <th>風險層</th><th>Kelly%</th><th>勝率60d</th><th>均報60d</th>
        <th>Grand</th><th>EQ</th><th>止損</th>
      </tr></thead>
      <tbody id="psBody"></tbody>
    </table></div>
  </div></div>
  <div style="margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">🏭 產業分配</div>
      <div id="psSectors"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📌 方法說明</div>
      <div id="psMethod" style="font-size:12px;color:#374151;line-height:1.7"></div>
    </div></div>
  </div>
</div><!-- /possize -->


<!-- ═══════════════════════════════════════════════════ PREMARKET ═══ -->
<div id="page-premarket" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">📋 開盤行動卡 — {mondayplan.get('date', TODAY)}</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">36個建議倉位的具體進出場價位、止損、DNA信號監控清單。</p>
  <div class="kpi-row" id="pmKpis"></div>
  <div id="pmGroups"></div>
</div><!-- /premarket -->

<!-- ═══════════════════════════════════════════════════ SCENARIO ═══ -->
<div id="page-scenario" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🎲 情境分析 — 組合壓力測試</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">基於Kelly組合(36持倉)的三種情境與四種壓力測試，量化風險/報酬輪廓。</p>
  <div class="kpi-row" id="scKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📊 情境報酬</div>
      <div id="scScenarios"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">💥 壓力測試</div>
      <div id="scStress"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📋 個股情境明細 (Top 20)</div>
    <div style="overflow-x:auto"><table class="data-table" id="scTable">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>產業</th><th style="text-align:right">配置%</th>
        <th style="text-align:right">🐂牛市</th><th style="text-align:right">📊基本</th>
        <th style="text-align:right">🐻熊市</th><th style="text-align:right">金融衝擊</th>
        <th style="text-align:right">止損%</th><th>評級</th>
      </tr></thead>
      <tbody id="scBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /scenario -->

<!-- ═══════════════════════════════════════════════════ DIVINCOME ═══ -->
<div id="page-divincome" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">💵 股息收入預測 — 未來12個月</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">Kelly組合(100萬TWD)的預期年股息收入，台灣股票通常7-8月除息。</p>
  <div class="kpi-row" id="diKpis"></div>
  <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📋 個股股息明細</div>
      <div style="overflow-x:auto"><table class="data-table">
        <thead><tr>
          <th>代號</th><th>名稱</th><th style="text-align:right">殖利率</th>
          <th style="text-align:right">每股股利</th><th style="text-align:right">年收入</th>
          <th style="text-align:right">配置%</th><th>除息月</th>
          <th>永續性</th><th>殖利率級別</th>
        </tr></thead>
        <tbody id="diBody"></tbody>
      </table></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px">📅 月份現金流</div>
      <div id="diSchedule"></div>
      <div style="margin-top:16px">
        <div class="section-title" style="margin-bottom:8px">💎 高殖利率精選</div>
        <div id="diPicks"></div>
      </div>
    </div></div>
  </div>
</div><!-- /divincome -->

<!-- ═══════════════════════════════ INSTITUTIONAL FLOWS ═══════════════ -->
<div id="page-instflows" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🏦 法人買賣超 — {instflows.get("data_date", PRICE_DATE)}</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">TWSE T86三大法人淨買賣超；外資/投信/自營商；看漲背離=價跌法買。</p>
  <div class="kpi-row" id="ifKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#2563eb">💎 TRIPLE持倉法人流向</div>
      <div id="ifTriple"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#16a34a">📈 大量買超 (>1000張)</div>
      <div id="ifHeavyBuy"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px;color:#dc2626">🔔 看漲背離 — 價跌法買 (機構逆勢建倉)</div>
    <p style="font-size:12px;color:#94a3b8;margin-bottom:10px">股價在30日均線以下，但三大法人淨買超 → 機構認為低估，逢低佈局。</p>
    <div style="overflow-x:auto"><table class="data-table" id="ifDivTable">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>Grand</th><th>評級</th>
        <th style="text-align:right">外資淨買</th><th style="text-align:right">投信淨買</th>
        <th style="text-align:right">法人合計</th><th style="text-align:right">vs MA30</th>
        <th>信號</th>
      </tr></thead>
      <tbody id="ifDivBody"></tbody>
    </table></div>
  </div></div>
  <div class="card" style="margin-top:12px"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全宇宙法人動向</div>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>Grand</th>
        <th style="text-align:right">外資</th><th style="text-align:right">投信</th>
        <th style="text-align:right">自營</th><th style="text-align:right">合計</th>
        <th>信號</th><th>背離</th>
      </tr></thead>
      <tbody id="ifAllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /instflows -->

<!-- ═════════════════════════ MASTER ACTION SIGNAL ══════════════════ -->
<div id="page-actionsig" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🎯 綜合行動信號</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">基本面(35%) + 智慧資金(25%) + Q2 EPS動能(20%) + 技術DNA(20%) → 行動評分與建議。</p>
  <div class="kpi-row" id="asKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#dc2626">🚀 立即買進</div>
      <div id="asBuyNow"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#16a34a">🆕 新買入信號 (未持有)</div>
      <p style="font-size:12px;color:#94a3b8;margin-bottom:8px">評為買進但尚未持倉的股票</p>
      <div id="asNewBuys"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全宇宙行動信號排名</div>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>板塊</th>
        <th style="text-align:right">行動分</th><th>行動</th>
        <th style="text-align:right">基本面</th><th style="text-align:right">智慧資金</th>
        <th style="text-align:right">EPS動能</th><th style="text-align:right">技術</th>
        <th>主要信號</th><th style="text-align:right">配置%</th>
      </tr></thead>
      <tbody id="asAllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /actionsig -->

<!-- ═══════════════════════════════ SMART MONEY CONFLUENCE ═══════════ -->
<div id="page-smartmoney" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🧲 智慧資金匯合分析</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">法人流向 + 融資融券 + 基本面品質 + 技術位置 + 估值 — 五維匯合評分 (0-100)。看漲背離得分最高。</p>
  <div class="kpi-row" id="smKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#b45309">🔥 強勢匯合 Top10</div>
      <div id="smTopList"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#dc2626">🌀 擠壓候選 (融券高+法人買進)</div>
      <p style="font-size:12px;color:#94a3b8;margin-bottom:8px">高融券餘額 + 三大法人淨買超 → 潛在軋空</p>
      <div id="smSqueeze"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全宇宙智慧資金匯合排名</div>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th>
        <th style="text-align:right">匯合分</th><th>信號</th>
        <th style="text-align:right">法人</th><th style="text-align:right">基本面</th>
        <th style="text-align:right">融資</th><th style="text-align:right">技術</th>
        <th style="text-align:right">估值</th>
        <th style="text-align:right">Grand</th><th>評級</th>
        <th style="text-align:right">法人信號</th><th>融資信號</th>
      </tr></thead>
      <tbody id="smAllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /smartmoney -->

<!-- ═══════════════════════════ Q2 EPS FORECAST ═══════════════════════ -->
<div id="page-q2forecast" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🔮 Q2 2026 EPS 預估</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">基於4月營收YoY + Q1營收YoY + 板塊季節性因子 + 營業槓桿，預測Q2 2026每股盈餘，計算H1年化預估PE。</p>
  <div class="kpi-row" id="q2Kpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#0369a1">⬆ EPS加速股 (Q2成長超越Q1)</div>
      <div id="q2AccList"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#15803d">💎 TRIPLE持倉 Q2前瞻</div>
      <div id="q2TripleList"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全宇宙 Q2 EPS 預估排名</div>
    <p style="font-size:11px;color:#94a3b8;margin-bottom:8px">預估PE = 股價 / (Q1+Q2e EPS×2)；成長率 = (Q2e/Q1-1)×100%</p>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>板塊</th>
        <th style="text-align:right">Q1 EPS</th><th style="text-align:right">Q2e EPS</th>
        <th style="text-align:right">成長%</th><th>加速</th>
        <th style="text-align:right">現PE</th><th style="text-align:right">預估PE</th>
        <th style="text-align:right">Δ</th><th>估值</th>
        <th style="text-align:right">4月YoY</th>
      </tr></thead>
      <tbody id="q2AllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /q2forecast -->

<!-- ═══════════════════════════════ MARGIN OF SAFETY ════════════════ -->
<div id="page-mos" class="page">
  <h2 style="font-size:20px;font-weight:700;margin-bottom:4px">🛡 安全邊際分析</h2>
  <p style="color:#64748b;margin-bottom:16px;font-size:13px">修改版葛拉罕公式：內在價值 = 最佳EPS × 合理PE；合理PE基於板塊基準×成長溢價×品質×DNA多頭信號。</p>
  <div class="kpi-row" id="mosKpis"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#15803d">🛡 最高安全邊際 Top10</div>
      <div id="mosTopList"></div>
    </div></div>
    <div class="card"><div class="card-pad">
      <div class="section-title" style="margin-bottom:10px;color:#0369a1">💎 GARP精選 (安全邊際+EPS加速)</div>
      <p style="font-size:12px;color:#94a3b8;margin-bottom:8px">MoS≥10% + EPS年增率>15%</p>
      <div id="mosGarp"></div>
    </div></div>
  </div>
  <div class="card"><div class="card-pad">
    <div class="section-title" style="margin-bottom:10px">📊 全宇宙安全邊際排名</div>
    <div style="overflow-x:auto"><table class="data-table">
      <thead><tr>
        <th>代號</th><th>名稱</th><th>板塊</th>
        <th style="text-align:right">現價</th><th style="text-align:right">內在價值</th>
        <th style="text-align:right">安全邊際%</th><th>評級</th>
        <th style="text-align:right">合理PE</th><th style="text-align:right">現PE</th>
        <th style="text-align:right">EPS加速</th><th>品質</th>
      </tr></thead>
      <tbody id="mosAllBody"></tbody>
    </table></div>
  </div></div>
</div><!-- /mos -->



<!-- ═══════════════════════════════════════════════════ TECHNICAL ═══ -->
<div id="page-technical" class="page">

  <!-- TAIEX banner -->
  <div class="alert-banner" style="background:linear-gradient(135deg,#fef2f2,#fff5f5);border-color:#fca5a5" id="taixBanner"></div>

  <!-- KPIs -->
  <div class="kpi-row" style="grid-template-columns:repeat(3,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">30d MA 以上</div>
      <div class="kpi-value green" id="kpiAboveMA"></div>
      <div class="kpi-sub">動能持續</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">30d MA 以下</div>
      <div class="kpi-value red" id="kpiBelowMA"></div>
      <div class="kpi-sub">修正 / 反彈機會</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">三重確認買進</div>
      <div class="kpi-value blue" id="kpiTriple"></div>
      <div class="kpi-sub">基本面 + 低於MA + 多頭融資</div>
    </div>
  </div>

  <!-- Triple confirmed -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⭐ 三重確認買進 (基本面 + 低於30日均線 + 多頭融資)</div>
    </div>
    <div class="card-pad" id="tripleConfirmed"></div>
  </div>

  <!-- Two column: bounce + momentum -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🔄 均值回歸候選 (高分 + 低於30d MA)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>分數</th><th>Δ vs MA</th><th>信號</th>
      </tr></thead>
      <tbody id="tbodyBounce"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📈 動能持續 (高分 + 高於30d MA)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>分數</th><th>Δ vs MA</th><th>信號</th>
      </tr></thead>
      <tbody id="tbodyMomentum"></tbody>
      </table>
    </div>
  </div>
  </div>

</div><!-- /technical -->

<!-- ═══════════════════════════════════════════════════ DIVIDEND ═══ -->
<div id="page-dividend" class="page">

  <div class="alert-banner" style="background:linear-gradient(135deg,#f0fdf4,#ecfdf5);border-color:#86efac">
    <div class="alert-icon">💰</div>
    <div>
      <div class="alert-title" style="color:#14532d">台灣股息季節 (6–8月)</div>
      <div class="alert-sub" style="color:#166534">
        大多數上市公司每年配一次股利，除權息日集中於 6–8 月。
        精確除息日需 TWSE Data API (付費)；下表依殖利率排序，評估
        0056 / 00713 高股息 ETF 成分股吸引力。
      </div>
    </div>
  </div>

  <div class="kpi-row" style="grid-template-columns:repeat(3,1fr)">
    <div class="kpi-card">
      <div class="kpi-label">殖利率 &gt; 4% 且分數 ≥ 45</div>
      <div class="kpi-value green" id="kpiHighDiv"></div>
      <div class="kpi-sub">高股息 + 優質基本面</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">最高殖利率</div>
      <div class="kpi-value amber" id="kpiTopDiv"></div>
      <div class="kpi-sub" id="kpiTopDivName"></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">預扣稅</div>
      <div class="kpi-value" style="color:#64748b">8.84%</div>
      <div class="kpi-sub">外資持有人股息扣繳稅</div>
    </div>
  </div>

  <!-- High-quality dividend picks -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">⭐ 高品質高股息 (殖利率 &gt;4% + 分數 ≥45)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>代號</th><th>名稱</th><th>殖利率</th><th>分數</th><th>預估P/E</th><th>P/B</th><th>Q1 EPS</th><th>評級</th>
      </tr></thead>
      <tbody id="tbodyHighDiv"></tbody>
      </table>
    </div>
  </div>

  <!-- All high-yield sorted -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📋 全部高殖利率排行 (殖利率 &gt; 2%)</div>
    </div>
    <div class="tbl-wrap">
      <table><thead><tr>
        <th>排名</th><th>代號</th><th>名稱</th><th>殖利率</th><th>分數</th>
        <th>預估P/E</th><th>Q1 EPS</th><th>ETF</th>
      </tr></thead>
      <tbody id="tbodyAllDiv"></tbody>
      </table>
    </div>
  </div>

  <!-- Strategy notes -->
  <div class="card">
    <div class="card-pad">
      <div class="section-title" style="margin-bottom:12px">📌 股息捕捉策略備忘</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:13px;color:#475569">
        <div>
          <p><strong>買進時機</strong><br>除息日前持有才能領到股利；股價在除息日會下跌約股利金額。</p>
          <p style="margin-top:10px"><strong>殖利率 + 低P/E</strong><br>如 5876 上海商銀 4.42% @ 9.7x 預估P/E 提供總報酬緩衝。</p>
        </div>
        <div>
          <p><strong>金融股注意</strong><br>銀行 / 保險使用 P/B ≤1.5 + 殖利率 &gt;4% 作為進場標準，避開 IFRS 17 收入失真。</p>
          <p style="margin-top:10px"><strong>ETF 再平衡</strong><br>0056 每季篩選，高殖利率股票可能在下次審查時加入或剔除。</p>
        </div>
      </div>
    </div>
  </div>

</div><!-- /dividend -->

<!-- ══════════════════════════════════════════════════ PORTFOLIO ═══ -->
<div id="page-portfolio" class="page">

  <!-- Scenario comparison table -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">📐 投資組合情境比較 (等權重)</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>組合</th><th>股數</th><th>平均分</th><th>平均預估P/E</th>
          <th>平均P/B</th><th>平均殖利率</th><th>平均收入YoY</th><th>多頭融資</th>
        </tr></thead>
        <tbody id="tbodyScenarios"></tbody>
      </table>
    </div>
  </div>

  <!-- Scenario detail cards -->
  <div id="scenarioCards"></div>

  <!-- Sector leaders -->
  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
      <div class="section-title">🏆 各產業最佳標的</div>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>產業</th><th>首選</th><th>分數</th><th>評級</th>
          <th>預估P/E</th><th>殖利率</th><th>收入YoY</th>
        </tr></thead>
        <tbody id="tbodySectorLeaders"></tbody>
      </table>
    </div>
  </div>

</div><!-- /portfolio -->

<!-- ══════════════════════════════════════════════════════ RISK ═══ -->
<div id="page-risk" class="page">

  <div class="alert-banner" style="background:linear-gradient(135deg,#f0f9ff,#eff6ff);border-color:#93c5fd">
    <div class="alert-icon">📐</div>
    <div>
      <div class="alert-title" style="color:#1e40af">PEG &amp; 風險調整評分說明</div>
      <div class="alert-sub" style="color:#1e3a5f">
        <strong>PEG</strong> = 預估P/E ÷ EPS成長率。&lt;1.0 = 相對成長被低估。
        &nbsp;|&nbsp; <strong>風險分</strong> (0–100): 估值、品質、收入趨勢、槓桿、融資。
        &nbsp;|&nbsp; <strong>RA分</strong> = 綜合分 × (1 − 風險/200)。
      </div>
    </div>
  </div>

  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card"><div class="kpi-label">PEG &lt; 1.0</div><div class="kpi-value blue" id="kpiPegCount"></div><div class="kpi-sub">相對成長被低估</div></div>
    <div class="kpi-card"><div class="kpi-label">最佳 PEG</div><div class="kpi-value green" id="kpiBestPeg"></div><div class="kpi-sub" id="kpiBestPegName"></div></div>
    <div class="kpi-card"><div class="kpi-label">低風險優質股</div><div class="kpi-value green" id="kpiLowRisk"></div><div class="kpi-sub">風險≤20 + 分數≥45</div></div>
    <div class="kpi-card"><div class="kpi-label">高風險旗幟</div><div class="kpi-value red" id="kpiHighRisk"></div><div class="kpi-sub">風險≥40</div></div>
  </div>

  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">🏆 風險調整後排行 (Top 15)</div></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>RA分</th><th>綜合分</th><th>風險</th><th>代號</th><th>名稱</th><th>產業</th><th>PEG</th><th>預估P/E</th><th>殖利率</th><th>評級</th>
    </tr></thead><tbody id="tbodyTopRA"></tbody></table></div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">💎 PEG &lt; 1.0 — 相對成長低估</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>PEG</th><th>預估P/E</th><th>成長率</th><th>分數</th></tr></thead><tbody id="tbodyPeg"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">🔴 高風險警示</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>風險</th><th>綜合分</th><th>預估P/E</th><th>營業利益率</th></tr></thead><tbody id="tbodyHighRisk"></tbody></table></div>
    </div>
  </div>

  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">📋 全覽：風險 vs 綜合分</div></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>綜合分</th><th>RA分</th><th>風險</th><th>代號</th><th>名稱</th><th>PEG</th><th>預估P/E</th><th>營業利益率</th><th>收入YoY</th><th>評級</th>
    </tr></thead><tbody id="tbodyRiskFull"></tbody></table></div>
  </div>

</div><!-- /risk -->

<!-- ══════════════════════════════════════════════════ TARGETS ═══ -->
<div id="page-targets" class="page">

  <div class="alert-banner" style="background:linear-gradient(135deg,#fdf4ff,#faf5ff);border-color:#d8b4fe">
    <div class="alert-icon">🎯</div>
    <div>
      <div class="alert-title" style="color:#6b21a8">目標價模型說明</div>
      <div class="alert-sub" style="color:#581c87">
        非金融股：合理P/E = EPS成長率 × PEG目標(0.8–1.0)，上限30x。
        金融股：合理P/B錨定，依股息殖利率與品質加減碼。
        ⚠️ 力積電(6770)目標價因一次性業外收入而失真，請勿依賴。
      </div>
    </div>
  </div>

  <div class="kpi-row" style="grid-template-columns:repeat(4,1fr)">
    <div class="kpi-card"><div class="kpi-label">買進目標 (&gt;+15%)</div><div class="kpi-value green" id="kpiBuyTgt"></div><div class="kpi-sub">上漲空間充足</div></div>
    <div class="kpi-card"><div class="kpi-label">持有 (-5% to +15%)</div><div class="kpi-value amber" id="kpiHoldTgt"></div><div class="kpi-sub">合理價位</div></div>
    <div class="kpi-card"><div class="kpi-label">減碼/避開 (&lt;-5%)</div><div class="kpi-value red" id="kpiSellTgt"></div><div class="kpi-sub">估值偏高</div></div>
    <div class="kpi-card"><div class="kpi-label">全宇宙平均上漲空間</div><div class="kpi-value" id="kpiAvgUpside" style="font-size:22px"></div><div class="kpi-sub">整體市場偏貴</div></div>
  </div>

  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">🟢 買進目標 (上漲空間 &gt; 15%)</div></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>代號</th><th>名稱</th><th>產業</th><th>現價</th><th>目標價</th><th>上漲空間</th><th>綜合分</th><th>方法</th>
    </tr></thead><tbody id="tbodyBuyTgt"></tbody></table></div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">⚪ 持有區間</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>現價</th><th>目標</th><th>空間</th><th>分數</th></tr></thead><tbody id="tbodyHoldTgt"></tbody></table></div>
    </div>
    <div class="card">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">🔴 減碼 / 避開</div></div>
      <div class="tbl-wrap"><table><thead><tr><th>代號</th><th>名稱</th><th>現價</th><th>目標</th><th>下跌空間</th><th>分數</th></tr></thead><tbody id="tbodySellTgt"></tbody></table></div>
    </div>
  </div>

  <div class="card">
    <div class="card-pad" style="border-bottom:1px solid #f1f5f9"><div class="section-title">📋 全部目標價</div></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>代號</th><th>名稱</th><th>產業</th><th>現價</th><th>目標</th><th>空間</th><th>分數</th><th>合理P/E</th><th>合理P/B</th><th>行動</th>
    </tr></thead><tbody id="tbodyAllTgt"></tbody></table></div>
  </div>

</div><!-- /targets -->

<!-- ══════════════════════════════════════════════ FULL MARKET PAGE ════ -->
<div id="page-fullmarket" class="page">
  <div class="card card-pad" style="margin-bottom:16px">
    <div class="section-title" style="margin-bottom:12px">🌐 全市場總覽 — 上市＋上櫃 ({fullmkt.get("total",0)} 支)</div>
    <div class="kpi-row" id="fmKpis"></div>
  </div>

  <!-- Q1 EPS Leaderboard -->
  <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:16px">
    <div class="card card-pad">
      <div class="section-title" style="margin-bottom:10px">🏆 Q1 EPS 排行（全市場 Top 15）</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>#</th><th>代號</th><th>名稱</th><th>市場</th><th>Q1 EPS</th><th>毛利率</th></tr></thead>
        <tbody id="fmEpsLeaderboard"></tbody>
      </table>
    </div>
    <div class="card card-pad">
      <div class="section-title" style="margin-bottom:10px">💹 毛利率 Top 15（營收>1億）</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>#</th><th>代號</th><th>名稱</th><th>市場</th><th>毛利率</th><th>Q1 EPS</th></tr></thead>
        <tbody id="fmGmLeaderboard"></tbody>
      </table>
    </div>
  </div>

  <!-- Sector summary -->
  <div class="card card-pad" style="margin-bottom:16px">
    <div class="section-title" style="margin-bottom:10px">📊 產業別營收動能</div>
    <div id="fmSectorGrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px"></div>
  </div>

  <!-- Filter bar -->
  <div class="card card-pad" style="margin-bottom:12px;display:flex;gap:10px;flex-wrap:wrap;align-items:center">
    <span style="font-weight:700;font-size:13px;color:#374151">篩選：</span>
    <select id="fmMarket" onchange="renderFMTable()" style="padding:4px 8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">
      <option value="ALL">全部市場</option>
      <option value="TSE">上市 (TSE)</option>
      <option value="OTC">上櫃 (OTC)</option>
    </select>
    <select id="fmSector" onchange="renderFMTable()" style="padding:4px 8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">
      <option value="">所有產業</option>
    </select>
    <label style="font-size:13px;color:#475569">營收YoY ≥
      <input id="fmYoyMin" type="number" value="" placeholder="—" style="width:55px;padding:3px 6px;border:1px solid #e2e8f0;border-radius:5px;font-size:13px" oninput="renderFMTable()">%
    </label>
    <label style="font-size:13px;color:#475569">PE ≤
      <input id="fmPeMax" type="number" value="" placeholder="—" style="width:55px;padding:3px 6px;border:1px solid #e2e8f0;border-radius:5px;font-size:13px" oninput="renderFMTable()">
    </label>
    <select id="fmEpsFilter" onchange="renderFMTable()" style="padding:4px 8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">
      <option value="">Q1 EPS 全部</option>
      <option value="pos">EPS &gt; 0</option>
      <option value="gt1">EPS &gt; 1</option>
      <option value="gt3">EPS &gt; 3</option>
      <option value="gt5">EPS &gt; 5</option>
    </select>
    <input id="fmSearch" type="text" placeholder="搜尋代號/名稱…" oninput="renderFMTable()" style="padding:5px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;flex:1;min-width:120px">
    <button onclick="fmResetFilters()" style="padding:4px 10px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;cursor:pointer">重置</button>
    <span id="fmCount" style="font-size:12px;color:#64748b;margin-left:auto"></span>
  </div>

  <!-- Table -->
  <div class="card">
    <div class="tbl-wrap">
      <table id="tblFullMarket">
        <thead><tr>
          <th onclick="fmSort('code')" style="cursor:pointer">代號 ↕</th>
          <th onclick="fmSort('name')" style="cursor:pointer">名稱 ↕</th>
          <th>市場</th>
          <th>產業</th>
          <th onclick="fmSort('price')" style="cursor:pointer">股價 ↕</th>
          <th onclick="fmSort('change')" style="cursor:pointer">漲跌 ↕</th>
          <th onclick="fmSort('pe')" style="cursor:pointer">本益比 ↕</th>
          <th onclick="fmSort('pb')" style="cursor:pointer">股價淨值比 ↕</th>
          <th onclick="fmSort('yield')" style="cursor:pointer">殖利率 ↕</th>
          <th onclick="fmSort('rev_yoy')" style="cursor:pointer">營收YoY ↕</th>
          <th onclick="fmSort('eps_q1')" style="cursor:pointer">Q1 EPS ↕</th>
          <th onclick="fmSort('gross_margin')" style="cursor:pointer">毛利率 ↕</th>
          <th onclick="fmSort('net_margin')" style="cursor:pointer">淨利率 ↕</th>
          <th onclick="fmSort('quick_score')" style="cursor:pointer">評分 ↕</th>
        </tr></thead>
        <tbody id="tbodyFullMarket"></tbody>
      </table>
    </div>
    <div style="display:flex;gap:8px;align-items:center;padding:10px 16px;border-top:1px solid #f1f5f9">
      <button id="fmPrevBtn" onclick="fmPage(-1)" style="padding:4px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;cursor:pointer">◀ 上一頁</button>
      <span id="fmPageInfo" style="font-size:12px;color:#64748b"></span>
      <button id="fmNextBtn" onclick="fmPage(1)" style="padding:4px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;cursor:pointer">下一頁 ▶</button>
    </div>
  </div>
</div><!-- /fullmarket -->

</div><!-- /main -->

<div class="footer">
  <a href="https://slashman413.github.io/terms.html" style="color:#a5b4fc;text-decoration:none">服務說明</a> · <a href="./privacy.html" style="color:#a5b4fc;text-decoration:none">隱私權政策</a> &nbsp;|&nbsp; 資料來源: TWSE (t187ap14_L/17_L/05_L/BWIBBU_ALL/MI_MARGN) + TPEX (t187ap14_O/06_O_ci/05_O) &nbsp;|&nbsp;
  上市 1,082 + 上櫃 887 = 1,969 家 Q1 2026 財務 &nbsp;|&nbsp; 分析日期: {TODAY}
</div>

<script>
// ═══════════════════════════════ DATA ═══════════════════════════════════════
const STOCKS  = {stocks_json};
const MOVERS  = {movers_json};
const GAINERS = {gainers_json};
const SECTORS = {sectors_json};
const TECH      = {tech_json};
const PORTFOLIO = {portfolio_json};
const RISKDATA   = {riskdata_json};
const PTARGETS   = {ptargets_json};
const ETFCONC    = {etfconc_json};
const DIVSUSTAIN = {divsustain_json};
const CONVDATA   = {convdata_json};
const APRDATA    = {aprdata_json};
const REBDATA    = {rebdata_json};
const TRADEDATA  = {tradedata_json};
const CHAINDATA  = {chaindata_json};
const BWIBBU2    = {bwibbu2_json};
const MOMENTUM   = {momentum_json};
const MAREFRESH  = {marefresh_json};
const DNASIGNALS = {dnasignals_json};
const GRANDDATA  = {granddata_json};
const BACKTEST   = {backtest_json};
const RSDATA     = {rsdata_json};
const PORTOPT    = {portopt_json};
const SECTORDATA   = {sectordata_json};
const WATCHALERTS  = {watchalerts_json};
const MAYPREVIEW     = {maypreview_json};
const TRIPLEREPORTS  = {triplereports_json};
const ETFCOMP        = {etfcomp_json};
const STOCKREPORTS   = {stockreports_json};
const CATALYST       = {catalyst_json};
const SENSITIVITY    = {sensitivity_json};
const PEERCOMP       = {peercomp_json};
const EARNINGSQ      = {earningsq_json};
const MONDAYPLAN     = {mondayplan_json};
const POSSIZE        = {possize_json};
const SECROTATION    = {secrotation_json};
const PREMARKET      = {premarket_json};
const SCENARIO       = {scenarioa_json};
const DIVINCOME      = {divincome_json};
const INSTFLOWS      = {instflows_json};
const SMARTMONEY     = {smartmoney_json};
const Q2FCST         = {q2fcst_json};
const ACTIONSIG      = {actionsig_json};
const DNATRIGGER     = {dnatrig_json};
const MOSDATA        = {mosdata_json};
const CONVICTION     = {conviction_json};
const SECMACRO       = {secmacro_json};
const FULLMKT        = {fullmkt_json};
const ETF4Q          = {etf4q_json};
const TRAIL_EPS      = {trail_json};
const OTC_ANALYSIS   = {otcanalysis_json};
const DNA_FULLMKT    = {dnafull_json};
const TAIEX_DATA     = {taiex_json};
const TAIEX_MONTHLY  = {taiex_monthly_json};
const TAIEX_CAPITAL  = {taiex_capital_json};
const EXPORTMANIFEST = {exportmanifest_json};
const SOP_BACKTEST   = {sop_bt_json};

// ═══════════════════════════════ PAYWALL ════════════════════════════════════
// ★ OWNER: edit AUTH_CODES to add/remove subscriber codes
const AUTH_CODES = [
  "TW168-IXP6KVS6", "TW168-AKKIJTUR", "TW168-ICYP1N5O",
  "TW168-YTRHKJHW", "TW168-BA42BCFQ", "TW168-B17RLXD3",
  "TW168-R6GQNUE8", "TW168-79FFBIB6", "TW168-UVWEGGFX",
  "TW168-ZSPT72LA"
];
const PREMIUM_PAGES = new Set([
  // 技術DNA (除回測驗證、SOP三年回測外)
  'strategy','dnascreen','dnatrigger','relstrength','momentum','technical',
  // 精選推薦
  'actionsig','conviction','triplereport','mondayplan','premarket','watchalerts','instflows','smartmoney'
]);
const PW_KEY = 'tw_etf_unlock'; const PW_DAYS = 30;

function isUnlocked() {{
  try {{
    const d = JSON.parse(localStorage.getItem(PW_KEY)||'null');
    return d && d.exp > Date.now();
  }} catch(e) {{ return false; }}
}}

function unlockPremium(code) {{
  localStorage.setItem(PW_KEY, JSON.stringify({{code, exp: Date.now()+PW_DAYS*86400000}}));
  document.getElementById('premiumLockIcon').textContent = '✅';
  document.getElementById('premiumLockIcon2').textContent = '✅';
}}

function showPaywall(pendingId, pendingBtn) {{
  window._pwPending = {{id:pendingId, btn:pendingBtn}};
  document.getElementById('pwCodeInput').value = '';
  document.getElementById('pwError').style.display = 'none';
  document.getElementById('paywallOverlay').style.display = 'flex';
  setTimeout(()=>document.getElementById('pwCodeInput').focus(), 100);
}}

function closePaywall() {{
  document.getElementById('paywallOverlay').style.display = 'none';
  window._pwPending = null;
}}

function verifyCode() {{
  const code = document.getElementById('pwCodeInput').value.trim().toUpperCase();
  const errEl = document.getElementById('pwError');
  if (AUTH_CODES.map(c=>c.toUpperCase()).includes(code)) {{
    unlockPremium(code);
    closePaywall();
    if (window._pwPending) showPage(window._pwPending.id, window._pwPending.btn);
  }} else {{
    errEl.style.display = 'block';
    document.getElementById('pwCodeInput').select();
  }}
}}

// Update lock icons on load
document.addEventListener('DOMContentLoaded', ()=>{{
  if (isUnlocked()) {{
    document.getElementById('premiumLockIcon').textContent = '✅';
    document.getElementById('premiumLockIcon2').textContent = '✅';
  }}
}});

// ═══════════════════════════════ HELPERS ═══════════════════════════════════
function fmt(v, dec=1, suffix='') {{
  if (v == null) return '<span style="color:#cbd5e1">—</span>';
  return v.toFixed(dec) + suffix;
}}
function fmtPct(v) {{
  if (v == null) return '<span style="color:#cbd5e1">—</span>';
  const cls = v >= 0 ? 'pos' : 'neg';
  return `<span class="${{cls}}">${{v >= 0 ? '+' : ''}}${{v.toFixed(1)}}%</span>`;
}}
function fmtNum(v) {{
  if (v == null) return '—';
  return Number(v.toFixed(0)).toLocaleString();
}}
function verdictBadge(v) {{
  if (!v) return '';
  const map = {{
    'STRONG BUY': 'strong-buy', 'BUY': 'buy', 'HOLD': 'hold',
    'REDUCE': 'reduce', 'AVOID': 'avoid', 'WATCH': 'watch',
    'WATCH⚠': 'psmc'
  }};
  const key = map[v] || 'neutral';
  return `<span class="badge badge-${{key}}">${{v}}</span>`;
}}
function marginBadge(sig) {{
  if (!sig || sig === 'N/A') return '<span style="color:#cbd5e1">—</span>';
  const icons = {{ BULLISH:'🟢', BEARISH:'🔴', MIXED:'🟡', UNWINDING:'⚪', NEUTRAL:'⚫', FLAT:'⚪' }};
  const map   = {{ BULLISH:'bullish', BEARISH:'bearish', MIXED:'mixed', UNWINDING:'unwinding', NEUTRAL:'neutral', FLAT:'neutral' }};
  return `<span class="badge badge-${{map[sig]||'neutral'}}">${{icons[sig]||''}} ${{sig}}</span>`;
}}
function scoreBar(score) {{
  if (score == null) return '—';
  const pct = score;
  const cls = score >= 70 ? 's90' : score >= 50 ? 's70' : score >= 35 ? 's50' : 's30';
  return `<div class="score-bar-wrap">
    <span class="score-num">${{score}}</span>
    <div class="score-bar"><div class="score-fill ${{cls}}" style="width:${{pct}}%"></div></div>
  </div>`;
}}
function scoreBreakdown(s) {{
  if (s.v_pts == null) return '';
  const total = (s.v_pts||0)+(s.g_pts||0)+(s.q_pts||0)+(s.i_pts||0);
  if (!total) return '';
  const vw = ((s.v_pts||0)/100*100).toFixed(0);
  const gw = ((s.g_pts||0)/100*100).toFixed(0);
  const qw = ((s.q_pts||0)/100*100).toFixed(0);
  const iw = ((s.i_pts||0)/100*100).toFixed(0);
  return `<div class="score-breakdown" title="V=${{s.v_pts}} G=${{s.g_pts}} Q=${{s.q_pts}} I=${{s.i_pts}}">
    <div class="score-v" style="flex:${{s.v_pts||0}}"></div>
    <div class="score-g" style="flex:${{s.g_pts||0}}"></div>
    <div class="score-q" style="flex:${{s.q_pts||0}}"></div>
    <div class="score-i" style="flex:${{s.i_pts||0}}"></div>
  </div>`;
}}

// ═══════════════════════════════ NAVIGATION ════════════════════════════════
// Mobile dropdown: click toggles; uses fixed positioning so overflow-x:auto doesn't clip
function _closeAllDropdowns() {{
  document.querySelectorAll('.nav-group.open').forEach(g => {{
    g.classList.remove('open');
    const dd = g.querySelector('.nav-dropdown');
    if (dd) {{ dd.style.cssText = ''; }}
  }});
}}
document.addEventListener('click', function(e) {{
  const btn = e.target.closest('.nav-group-btn');
  if (btn) {{
    const grp = btn.closest('.nav-group');
    const isOpen = grp.classList.contains('open');
    _closeAllDropdowns();
    if (!isOpen) {{
      grp.classList.add('open');
      if (window.innerWidth <= 900) {{
        const r = btn.getBoundingClientRect();
        const dd = grp.querySelector('.nav-dropdown');
        if (dd) {{
          dd.style.position = 'fixed';
          dd.style.top = (r.bottom + 4) + 'px';
          dd.style.left = Math.max(8, Math.min(r.left, window.innerWidth - 180)) + 'px';
          dd.style.zIndex = '1000';
        }}
      }}
    }}
    e.stopPropagation();
    return;
  }}
  if (!e.target.closest('.nav-group')) _closeAllDropdowns();
}});

function showPage(id, btn) {{
  // ── Paywall gate ──────────────────────────────────────────────────────────
  if (PREMIUM_PAGES.has(id) && !isUnlocked()) {{ showPaywall(id, btn); return; }}
  // ─────────────────────────────────────────────────────────────────────────
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-group-btn').forEach(t => t.classList.remove('active'));
  _closeAllDropdowns();
  document.getElementById('page-' + id).classList.add('active');
  btn.classList.add('active');
  // Mark parent group button active when a dropdown item is selected
  const grp = btn.closest('.nav-group');
  if (grp) grp.querySelector('.nav-group-btn').classList.add('active');
  if (id === 'screener'  && !window._screenerInited)  {{ initScreener();  window._screenerInited  = true; }}
  if (id === 'margin'    && !window._marginInited)    {{ initMargin();    window._marginInited    = true; }}
  if (id === 'technical' && !window._technicalInited) {{ initTechnical(); window._technicalInited = true; }}
  if (id === 'dividend'  && !window._dividendInited)  {{ initDividend();  window._dividendInited  = true; }}
  if (id === 'portfolio' && !window._portfolioInited) {{ initPortfolio(); window._portfolioInited = true; }}
  if (id === 'risk'      && !window._riskInited)      {{ initRisk();      window._riskInited      = true; }}
  if (id === 'targets'   && !window._targetsInited)   {{ initTargets();   window._targetsInited   = true; }}
  if (id === 'sectors'   && !window._sectorsInited)   {{ initSectors(); initSectorMap(); initSecRotation(); initSecMacro(); window._sectorsInited = true; }}
  if (id === 'etfconc'   && !window._etfconcInited)   {{ initETFConc();   window._etfconcInited   = true; }}
  if (id === 'divsafe'   && !window._divsafeInited)   {{ initDivSafe();   window._divsafeInited   = true; }}
  if (id === 'conviction'&& !window._convInited)      {{ initConviction(); initConvMatrix(); initGrandUnified(); window._convInited = true; }}
  if (id === 'aprevenue' && !window._aprInited)       {{ initAprRevenue();window._aprInited       = true; }}
  if (id === 'rebalance' && !window._rebInited)       {{ initRebalance(); window._rebInited       = true; }}
  if (id === 'tradesetup'&& !window._tradeInited)     {{ initTradeSetup();window._tradeInited     = true; }}
  if (id === 'aichain'   && !window._chainInited)     {{ initAiChain();   window._chainInited     = true; }}
  if (id === 'valrefresh'&& !window._valrInited)      {{ initValRefresh();window._valrInited      = true; }}
  if (id === 'momentum'  && !window._momInited)       {{ initMomentum();  window._momInited       = true; }}
  if (id === 'strategy'    && !window._stratInited)   {{ initStrategySystem(); window._stratInited = true; }}
  if (id === 'dnascreen'   && !window._dnaInited)     {{ initDnaScreen(); initDnaHeat(); window._dnaInited = true; }}
  if (id === 'backtest'    && !window._btInited)       {{ initBacktest();    window._btInited       = true; }}
  if (id === 'relstrength' && !window._rsInited)       {{ initRelStrength(); window._rsInited       = true; }}
  if (id === 'portopt'     && !window._poInited)       {{ initPortOpt();     window._poInited       = true; }}
  if (id === 'watchalerts' && !window._waInited)       {{ initWatchAlerts(); window._waInited       = true; }}
  if (id === 'maypreview'   && !window._mpInited)      {{ initMayPreview();    window._mpInited      = true; }}
  if (id === 'triplereport' && !window._trInited)      {{ initTripleReport();  window._trInited      = true; }}
  if (id === 'etfcompare'   && !window._ecInited)      {{ initEtfCompare();    window._ecInited      = true; }}
  if (id === 'otcanalysis'  && !window._oaInited)      {{ initOtcAnalysis();   window._oaInited      = true; }}
  if (id === 'stockdetail'  && !window._sdInited)      {{ initStockDetail();   window._sdInited      = true; }}
  if (id === 'catalyst'     && !window._catInited)     {{ initCatalyst();      window._catInited     = true; }}
  if (id === 'sensitivity'  && !window._senInited)     {{ initSensitivity();   window._senInited     = true; }}
  if (id === 'peercomp'     && !window._pcInited)      {{ initPeerComp();      window._pcInited      = true; }}
  if (id === 'earningsq'    && !window._eqInited)      {{ initEarningsQ();     window._eqInited      = true; }}
  if (id === 'mondayplan'   && !window._mpInited2)     {{ initMondayPlan();    window._mpInited2     = true; }}
  if (id === 'possize'      && !window._psInited)       {{ initPosSize();       window._psInited      = true; }}
  if (id === 'premarket'    && !window._pmInited)       {{ initPremarket();     window._pmInited      = true; }}
  if (id === 'scenario'     && !window._scInited)       {{ initScenario();      window._scInited      = true; }}
  if (id === 'divincome'    && !window._diInited)       {{ initDivIncome();     window._diInited      = true; }}
  if (id === 'instflows'    && !window._ifInited)       {{ initInstFlows();     window._ifInited      = true; }}
  if (id === 'actionsig'    && !window._asInited)       {{ initActionSig();     window._asInited      = true; }}
  if (id === 'dnatrigger'   && !window._dtInited)       {{ initDnaTrigger();    window._dtInited      = true; }}
  if (id === 'mos'          && !window._mosInited)       {{ initMoS();           window._mosInited     = true; }}
  if (id === 'smartmoney'   && !window._smcInited)      {{ initSmartMoney();    window._smcInited     = true; }}
  if (id === 'q2forecast'   && !window._q2fInited)      {{ initQ2Forecast();    window._q2fInited     = true; }}
  if (id === 'export'       && !window._exportInited)  {{ initExport();        window._exportInited  = true; }}
  // donate page — static, no init needed
  if (id === 'fullmarket'   && !window._fmInited)       {{ initFullMarket();    window._fmInited      = true; }}
  if (id === 'sopbacktest'  && !window._sbInited)       {{ initSopBacktest();   window._sbInited      = true; }}
}}

function showSubTab(btn, id) {{
  const page = btn.closest('.page');
  page.querySelectorAll('.sub-tab').forEach(b => b.classList.remove('active'));
  page.querySelectorAll('.sub-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

// ═══════════════════════════════ OVERVIEW ══════════════════════════════════
(function initOverview() {{
  // Page view counter — persists on counterapi.dev servers across rebuilds
  fetch('https://api.counterapi.dev/v1/tw-etf-dashboard/pageviews/up')
    .then(r => r.json())
    .then(d => {{
      const el = document.getElementById('kpi-pageviews');
      if (el && d && d.count != null) el.textContent = d.count.toLocaleString();
    }})
    .catch(() => {{}});

  // Top picks: BUY+ sorted by score
  const picks = STOCKS.filter(s => ['STRONG BUY','BUY','WATCH⚠'].includes(s.verdict) && s.score != null)
                      .sort((a,b) => (b.score||0)-(a.score||0)).slice(0,10);
  (document.getElementById('tbodyPicks')||{}).innerHTML = picks.map(s => `
    <tr onclick="showBBChart('${{s.code}}','${{s.name}}')" style="cursor:pointer" title="點擊查看K線+布林通道">
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name}}</td>
      <td>${{verdictBadge(s.verdict)}}</td>
      <td>${{scoreBar(s.score)}}</td>
      <td>¥${{s.price != null ? s.price.toLocaleString() : '—'}}</td>
      <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{fmtPct(s.rev_yoy)}}</td>
      <td>${{s.q1_eps != null ? '¥'+s.q1_eps : '—'}}</td>
      <td>${{marginBadge(s.margin_sig)}}</td>
    </tr>`).join('');

  // Movers
  (document.getElementById('declinersList')||{}).innerHTML = MOVERS.map(m => `
    <div class="mover-row" onclick="showBBChart('${{m.code}}','${{m.name}}')" style="cursor:pointer" title="點擊查看K線+布林通道">
      <div><div class="mover-code">${{m.code}} ${{m.name}}</div></div>
      <div style="text-align:right">
        <div class="mover-chg neg">${{m.chg.toFixed(2)}}%</div>
        <div style="font-size:11px;color:#94a3b8">綜合分 ${{m.score}}</div>
      </div>
    </div>`).join('');

  (document.getElementById('gainersList')||{}).innerHTML = GAINERS.map(g => `
    <div class="mover-row" onclick="showBBChart('${{g.code}}','${{g.name}}')" style="cursor:pointer" title="點擊查看K線+布林通道">
      <div><div class="mover-code">${{g.code}} ${{g.name}}</div></div>
      <div class="mover-chg pos">+${{g.chg.toFixed(2)}}%</div>
    </div>`).join('');

  // Revenue momentum: top 8 by YoY
  const mom = STOCKS.filter(s => s.rev_yoy != null && s.score != null)
                    .sort((a,b) => (b.rev_yoy||0)-(a.rev_yoy||0)).slice(0,8);
  document.getElementById('tbodyMomentum').innerHTML = mom.map(s => `
    <tr onclick="showBBChart('${{s.code}}','${{s.name}}')" style="cursor:pointer" title="點擊查看K線+布林通道">
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name}}</td>
      <td>${{fmtPct(s.rev_yoy)}}</td>
      <td>${{fmtPct(s.rev_yoy != null ? s.rev_yoy : null)}}</td>
      <td>${{s.q1_eps != null ? '¥'+s.q1_eps : '—'}}</td>
      <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{verdictBadge(s.verdict)}}</td>
    </tr>`).join('');
}})();

// ═══════════════════════════════ SCREENER ══════════════════════════════════
let _sortCol = 'score', _sortDir = -1;

function initScreener() {{
  // Populate sector filter
  const secs = [...new Set(STOCKS.map(s => s.sector).filter(Boolean))].sort();
  const sel = document.getElementById('filterSector');
  secs.forEach(s => {{ const o = document.createElement('option'); o.value = s; o.text = s; sel.appendChild(o); }});
  // Make headers sortable
  document.querySelectorAll('#tblScreener thead th[data-col]').forEach(th => {{
    th.addEventListener('click', () => {{
      const col = th.dataset.col;
      if (_sortCol === col) _sortDir *= -1; else {{ _sortCol = col; _sortDir = -1; }}
      document.querySelectorAll('#tblScreener thead th').forEach(t => t.classList.remove('sorted-asc','sorted-desc'));
      th.classList.add(_sortDir === -1 ? 'sorted-desc' : 'sorted-asc');
      renderScreener();
    }});
  }});
  // Default sort header
  const defTh = document.querySelector('#tblScreener thead th[data-col="score"]');
  if (defTh) defTh.classList.add('sorted-desc');
  renderScreener();
}}

function renderScreener() {{
  const q   = (document.getElementById('searchBox').value || '').toLowerCase();
  const vf  = document.getElementById('filterVerdict').value;
  const sf  = document.getElementById('filterSector').value;
  const mf  = document.getElementById('filterMargin').value;

  let rows = STOCKS.filter(s => {{
    if (q  && !s.code.includes(q) && !s.name.toLowerCase().includes(q)) return false;
    if (vf && s.verdict !== vf) return false;
    if (sf && s.sector  !== sf) return false;
    if (mf && s.margin_sig !== mf) return false;
    return true;
  }});

  rows.sort((a,b) => {{
    let va = a[_sortCol], vb = b[_sortCol];
    if (va == null) va = _sortDir === -1 ? -Infinity : Infinity;
    if (vb == null) vb = _sortDir === -1 ? -Infinity : Infinity;
    if (typeof va === 'string') return _sortDir * va.localeCompare(vb);
    return _sortDir * (va - vb);
  }});

  document.getElementById('tbodyScreener').innerHTML = rows.map(s => `
    <tr>
      <td><strong>${{s.code}}</strong></td>
      <td style="max-width:140px;overflow:hidden;text-overflow:ellipsis">${{s.name}}</td>
      <td><span style="font-size:11px;color:#64748b">${{s.sector||'—'}}</span></td>
      <td>${{scoreBar(s.score)}}</td>
      <td>${{verdictBadge(s.verdict)}}</td>
      <td>${{s.price != null ? '¥'+s.price.toLocaleString() : '—'}}</td>
      <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{s.pb != null ? s.pb.toFixed(2)+'x' : '—'}}</td>
      <td>${{s.div != null ? s.div.toFixed(2)+'%' : '—'}}</td>
      <td>${{fmtPct(s.rev_yoy)}}</td>
      <td>${{s.q1_eps != null ? '¥'+s.q1_eps : '—'}}</td>
      <td>${{s.op_margin != null ? s.op_margin.toFixed(1)+'%' : '—'}}</td>
      <td>${{marginBadge(s.margin_sig)}}</td>
      <td>${{s.source !== '0050' ? '<span class="src-pill">'+s.source+'</span>' : '<span style="color:#94a3b8;font-size:11px">0050</span>'}}</td>
    </tr>`).join('');

  document.getElementById('screenerCount').textContent = `顯示 ${{rows.length}} / ${{STOCKS.length}} 支股票`;
}}

// ═══════════════════════════════ MARGIN ════════════════════════════════════
function initMargin() {{
  // Confirmed BUY (score ≥65 + BULLISH) or BUY SIGNAL (score ≥50 + BULLISH)
  const MARGIN_SCORES = {{ // use composite scores from our data
    "2330":85,"2317":72,"2454":68,"6669":80,"3008":65,"2382":73,
    "2376":77,"2357":70,"2408":72,"2603":65,"2327":68,"3034":60,
    "2308":55,"4938":58,"1303":55,"2395":62,"2303":60,"2379":60,
    "2615":60,"2207":58,"2301":52,"2409":42,"1101":45,"3037":48,
    "6415":50,"2337":55,"2352":42,"6770":40,"2882":60,"2881":62,
    "2886":58,"2891":60,"2884":55,"5880":52,"2892":55,"5871":65,
    "2887":50,"2801":45,"2883":48,"2890":48,"5876":58,"2412":55,
    "2002":35,"1301":45,"1102":42,"1216":50,"3045":55,"3711":60,
    "1590":52,"2912":45,"4904":48,"6488":40,"2823":38,"2880":42,
    "2888":35,"3231":50,"2383":52,"2344":55,"3481":30,"2049":45,"6743":30,
  }};

  // Build margin rows from STOCKS
  const marginRows = STOCKS.filter(s => s.margin_sig && s.margin_sig !== 'N/A')
    .map(s => ({{ ...s, ms: MARGIN_SCORES[s.code] || s.score || 40 }}))
    .sort((a,b) => (b.ms||0)-(a.ms||0));

  const confirmed = marginRows.filter(s => s.margin_sig === 'BULLISH' && (s.ms||0) >= 65);
  const buySignal = marginRows.filter(s => s.margin_sig === 'BULLISH' && (s.ms||0) >= 50 && (s.ms||0) < 65);
  const diverge   = marginRows.filter(s => s.margin_sig === 'BEARISH'  && (s.ms||0) >= 65);

  document.getElementById('tbodyConfirmed').innerHTML = [
    ...confirmed.map(s => `<tr>
      <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
      <td>${{scoreBar(s.ms)}}</td><td>${{marginBadge(s.margin_sig)}}</td>
      <td class="pos">${{s.m_chg != null ? '+'+fmtNum(s.m_chg) : '—'}}</td>
      <td class="neg">${{s.s_chg != null ? fmtNum(s.s_chg) : '—'}}</td>
      <td><span class="badge badge-confirmed">CONFIRMED BUY ✓</span></td>
    </tr>`),
    ...buySignal.map(s => `<tr>
      <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
      <td>${{scoreBar(s.ms)}}</td><td>${{marginBadge(s.margin_sig)}}</td>
      <td class="pos">${{s.m_chg != null ? '+'+fmtNum(s.m_chg) : '—'}}</td>
      <td class="neg">${{s.s_chg != null ? fmtNum(s.s_chg) : '—'}}</td>
      <td><span class="badge badge-signal">BUY SIGNAL ↑</span></td>
    </tr>`)
  ].join('');

  document.getElementById('tbodyDivergence').innerHTML = diverge.map(s => `<tr>
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td>${{scoreBar(s.ms)}}</td><td>${{marginBadge(s.margin_sig)}}</td>
    <td style="color:#64748b;font-size:12px">融資↓${{fmtNum(s.m_chg)}} 融券↑${{fmtNum(s.s_chg)}}</td>
  </tr>`).join('') || '<tr><td colspan="5" style="color:#94a3b8;padding:12px">無背離信號</td></tr>';

  // Short squeeze
  const squeeze = STOCKS.filter(s => s.m_today && s.s_today && s.m_today > 0)
    .map(s => ({{ ...s, ratio: s.s_today / s.m_today * 100 }}))
    .filter(s => s.ratio > 15)
    .sort((a,b) => b.ratio - a.ratio);

  document.getElementById('tbodySqueeze').innerHTML = squeeze.map(s => `<tr class="squeeze-high">
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td><span class="squeeze-pct">${{s.ratio.toFixed(1)}}%</span></td>
    <td>${{fmtNum(s.s_today)}}</td><td>${{fmtNum(s.m_today)}}</td>
    <td>${{scoreBar(s.score)}}</td>
  </tr>`).join('') || '<tr><td colspan="6" style="color:#94a3b8;padding:12px">無軋空候選</td></tr>';

  // Full margin snapshot
  document.getElementById('tbodyMarginFull').innerHTML = marginRows.map(s => `<tr>
    <td>${{scoreBar(s.ms)}}</td>
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td>${{marginBadge(s.margin_sig)}}</td>
    <td style="font-size:12px">${{s.m_today != null ? fmtNum(s.m_today) : '—'}}</td>
    <td class="${{s.m_chg > 0 ? 'pos' : s.m_chg < 0 ? 'neg' : ''}}">${{s.m_chg != null ? (s.m_chg > 0 ? '+' : '')+fmtNum(s.m_chg) : '—'}}</td>
    <td style="font-size:12px">${{s.s_today != null ? fmtNum(s.s_today) : '—'}}</td>
    <td class="${{s.s_chg > 0 ? 'neg' : s.s_chg < 0 ? 'pos' : ''}}">${{s.s_chg != null ? (s.s_chg > 0 ? '+' : '')+fmtNum(s.s_chg) : '—'}}</td>
  </tr>`).join('');
}}

// ═══════════════════════════════ TECHNICAL ═════════════════════════════════
function initTechnical() {{
  // TAIEX banner
  const t = TECH.taiex;
  document.getElementById('taixBanner').innerHTML = `
    <div class="alert-icon">📉</div>
    <div>
      <div class="alert-title" style="color:#991b1b">
        TAIEX ${{t.close.toLocaleString()}} &nbsp; <span class="neg">${{t.pct.toFixed(2)}}%</span>
      </div>
      <div class="alert-sub" style="color:#7f1d1d">
        {PRICE_DATE} 收盤行情 — 30日均線分析顯示 <strong>${{TECH.summary.below_ma}} 支</strong>股票跌破均線；
        TRIPLE CONFIRMED: ${{TECH.triple_confirmed.length}} 支，可能提供均值回歸買入機會。
      </div>
    </div>`;

  document.getElementById('kpiAboveMA').textContent  = TECH.summary.above_ma;
  document.getElementById('kpiBelowMA').textContent  = TECH.summary.below_ma;
  document.getElementById('kpiTriple').textContent   = TECH.triple_confirmed.length;

  // Triple confirmed cards
  const tripleStocks = TECH.triple_confirmed.map(code => {{
    const s = STOCKS.find(x => x.code === code) || {{}};
    const bc = TECH.bounce_candidates.find(x => x.code === code) || {{}};
    return {{ code, name: s.name || bc.name || code, score: s.score || bc.score,
              pct: bc.pct_vs_ma, fwd_pe: s.fwd_pe, verdict: s.verdict }};
  }});
  document.getElementById('tripleConfirmed').innerHTML = `
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
    ${{tripleStocks.map(s => `
      <div style="border:2px solid #16a34a;border-radius:8px;padding:14px;background:linear-gradient(135deg,#f0fdf4,#fff)">
        <div style="font-size:18px;font-weight:800;color:#14532d">${{s.code}}</div>
        <div style="font-size:13px;color:#166534;margin-bottom:8px">${{(s.name||'').split(' ')[0]}}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <span class="badge badge-confirmed">分數 ${{s.score}}</span>
          <span class="badge badge-buy">MA ${{s.pct != null ? (s.pct>0?'+':'')+s.pct.toFixed(1)+'%' : '↓'}}</span>
          ${{verdictBadge(s.verdict)}}
        </div>
        <div style="font-size:11px;color:#64748b;margin-top:8px">
          ${{s.fwd_pe != null ? '預估P/E: '+s.fwd_pe.toFixed(1)+'x' : ''}}
        </div>
      </div>`).join('')}}
    </div>`;

  // Bounce candidates table
  document.getElementById('tbodyBounce').innerHTML = TECH.bounce_candidates.map(r => `
    <tr>
      <td><strong>${{r.code}}</strong></td>
      <td>${{r.name.split(' ')[0] || r.name}}</td>
      <td>${{scoreBar(r.score)}}</td>
      <td><span class="neg">${{r.pct_vs_ma.toFixed(1)}}%</span></td>
      <td><span style="font-size:12px;color:#dc2626">${{r.tech_sig}}</span></td>
    </tr>`).join('');

  // Momentum intact table
  document.getElementById('tbodyMomentum').innerHTML = TECH.momentum_intact.map(r => `
    <tr>
      <td><strong>${{r.code}}</strong></td>
      <td>${{r.name.split(' ')[0] || r.name}}</td>
      <td>${{scoreBar(r.score)}}</td>
      <td><span class="pos">+${{r.pct_vs_ma.toFixed(1)}}%</span></td>
      <td><span style="font-size:12px;color:#16a34a">${{r.tech_sig}}</span></td>
    </tr>`).join('');
}}

// ═══════════════════════════════ DIVIDEND ══════════════════════════════════
function initDividend() {{
  const allDiv = STOCKS.filter(s => s.div != null && s.div > 2.0)
                       .sort((a,b) => (b.div||0)-(a.div||0));
  const highQual = TECH.high_div_quality;

  document.getElementById('kpiHighDiv').textContent = highQual.length;
  if (allDiv[0]) {{
    document.getElementById('kpiTopDiv').textContent = allDiv[0].div.toFixed(2) + '%';
    document.getElementById('kpiTopDivName').textContent = allDiv[0].name.split(' ')[0] + ' ' + allDiv[0].code;
  }}

  // High quality table
  document.getElementById('tbodyHighDiv').innerHTML = highQual.map(hd => {{
    const s = STOCKS.find(x => x.code === hd.code) || {{}};
    const star = hd.div > 4.5 ? '⭐ ' : '';
    return `<tr>
      <td><strong>${{hd.code}}</strong></td>
      <td>${{hd.name}}</td>
      <td><strong class="pos">${{star}}${{hd.div.toFixed(2)}}%</strong></td>
      <td>${{scoreBar(hd.score)}}</td>
      <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{s.pb != null ? s.pb.toFixed(2)+'x' : '—'}}</td>
      <td>${{s.q1_eps != null ? '¥'+s.q1_eps : '—'}}</td>
      <td>${{verdictBadge(s.verdict)}}</td>
    </tr>`;
  }}).join('');

  // All high-yield
  const etfMap = {{'2603':'0050','2601':'0056','5871':'0056+00713','2801':'0056+00713',
    '1590':'0056+00878','2880':'0056+00713','2912':'0056+00713','4904':'0056+00713'}};
  document.getElementById('tbodyAllDiv').innerHTML = allDiv.map((s,i) => `
    <tr>
      <td style="color:#94a3b8;font-weight:600">#${{i+1}}</td>
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name.split(' ')[0]}}</td>
      <td><strong class="${{s.div >= 4 ? 'pos' : ''}}">${{s.div.toFixed(2)}}%</strong></td>
      <td>${{scoreBar(s.score)}}</td>
      <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{s.q1_eps != null ? '¥'+s.q1_eps : '—'}}</td>
      <td><span style="font-size:11px;color:#64748b">${{s.source || '0050'}}</span></td>
    </tr>`).join('');
}}

// ═══════════════════════════════ PORTFOLIO ═════════════════════════════════
function initPortfolio() {{
  const SCENARIO_COLORS = ['#2563eb','#16a34a','#0ea5e9','#f59e0b','#8b5cf6'];

  // Summary comparison table
  document.getElementById('tbodyScenarios').innerHTML = PORTFOLIO.scenarios.map((p,i) => {{
    if (!p) return '';
    const color = SCENARIO_COLORS[i % SCENARIO_COLORS.length];
    return `<tr>
      <td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${{color}};margin-right:6px"></span><strong>${{p.name}}</strong></td>
      <td style="font-weight:700;color:#1a2332">${{p.count}}</td>
      <td>${{scoreBar(Math.round(p.avg_score||0))}}</td>
      <td>${{p.avg_fwd_pe != null ? p.avg_fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{p.avg_pb != null ? p.avg_pb.toFixed(2)+'x' : '—'}}</td>
      <td class="pos">${{p.avg_div != null ? p.avg_div.toFixed(2)+'%' : '—'}}</td>
      <td>${{fmtPct(p.avg_yoy)}}</td>
      <td>${{p.bullish_margin}}/${{p.count}}</td>
    </tr>`;
  }}).join('');

  // Detail cards for each scenario
  document.getElementById('scenarioCards').innerHTML = PORTFOLIO.scenarios.map((p,i) => {{
    if (!p) return '';
    const color = SCENARIO_COLORS[i % SCENARIO_COLORS.length];
    const stockList = p.stocks.map(s => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f1f5f9">
        <div>
          <strong>${{s.code}}</strong>
          <span style="color:#64748b;margin-left:6px;font-size:12px">${{s.name}}</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          ${{s.div != null ? `<span style="font-size:11px;color:#16a34a;font-weight:700">${{s.div.toFixed(2)}}%</span>` : ''}}
          ${{s.fwd_pe != null ? `<span style="font-size:11px;color:#64748b">${{s.fwd_pe.toFixed(1)}}x</span>` : ''}}
          <span style="font-size:11px;background:#f1f5f9;border-radius:4px;padding:1px 5px;font-weight:700">${{s.score}}</span>
        </div>
      </div>`).join('');

    return `<div class="card" style="margin-bottom:14px">
      <div class="card-pad" style="border-bottom:2px solid ${{color}}">
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div class="section-title" style="color:${{color}}">${{p.name}}</div>
          <div style="display:flex;gap:16px;font-size:13px">
            <span>平均分 <strong>${{(p.avg_score||0).toFixed(0)}}</strong></span>
            <span>P/E <strong>${{p.avg_fwd_pe ? p.avg_fwd_pe.toFixed(1)+'x' : '—'}}</strong></span>
            <span>殖利率 <strong class="pos">${{p.avg_div ? p.avg_div.toFixed(2)+'%' : '—'}}</strong></span>
            <span>收入YoY <strong>${{fmtPct(p.avg_yoy)}}</strong></span>
          </div>
        </div>
      </div>
      <div class="card-pad">${{stockList}}</div>
    </div>`;
  }}).join('');

  // Sector leaders
  const leaders = PORTFOLIO.sector_leaders;
  const sectorOrder = Object.keys(leaders).sort((a,b) =>
    (leaders[b][0]?.score||0) - (leaders[a][0]?.score||0));

  document.getElementById('tbodySectorLeaders').innerHTML = sectorOrder.map(sec => {{
    const best = leaders[sec][0];
    if (!best) return '';
    return `<tr>
      <td><strong>${{sec}}</strong></td>
      <td><strong>${{best.code}}</strong> ${{best.name}}</td>
      <td>${{scoreBar(best.score)}}</td>
      <td>${{verdictBadge(best.verdict)}}</td>
      <td>${{best.fwd_pe != null ? best.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td>${{best.div != null ? best.div.toFixed(2)+'%' : '—'}}</td>
      <td>${{fmtPct(best.rev_yoy)}}</td>
    </tr>`;
  }}).join('');
}}

// ══════════════════════════════ PRICE TARGETS ══════════════════════════════
function initTargets() {{
  const T = PTARGETS.targets;
  const buys  = T.filter(t => t.action === 'STRONG BUY' || t.action === 'BUY');
  const holds = T.filter(t => t.action === 'HOLD');
  const sells = T.filter(t => t.action === 'REDUCE' || t.action === 'AVOID');
  const avg   = T.reduce((s,t) => s + t.upside, 0) / T.length;

  document.getElementById('kpiBuyTgt').textContent  = buys.length;
  document.getElementById('kpiHoldTgt').textContent = holds.length;
  document.getElementById('kpiSellTgt').textContent = sells.length;
  const avgEl = document.getElementById('kpiAvgUpside');
  avgEl.textContent = (avg >= 0 ? '+' : '') + avg.toFixed(1) + '%';
  avgEl.className   = 'kpi-value ' + (avg >= 0 ? 'green' : 'red');

  function upsideCell(u) {{
    const cls = u > 15 ? 'pos' : u < -5 ? 'neg' : '';
    return `<strong class="${{cls}}">${{u >= 0 ? '+' : ''}}${{u.toFixed(1)}}%</strong>`;
  }}
  function priceBar(price, target) {{
    const ratio = Math.min(Math.max(price / target, 0.3), 1.7);
    const pct   = ((ratio - 0.3) / 1.4 * 100).toFixed(0);
    const col   = ratio < 0.85 ? '#16a34a' : ratio > 1.1 ? '#dc2626' : '#f59e0b';
    return `<div style="position:relative;height:4px;background:#e2e8f0;border-radius:2px;margin-top:4px">
      <div style="position:absolute;left:${{pct}}%;top:-3px;width:10px;height:10px;border-radius:50%;background:${{col}};transform:translateX(-50%)"></div>
    </div>`;
  }}

  document.getElementById('tbodyBuyTgt').innerHTML = buys.map(t => `<tr>
    <td><strong>${{t.code}}</strong>${{t.code==='6770' ? ' ⚠️' : ''}}</td>
    <td>${{t.name.split(' ')[0]}}</td>
    <td><span style="font-size:11px;color:#64748b">${{t.sector}}</span></td>
    <td>¥${{t.price.toLocaleString()}}</td>
    <td><strong>¥${{t.target.toLocaleString()}}</strong>${{priceBar(t.price,t.target)}}</td>
    <td>${{upsideCell(t.upside)}}</td>
    <td>${{scoreBar(t.score)}}</td>
    <td style="font-size:11px;color:#64748b;max-width:200px;white-space:normal">${{t.method}}</td>
  </tr>`).join('');

  document.getElementById('tbodyHoldTgt').innerHTML = holds.map(t => `<tr>
    <td><strong>${{t.code}}</strong></td><td>${{t.name.split(' ')[0]}}</td>
    <td>¥${{t.price.toLocaleString()}}</td><td>¥${{t.target.toLocaleString()}}</td>
    <td>${{upsideCell(t.upside)}}</td><td>${{scoreBar(t.score)}}</td>
  </tr>`).join('');

  document.getElementById('tbodySellTgt').innerHTML = sells.map(t => `<tr>
    <td><strong>${{t.code}}</strong></td><td>${{t.name.split(' ')[0]}}</td>
    <td>¥${{t.price.toLocaleString()}}</td><td>¥${{t.target.toLocaleString()}}</td>
    <td>${{upsideCell(t.upside)}}</td><td>${{scoreBar(t.score)}}</td>
  </tr>`).join('');

  const allSorted = [...T].sort((a,b) => (b.score||0)-(a.score||0));
  document.getElementById('tbodyAllTgt').innerHTML = allSorted.map(t => `<tr>
    <td><strong>${{t.code}}</strong></td><td>${{t.name.split(' ')[0]}}</td>
    <td><span style="font-size:11px;color:#64748b">${{t.sector}}</span></td>
    <td>¥${{t.price.toLocaleString()}}</td><td>¥${{t.target.toLocaleString()}}</td>
    <td>${{upsideCell(t.upside)}}</td>
    <td>${{scoreBar(t.score)}}</td>
    <td>${{t.fair_pe != null ? t.fair_pe.toFixed(1)+'x' : '—'}}</td>
    <td>${{t.fair_pb != null ? t.fair_pb.toFixed(2)+'x' : '—'}}</td>
    <td>${{verdictBadge(t.action)}}</td>
  </tr>`).join('');
}}

// ════════════════════════════════ RISK/PEG ═════════════════════════════════
function initRisk() {{
  function riskBadge(r) {{
    if (r <= 15)  return `<span class="badge badge-bullish">LOW</span>`;
    if (r <= 30)  return `<span class="badge badge-hold">MOD</span>`;
    if (r <= 50)  return `<span class="badge badge-watch">HIGH</span>`;
    return              `<span class="badge badge-bearish">DANGER</span>`;
  }}
  function pegBadge(peg) {{
    if (peg == null) return '—';
    const col = peg < 0.5 ? '#0ea5e9' : peg < 1.0 ? '#16a34a' : peg < 1.5 ? '#64748b' : '#dc2626';
    return `<strong style="color:${{col}}">${{peg.toFixed(2)}}</strong>`;
  }}

  const pegUnder = RISKDATA.peg_undervalued.filter(s => s.peg < 1.0);
  document.getElementById('kpiPegCount').textContent  = pegUnder.length;
  document.getElementById('kpiLowRisk').textContent   = RISKDATA.low_risk.length;
  document.getElementById('kpiHighRisk').textContent  = RISKDATA.high_risk.length;
  if (RISKDATA.peg_undervalued[0]) {{
    const b = RISKDATA.peg_undervalued[0];
    document.getElementById('kpiBestPeg').textContent    = b.peg.toFixed(3);
    document.getElementById('kpiBestPegName').textContent = b.code + ' ' + b.name;
  }}

  // Top RA table
  document.getElementById('tbodyTopRA').innerHTML = RISKDATA.top_ra.slice(0,15).map(s => `<tr>
    <td><strong style="color:#2563eb">${{s.ra_score}}</strong></td>
    <td>${{scoreBar(s.score)}}</td>
    <td>${{riskBadge(s.risk)}}</td>
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td><span style="font-size:11px;color:#64748b">${{s.sector}}</span></td>
    <td>${{pegBadge(s.peg)}}</td>
    <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
    <td>${{s.div != null ? s.div.toFixed(2)+'%' : '—'}}</td>
    <td>${{verdictBadge(s.verdict)}}</td>
  </tr>`).join('');

  // PEG undervalued
  document.getElementById('tbodyPeg').innerHTML = RISKDATA.peg_undervalued.map(s => `<tr>
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td>${{pegBadge(s.peg)}}</td>
    <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
    <td class="pos">+${{s.growth_rate != null ? s.growth_rate.toFixed(0) : '—'}}%</td>
    <td>${{scoreBar(s.score)}}</td>
  </tr>`).join('');

  // High risk
  document.getElementById('tbodyHighRisk').innerHTML = RISKDATA.high_risk.map(s => {{
    const full = RISKDATA.all_stocks.find(x => x.code === s.code) || {{}};
    return `<tr>
      <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
      <td><strong class="neg">${{s.risk}}</strong></td>
      <td>${{scoreBar(s.score)}}</td>
      <td>${{full.fwd_pe != null ? full.fwd_pe.toFixed(1)+'x' : '—'}}</td>
      <td class="${{(full.op_margin||0)<0?'neg':''}}">${{full.op_margin != null ? full.op_margin.toFixed(1)+'%' : '—'}}</td>
    </tr>`;
  }}).join('');

  // Full table sorted by composite score
  const allS = [...RISKDATA.all_stocks].sort((a,b) => (b.score||0)-(a.score||0));
  document.getElementById('tbodyRiskFull').innerHTML = allS.map(s => `<tr>
    <td>${{scoreBar(s.score)}}</td>
    <td><strong style="color:#2563eb">${{s.ra_score||'—'}}</strong></td>
    <td>${{riskBadge(s.risk)}}</td>
    <td><strong>${{s.code}}</strong></td><td>${{s.name}}</td>
    <td>${{pegBadge(s.peg)}}</td>
    <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
    <td class="${{(s.op_margin||0)<0?'neg':''}}">${{s.op_margin != null ? s.op_margin.toFixed(1)+'%' : '—'}}</td>
    <td>${{fmtPct(s.rev_yoy)}}</td>
    <td>${{verdictBadge(s.verdict)}}</td>
  </tr>`).join('');
}}

// ═══════════════════════════════ SECTORS ═══════════════════════════════════
function initSectors() {{
  const maxAvg = Math.max(...SECTORS.map(s => s.avg));

  // Bar chart
  const barColors = [
    '#2563eb','#16a34a','#0ea5e9','#8b5cf6','#f59e0b',
    '#ef4444','#64748b','#14b8a6','#f97316','#a855f7','#84cc16','#06b6d4'
  ];
  document.getElementById('sectorChart').innerHTML = SECTORS.map((s,i) => {{
    const pct = (s.avg / 80 * 100).toFixed(0);
    const color = barColors[i % barColors.length];
    const verdict = s.avg >= 60 ? 'BUY' : s.avg >= 45 ? 'HOLD' : 'REDUCE';
    return `<div class="bar-row">
      <div class="bar-label">${{s.sector}}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${{pct}}%;background:${{color}}">
          ${{s.avg.toFixed(1)}}
        </div>
      </div>
      <div class="bar-count">${{s.count}}支</div>
    </div>`;
  }}).join('');

  // Detail table: for each sector show best stock
  const sectorDetail = SECTORS.map(sec => {{
    const secStocks = STOCKS.filter(s => s.sector === sec.sector && s.score != null)
                            .sort((a,b) => (b.score||0)-(a.score||0));
    const best = secStocks[0];
    const verdict = sec.avg >= 60 ? 'BUY' : sec.avg >= 45 ? 'HOLD' : 'REDUCE';
    return `<tr>
      <td><strong>${{sec.sector}}</strong></td>
      <td>${{sec.count}}</td>
      <td>${{scoreBar(Math.round(sec.avg))}}</td>
      <td>${{verdictBadge(verdict)}}</td>
      <td>${{best ? `<strong>${{best.code}}</strong> ${{best.name.split(' ')[0]}} (${{best.score}})` : '—'}}</td>
    </tr>`;
  }});
  document.getElementById('tbodySectorDetail').innerHTML = sectorDetail.join('');
}}

// ══════════════════════════════ TRADE SETUP ═════════════════════════════════
function initTradeSetup() {{
  const T = TRADEDATA;
  const setups = T.setups;

  document.getElementById('kpiTradeCount').textContent = setups.length;
  document.getElementById('kpiAvgRR').textContent      = T.avg_rr.toFixed(1) + '×';
  document.getElementById('kpiTotalPos').textContent   = T.total_position_pct.toFixed(0) + '%';

  const best = [...setups].sort((a,b) => b.rr - a.rr)[0];
  if (best) {{
    document.getElementById('kpiBestRR').textContent     = best.rr.toFixed(1) + '×';
    document.getElementById('kpiBestRRName').textContent = best.code + ' ' + best.name.split(' ')[0];
  }}

  function actionBadge(a) {{
    return a === 'STRONG BUY'
      ? '<span class="badge" style="background:#fef2f2;color:#991b1b;font-weight:700">🔥 最強推薦</span>'
      : '<span class="badge badge-bullish">✅ 買進</span>';
  }}

  // Summary table
  document.getElementById('tbodyTradeSummary').innerHTML = setups.map(s => `<tr>
    <td>${{actionBadge(s.action)}}</td>
    <td><strong>${{s.code}}</strong></td>
    <td>${{s.name.split(' ')[0]}}</td>
    <td>¥${{s.price.toLocaleString()}}</td>
    <td><strong>¥${{s.target.toLocaleString()}}</strong></td>
    <td><strong class="pos">+${{s.upside.toFixed(1)}}%</strong></td>
    <td><span class="neg">¥${{s.stop_price.toLocaleString()}} (-${{s.stop_pct.toFixed(0)}}%)</span></td>
    <td><strong style="color:${{s.rr>=5?'#6d28d9':s.rr>=3?'#16a34a':'#64748b'}}">${{s.rr.toFixed(1)}}×</strong></td>
    <td><strong>${{s.position_pct.toFixed(1)}}%</strong></td>
    <td>${{s.months ? '~'+s.months+'個月' : '—'}}</td>
  </tr>`).join('');

  // Trade cards
  const grid = document.getElementById('tradeCardsGrid');
  grid.innerHTML = setups.map(s => {{
    const triLabel = s.is_triple ? '<span style="color:#f59e0b;font-weight:700"> ⭐</span>' : '';
    const rrColor  = s.rr >= 5 ? '#7c3aed' : s.rr >= 3 ? '#16a34a' : '#64748b';
    return `
    <div class="card" style="border-left:4px solid ${{s.action==='STRONG BUY'?'#dc2626':'#16a34a'}}">
      <div class="card-pad" style="background:${{s.action==='STRONG BUY'?'#fef9f9':'#f9fffe'}};border-bottom:1px solid #f1f5f9">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <span style="font-size:18px;font-weight:700;color:#1a2332">${{s.code}}</span>
            <span style="margin-left:8px;color:#475569">${{s.name.split(' ')[0]}}${{triLabel}}</span>
          </div>
          <div>${{actionBadge(s.action)}}</div>
        </div>
        <div style="font-size:11px;color:#94a3b8;margin-top:2px">${{s.sector}} | Score ${{s.score}} | Risk ${{s.risk}}</div>
      </div>
      <div class="card-pad">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px">
          <div>
            <div style="color:#64748b;font-size:11px">現價</div>
            <div style="font-weight:600">¥${{s.price.toLocaleString()}}</div>
          </div>
          <div>
            <div style="color:#64748b;font-size:11px">目標價</div>
            <div style="font-weight:700;color:#16a34a">¥${{s.target.toLocaleString()}} <span class="pos">(+${{s.upside.toFixed(0)}}%)</span></div>
          </div>
          <div>
            <div style="color:#64748b;font-size:11px">進場區間</div>
            <div>¥${{s.entry_lo}} – ¥${{s.entry_hi}}</div>
          </div>
          <div>
            <div style="color:#64748b;font-size:11px">停損</div>
            <div style="color:#dc2626;font-weight:600">¥${{s.stop_price}} (-${{s.stop_pct.toFixed(0)}}%)</div>
          </div>
          <div>
            <div style="color:#64748b;font-size:11px">風險/報酬</div>
            <div style="font-weight:700;color:${{rrColor}};font-size:16px">${{s.rr.toFixed(1)}}×</div>
          </div>
          <div>
            <div style="color:#64748b;font-size:11px">建議倉位</div>
            <div style="font-weight:600">${{s.position_pct.toFixed(1)}}% 組合</div>
          </div>
        </div>
        <div style="margin-top:10px;padding:8px;background:#f8fafc;border-radius:6px;font-size:11px;color:#475569">
          <strong>催化劑:</strong> ${{s.catalysts.slice(0,2).join(' | ')}}
        </div>
        ${{s.div ? `<div style="margin-top:6px;font-size:11px;color:#15803d">股息殖利率: ${{s.div.toFixed(2)}}% | 遠期P/E: ${{s.fwd_pe ? s.fwd_pe.toFixed(1)+'x' : '—'}}</div>` : ''}}
      </div>
    </div>`;
  }}).join('');
}}

// ══════════════════════════════ REBALANCE ═══════════════════════════════════
function initRebalance() {{
  const R = REBDATA;

  document.getElementById('kpiWeakest').textContent    = R.weakest_component.code;
  document.getElementById('kpiWeakestName').textContent= R.weakest_component.name + ' #' +
    R.all_ranked.find(x => x.code === R.weakest_component.code)?.rank;
  document.getElementById('kpiAtRisk').textContent     = R.at_risk.length;
  document.getElementById('kpiBorderline').textContent = R.borderline.length;

  function riskBadge(r) {{
    if (r === 'HIGH')     return '<span class="badge badge-bearish">🔴 高風險</span>';
    if (r === 'MODERATE') return '<span class="badge badge-hold">🟡 觀察</span>';
    return '<span class="badge badge-bullish">✅ 安全</span>';
  }}

  // Borderline table
  document.getElementById('tbodyBorderline').innerHTML = R.borderline.map(c => `<tr>
    <td><strong style="color:#dc2626">#${{c.rank}}</strong></td>
    <td><strong>${{c.code}}</strong></td>
    <td>${{c.name}}</td>
    <td>¥${{c.mktcap_adj.toFixed(1)}}B</td>
    <td><span class="${{c.chg >= 0 ? 'pos' : 'neg'}}">${{c.chg >= 0 ? '+' : ''}}${{c.chg.toFixed(2)}}%</span></td>
    <td>${{c.cum_yoy != null ? `<span class="${{(c.cum_yoy||0)>=0?'pos':'neg'}}">${{(c.cum_yoy||0)>=0?'+':''}}${{c.cum_yoy.toFixed(1)}}%</span>` : '—'}}</td>
    <td>${{riskBadge(c.risk)}}</td>
  </tr>`).join('');

  // Core top 10
  document.getElementById('tbodyCore10').innerHTML = R.core_top10.map(c => `<tr>
    <td><strong>#${{c.rank}}</strong></td>
    <td><strong>${{c.code}}</strong></td>
    <td>${{c.name}}</td>
    <td>¥${{c.mktcap_adj.toFixed(0)}}B</td>
    <td><span class="${{R.all_ranked.find(x=>x.code===c.code)?.chg>=0?'pos':'neg'}}">
      ${{(R.all_ranked.find(x=>x.code===c.code)?.chg||0)>=0?'+':''}}
      ${{(R.all_ranked.find(x=>x.code===c.code)?.chg||0).toFixed(2)}}%</span></td>
  </tr>`).join('');

  // Full ranking
  document.getElementById('tbodyRebFull').innerHTML = R.all_ranked.map(c => {{
    const statusMap = {{'HIGH':'<span class="badge badge-bearish">🔴 風險</span>',
                        'MODERATE':'<span class="badge badge-hold">🟡 觀察</span>',
                        'SAFE':'<span class="badge badge-bullish">✅</span>'}};
    return `<tr>
      <td><strong style="color:${{c.rank>=48?'#dc2626':c.rank>=44?'#f59e0b':'#475569'}}">#${{c.rank}}</strong></td>
      <td><strong>${{c.code}}</strong></td>
      <td>${{c.name}}</td>
      <td>¥${{c.mktcap_adj.toFixed(1)}}B</td>
      <td><span class="${{c.chg>=0?'pos':'neg'}}">${{c.chg>=0?'+':''}}${{c.chg.toFixed(2)}}%</span></td>
      <td>${{c.cum_yoy!=null?`<span class="${{c.cum_yoy>=0?'pos':'neg'}}">${{c.cum_yoy>=0?'+':''}}${{c.cum_yoy.toFixed(1)}}%</span>`:'—'}}</td>
      <td>${{statusMap[c.rank_risk]||''}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ APRIL REVENUE ══════════════════════════════
function initAprRevenue() {{
  const A = APRDATA;
  const all = A.all_results;

  document.getElementById('kpiAprHigh').textContent  = A.high_growth.length;
  document.getElementById('kpiAprAccel').textContent = A.accelerating.length;
  document.getElementById('kpiAprNeg').textContent   = A.negative_yoy.length;

  function yoyCell(v) {{
    if (v == null) return '—';
    const cls = v > 20 ? 'pos' : v < 0 ? 'neg' : '';
    const sign = v >= 0 ? '+' : '';
    return `<span class="${{cls}}">${{sign}}${{v.toFixed(1)}}%</span>`;
  }}
  function momCell(v) {{
    if (v == null) return '—';
    const cls = v > 5 ? 'pos' : v < -5 ? 'neg' : '';
    const sign = v >= 0 ? '+' : '';
    return `<span class="${{cls}}">${{sign}}${{v.toFixed(1)}}%</span>`;
  }}
  function accelBadge(a) {{
    const map = {{
      'ACCELERATING': '<span class="badge" style="background:#ede9fe;color:#6d28d9">⬆⬆ 加速</span>',
      'STABLE↑':      '<span class="badge badge-bullish">⬆ 穩升</span>',
      'STABLE↓':      '<span class="badge badge-hold">⬇ 穩降</span>',
      'DECELERATING': '<span class="badge badge-bearish">⬇⬇ 減速</span>',
    }};
    return map[a] || '<span style="color:#94a3b8">—</span>';
  }}

  // Top 20 by cum YoY
  const sorted = [...all].sort((a,b) => (b.cum_yoy||0)-(a.cum_yoy||0));
  document.getElementById('tbodyAprTop').innerHTML = sorted.slice(0,20).map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><span style="font-size:11px;color:#64748b">${{r.sector}}</span></td>
    <td>${{yoyCell(r.april_yoy)}}</td>
    <td><strong>${{yoyCell(r.cum_yoy)}}</strong></td>
    <td>${{momCell(r.mom)}}</td>
    <td>${{accelBadge(r.accel)}}</td>
    <td>${{r.score != null ? scoreBar(r.score) : '—'}}</td>
  </tr>`).join('');

  // Contracting stocks
  const neg = [...all].filter(r => (r.cum_yoy||0) < 0).sort((a,b) => (a.cum_yoy||0)-(b.cum_yoy||0));
  document.getElementById('tbodyAprNeg').innerHTML = neg.map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><strong class="neg">${{r.cum_yoy != null ? r.cum_yoy.toFixed(1)+'%' : '—'}}</strong></td>
    <td>${{yoyCell(r.april_yoy)}}</td>
    <td>${{r.score != null ? scoreBar(r.score) : '—'}}</td>
  </tr>`).join('');

  // Accelerating stocks
  const accel = all.filter(r => r.accel === 'ACCELERATING' || r.accel === 'STABLE↑')
    .sort((a,b) => (b.cum_yoy||0)-(a.cum_yoy||0));
  document.getElementById('tbodyAprAccel').innerHTML = accel.map(r => {{
    const delta = (r.cum_yoy||0) - (r.q1_yoy||0);
    return `<tr>
      <td><strong>${{r.code}}</strong></td>
      <td>${{r.name}}</td>
      <td><strong class="pos">${{r.cum_yoy != null ? '+'+r.cum_yoy.toFixed(1)+'%' : '—'}}</strong></td>
      <td>${{r.q1_yoy != null ? (r.q1_yoy >= 0 ? '+' : '')+r.q1_yoy.toFixed(1)+'%' : '—'}}</td>
      <td><span style="color:#7c3aed;font-weight:700">+${{delta.toFixed(1)}}pp</span></td>
    </tr>`;
  }}).join('');

  // Full table
  document.getElementById('tbodyAprFull').innerHTML = sorted.map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td>${{r.apr_b != null ? '¥'+r.apr_b.toFixed(1)+'B' : '—'}}</td>
    <td>${{r.cum_b != null ? '¥'+r.cum_b.toFixed(1)+'B' : '—'}}</td>
    <td>${{yoyCell(r.april_yoy)}}</td>
    <td>${{yoyCell(r.cum_yoy)}}</td>
    <td>${{momCell(r.mom)}}</td>
    <td>${{accelBadge(r.accel)}}</td>
  </tr>`).join('');
}}

// ════════════════════════════════ CONVICTION ════════════════════════════════
function initConviction() {{
  const C = CONVDATA;
  const all = C.all_ranked;

  document.getElementById('kpiStrongBuy').textContent = C.strong_buys.length;
  document.getElementById('kpiBuyConv').textContent   = C.buys.length;
  document.getElementById('kpiAvoidConv').textContent = all.filter(r => r.action === 'AVOID').length;
  const avgConv = all.reduce((s,r) => s + r.conv, 0) / all.length;
  document.getElementById('kpiAvgConv').textContent   = avgConv.toFixed(0);

  function convBar(c) {{
    const pct = Math.min(100, Math.max(0, c));
    const col = c >= 65 ? '#7c3aed' : c >= 45 ? '#16a34a' : c >= 25 ? '#f59e0b' : '#dc2626';
    return `<div style="display:flex;align-items:center;gap:6px">
      <div style="width:${{pct}}px;max-width:100px;height:10px;background:${{col}};border-radius:5px;min-width:4px"></div>
      <strong style="color:${{col}}">${{c}}</strong></div>`;
  }}

  function actionBadge(a) {{
    const map = {{
      'STRONG BUY': '<span class="badge" style="background:#ede9fe;color:#6d28d9;font-weight:700">🔥 最強推薦</span>',
      'BUY':        '<span class="badge badge-bullish">✅ 買進</span>',
      'WATCH':      '<span class="badge badge-hold">👀 觀察</span>',
      'HOLD':       '<span class="badge" style="background:#f1f5f9;color:#475569">⏸ 持有</span>',
      'AVOID':      '<span class="badge badge-bearish">❌ 迴避</span>',
    }};
    return map[a] || a;
  }}

  function maBadge(pct) {{
    if (pct == null) return '—';
    const cls = pct < -2 ? 'pos' : pct > 2 ? 'neg' : '';
    const icon = pct < -5 ? '⬇⬇' : pct < -2 ? '⬇' : pct > 5 ? '⬆⬆' : pct > 2 ? '⬆' : '~';
    return `<span class="${{cls}}">${{icon}} ${{pct.toFixed(1)}}%</span>`;
  }}

  // Conviction detail modal (must be on window for onclick handlers)
  window.showConvDetail = function(code) {{
    const sb  = C.strong_buys.find(x => x.code === code);
    const buy = C.buys.find(x => x.code === code);
    const ar  = all.find(x => x.code === code);
    const r   = ar || sb || buy || {{}};
    const conv   = r.conv  || 0;
    const score  = r.score || 0;
    const risk   = r.risk  != null ? r.risk : null;
    const upside = r.upside != null ? r.upside : null;
    const peg    = r.peg   != null ? r.peg   : null;
    const action = r.action || (sb ? 'STRONG BUY' : buy ? 'BUY' : '');
    const convCol = conv >= 65 ? '#7c3aed' : conv >= 45 ? '#16a34a' : '#f59e0b';

    // Score breakdown logic
    const METHOD = [
      ['基本面 (Grand Score)', score, 30, score >= 70 ? '#7c3aed' : score >= 50 ? '#16a34a' : '#f59e0b', `綜合分 ${{score}}/100`],
      ['均值回歸 (vs 30日線)', r.pct_vs_ma != null ? (r.pct_vs_ma < 0 ? 20 : r.pct_vs_ma < 2 ? 8 : 0) : null, 20, '#0ea5e9', r.pct_vs_ma != null ? `${{r.pct_vs_ma.toFixed(1)}}% (${{r.pct_vs_ma < 0 ? '低於均線，有回升空間' : '高於均線'}})` : '無資料'],
      ['目標價空間', upside != null ? Math.min(20, Math.round(upside / 10)) : null, 20, '#16a34a', upside != null ? `+${{upside.toFixed(1)}}% 上漲空間` : '無資料'],
      ['風險評估', risk != null ? Math.max(0, 15 - Math.round(risk * 0.5)) : null, 15, risk <= 15 ? '#16a34a' : risk <= 30 ? '#f59e0b' : '#dc2626', risk != null ? `風險指數 ${{risk}} (${{risk <= 15 ? '低風險' : risk <= 30 ? '中風險' : '高風險'}})` : '無資料'],
      ['籌碼/融資多頭', r.margin_sig === 'BULLISH' ? 10 : r.margin_sig === 'MIXED' ? 5 : 0, 10, '#f59e0b', r.margin_sig || '無資料'],
      ['PEG 低估', peg != null ? (peg < 0.3 ? 5 : peg < 0.5 ? 3 : peg < 1 ? 1 : 0) : null, 5, '#7c3aed', peg != null ? `PEG = ${{peg.toFixed(2)}} (${{peg < 0.5 ? '深度低估' : peg < 1 ? '低估' : '合理'}})` : '無資料'],
      ['三重確認', r.is_triple ? 5 : 0, 5, '#6d28d9', r.is_triple ? 'DNA + 籌碼 + 基本面 三重共振' : '尚未達到三重確認'],
    ];

    const reasonsHtml = (sb && sb.reasons && sb.reasons.length)
      ? `<div style="margin-top:16px"><div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.05em">推薦理由</div>
         ${{sb.reasons.map(s => `<div style="display:flex;align-items:flex-start;gap:6px;padding:5px 0;border-bottom:1px solid #f8fafc;font-size:13px"><span style="color:#7c3aed;margin-top:1px">✔</span><span>${{s}}</span></div>`).join('')}}</div>`
      : '';

    const dnaLink = typeof showDnaScreenDetail === 'function'
      ? `<button onclick="document.getElementById('convDetailModal').style.display='none';showDnaScreenDetail('${{code}}')" style="margin-top:16px;width:100%;padding:9px;background:linear-gradient(135deg,#6d28d9,#7c3aed);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600">📈 查看K線圖與DNA技術指標</button>`
      : '';

    document.getElementById('convDetailContent').innerHTML = `
      <div style="margin-bottom:16px">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
          <span style="font-size:22px;font-weight:800;color:${{convCol}}">${{code}}</span>
          <span style="font-size:18px;font-weight:700;color:#1e293b">${{r.name || ''}}</span>
          ${{r.sector ? `<span style="font-size:11px;background:#f1f5f9;color:#64748b;padding:2px 8px;border-radius:10px">${{r.sector}}</span>` : ''}}
          ${{actionBadge(action)}}
        </div>
      </div>

      <div style="background:linear-gradient(135deg,${{convCol}}18,${{convCol}}08);border:1px solid ${{convCol}}30;border-radius:10px;padding:14px;margin-bottom:16px;text-align:center">
        <div style="font-size:12px;color:#64748b;font-weight:600;margin-bottom:4px">信念分</div>
        <div style="font-size:48px;font-weight:800;color:${{convCol}};line-height:1">${{conv}}</div>
        <div style="height:8px;background:#e2e8f0;border-radius:4px;margin-top:10px">
          <div style="height:8px;width:${{Math.min(100,conv)}}%;background:${{convCol}};border-radius:4px;transition:width 0.5s"></div>
        </div>
        <div style="font-size:11px;color:#94a3b8;margin-top:4px">/ 100 分</div>
      </div>

      <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.05em">評分細節</div>
      ${{METHOD.map(([label, pts, max, col, desc]) => `
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
            <span style="font-size:12px;color:#374151;font-weight:600">${{label}}</span>
            <span style="font-size:12px;font-weight:700;color:${{col}}">${{pts != null ? `+${{pts}}` : '?'}} / ${{max}}</span>
          </div>
          <div style="height:5px;background:#f1f5f9;border-radius:3px">
            <div style="height:5px;width:${{pts != null ? Math.min(100, pts/max*100) : 0}}%;background:${{col}};border-radius:3px"></div>
          </div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px">${{desc}}</div>
        </div>`).join('')}}
      ${{reasonsHtml}}
      ${{dnaLink}}`;

    const modal = document.getElementById('convDetailModal');
    modal.style.display = 'flex';
  }}

  // Strong buys table
  document.getElementById('tbodyStrongBuy').innerHTML = C.strong_buys.map(r => `<tr style="cursor:pointer" onclick="showConvDetail('${{r.code}}')">
    <td>${{convBar(r.conv)}}</td>
    <td><strong style="color:#6d28d9">${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><span style="font-size:11px;color:#64748b">${{r.sector}}</span></td>
    <td>${{scoreBar(r.score)}}</td>
    <td><span class="${{r.risk <= 15 ? 'pos' : r.risk <= 30 ? '' : 'neg'}}">${{r.risk}}</span></td>
    <td>${{r.upside != null ? `<strong class="pos">+${{r.upside.toFixed(1)}}%</strong>` : '—'}}</td>
    <td>${{r.peg != null ? r.peg.toFixed(2) : '—'}}</td>
    <td>${{maBadge(r.pct_vs_ma)}}</td>
    <td>${{marginBadge(r.margin_sig)}}</td>
    <td>${{r.is_triple ? '⭐' : '—'}}</td>
  </tr>`).join('');

  // Buys table
  document.getElementById('tbodyBuyConv').innerHTML = C.buys
    .filter(r => r.code !== '6770')  // PSMC flag
    .map(r => `<tr style="cursor:pointer" onclick="showConvDetail('${{r.code}}')">
    <td>${{convBar(r.conv)}}</td>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td>${{scoreBar(r.score)}}</td>
    <td>${{r.upside != null ? `<span class="pos">+${{r.upside.toFixed(1)}}%</span>` : '—'}}</td>
    <td>${{marginBadge(r.margin_sig)}}</td>
  </tr>`).join('');

  // Watch table
  const watches = all.filter(r => r.action === 'WATCH').slice(0, 10);
  document.getElementById('tbodyWatchConv').innerHTML = watches.map(r => `<tr style="cursor:pointer" onclick="showConvDetail('${{r.code}}')">
    <td>${{convBar(r.conv)}}</td>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td>${{scoreBar(r.score)}}</td>
    <td>${{r.upside != null ? `<span>${{r.upside >= 0 ? '+' : ''}}${{r.upside.toFixed(1)}}%</span>` : '—'}}</td>
  </tr>`).join('');

  // Full ranked list
  document.getElementById('tbodyConvFull').innerHTML = all.map((r, i) => `<tr style="cursor:pointer" onclick="showConvDetail('${{r.code}}')">
    <td style="color:#94a3b8;font-size:12px">${{i+1}}</td>
    <td>${{convBar(r.conv)}}</td>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><span style="font-size:11px;color:#64748b">${{r.sector}}</span></td>
    <td>${{actionBadge(r.action)}}</td>
    <td>${{scoreBar(r.score)}}</td>
    <td><span class="${{r.risk <= 20 ? 'pos' : r.risk >= 40 ? 'neg' : ''}}">${{r.risk}}</span></td>
    <td>${{r.upside != null ? `<span class="${{r.upside >= 15 ? 'pos' : r.upside < -5 ? 'neg' : ''}}">${{r.upside >= 0 ? '+' : ''}}${{r.upside.toFixed(1)}}%</span>` : '—'}}</td>
    <td>${{marginBadge(r.margin_sig)}}</td>
  </tr>`).join('');
}}

// ════════════════════════════════ DIVIDEND SAFETY ══════════════════════════
function initDivSafe() {{
  const D = DIVSUSTAIN;
  const sm = D.summary;

  document.getElementById('kpiDivTotal').textContent   = sm.total_payers;
  document.getElementById('kpiDivSafe').textContent    = sm.safe_count;
  document.getElementById('kpiDivRisk').textContent    = sm.at_risk_count;
  document.getElementById('kpiDivQuality').textContent = sm.quality_count;

  function safetyBadge(s) {{
    const map = {{
      'SAFE':        '<span class="badge badge-bullish">SAFE ✅</span>',
      'MODERATE':    '<span class="badge" style="background:#dcfce7;color:#15803d">MOD 🟢</span>',
      'TIGHT':       '<span class="badge badge-hold">TIGHT 🟡</span>',
      'AT RISK':     '<span class="badge badge-bearish">AT RISK 🔴</span>',
      'UNSUSTAINABLE':'<span class="badge badge-bearish">UNSUST 💀</span>',
      'UNKNOWN':     '<span class="badge" style="background:#f1f5f9;color:#64748b">? </span>',
    }};
    return map[s] || s;
  }}

  function qualityBadge(q) {{
    if (q === 'HIGH') return '<span style="color:#7c3aed;font-weight:700">⭐ 質優</span>';
    if (q === 'GOOD') return '<span style="color:#16a34a">✓ 良好</span>';
    if (q === 'STRETCHED') return '<span style="color:#dc2626">⚠ 偏高</span>';
    return '<span style="color:#64748b">OK</span>';
  }}

  function payoutCell(p) {{
    if (p == null) return '—';
    const cls = p > 100 ? 'neg' : p > 80 ? '' : 'pos';
    const icon = p > 100 ? '🔴' : p > 80 ? '🟡' : p > 50 ? '🟢' : '✅';
    return `<span class="${{cls}}">${{icon}} ${{p.toFixed(1)}}%</span>`;
  }}

  // Quality picks table
  document.getElementById('tbodyDivQuality').innerHTML = D.quality_picks.map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><span style="font-size:11px;color:#64748b">${{r.sector}}</span></td>
    <td><strong class="pos">${{r.yield.toFixed(2)}}%</strong></td>
    <td>—</td>
    <td>—</td>
    <td>${{payoutCell(r.payout)}}</td>
    <td><strong>${{r.coverage != null ? r.coverage.toFixed(2)+'×' : '—'}}</strong></td>
    <td>${{safetyBadge(r.safety)}}</td>
    <td>${{r.score != null ? scoreBar(r.score) : '—'}}</td>
  </tr>`).join('');

  // At-risk table
  const notes = {{
    '3481': '面板轉虧為盈中，EPS仍偏低',
    '1101': '營收衰退，水泥業景氣下行',
    '4938': '和碩薄利，EPS基期低',
    '2352': '佳世達多元化轉型期',
    '2609': '陽明航運景氣下行，Q1低谷',
    '2603': '長榮高殖利率但配息率剛過100%',
    '1102': '亞泥水泥業週期下行',
  }};
  document.getElementById('tbodyDivRisk').innerHTML = D.at_risk.map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td class="pos">${{r.yield.toFixed(2)}}%</td>
    <td class="neg">${{r.payout != null ? r.payout.toFixed(1)+'%' : '—'}}</td>
    <td style="font-size:11px;color:#64748b">${{notes[r.code] || '配息率超過百分之百'}}</td>
  </tr>`).join('');

  // Yield distribution
  const bands = [
    {{ label:'<2%',    min:0,   max:2,   count:0 }},
    {{ label:'2–3%',   min:2,   max:3,   count:0 }},
    {{ label:'3–4%',   min:3,   max:4,   count:0 }},
    {{ label:'4–5%',   min:4,   max:5,   count:0 }},
    {{ label:'5–6%',   min:5,   max:6,   count:0 }},
    {{ label:'>6%',    min:6,   max:999, count:0 }},
  ];
  D.all_payers.forEach(r => {{
    const b = bands.find(b => r.yield >= b.min && r.yield < b.max);
    if (b) b.count++;
  }});
  const maxCount = Math.max(...bands.map(b => b.count));
  document.getElementById('divYieldDist').innerHTML = `
    <div style="font-size:12px;color:#64748b;margin-bottom:8px">殖利率分佈 (${{D.all_payers.length}}支配息股)</div>
    ${{bands.map(b => `
      <div class="bar-row">
        <div class="bar-label" style="width:50px">${{b.label}}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width:${{maxCount > 0 ? (b.count/maxCount*100).toFixed(0) : 0}}%;background:#8b5cf6">
            ${{b.count}}支
          </div>
        </div>
      </div>`).join('')}}
    <div style="margin-top:12px;font-size:12px;color:#475569">
      平均殖利率: <strong>${{sm.avg_yield.toFixed(2)}}%</strong> |
      質優高息: <strong style="color:#7c3aed">${{sm.quality_count}}支</strong> (≥4.5% + 安全配息)
    </div>`;

  // Full table
  document.getElementById('tbodyDivFull').innerHTML = D.all_payers.map(r => `<tr>
    <td><strong>${{r.code}}</strong></td>
    <td>${{r.name}}</td>
    <td><strong class="${{r.yield >= 4.5 ? 'pos' : ''}}">${{r.yield.toFixed(2)}}%</strong></td>
    <td>${{payoutCell(r.payout)}}</td>
    <td>${{r.coverage != null ? r.coverage.toFixed(2)+'×' : '—'}}</td>
    <td>${{safetyBadge(r.safety)}}</td>
    <td>${{qualityBadge(r.quality)}}</td>
    <td>${{r.score != null ? scoreBar(r.score) : '—'}}</td>
  </tr>`).join('');
}}

// ════════════════════════════════ ETF CONCENTRATION ═══════════════════════
function initETFConc() {{
  const C = ETFCONC;
  const scoreMap = {{}};
  STOCKS.forEach(s => {{ if (s.score != null) scoreMap[s.code] = s.score; }});

  document.getElementById('kpiHHI0050').textContent   = C.hhi_0050.toLocaleString();
  document.getElementById('kpiHHIBlend').textContent  = C.hhi_blended.toLocaleString();
  document.getElementById('kpiTsmc0050').textContent  = C.tsmc_0050_wt.toFixed(1) + '%';
  document.getElementById('kpiTsmcBlend').textContent = C.tsmc_blended_wt.toFixed(2) + '%';
  document.getElementById('tsmc0050Inline').textContent  = C.tsmc_0050_wt.toFixed(1) + '%';
  document.getElementById('tsmcBlendInline').textContent = C.tsmc_blended_wt.toFixed(2) + '%';

  // 0050 top holdings table
  const wt0050 = C.weights_0050;
  const sorted0050 = Object.entries(wt0050).sort((a,b) => b[1]-a[1]).slice(0,15);
  const allStockMap = {{}};
  STOCKS.forEach(s => allStockMap[s.code] = s);
  document.getElementById('tbody0050Top').innerHTML = sorted0050.map(([code, wt], i) => {{
    const s = allStockMap[code] || {{}};
    const blend = (C.blended_top20.find(x => x.code === code) || {{}}).wt;
    const etfs  = (C.blended_top20.find(x => x.code === code) || {{}}).etfs || ['0050'];
    const nEtfs = etfs.length;
    const sc = scoreMap[code];
    const barW = Math.round(wt / C.tsmc_0050_wt * 100);
    return `<tr>
      <td>${{i+1}}</td>
      <td><strong>${{code}}</strong></td>
      <td>${{s.name || code}}</td>
      <td>
        <div style="display:flex;align-items:center;gap:6px">
          <div style="width:${{barW}}px;max-width:120px;min-width:4px;height:8px;background:#3b82f6;border-radius:4px"></div>
          <span style="font-weight:600;color:#1e40af">${{wt.toFixed(1)}}%</span>
        </div>
      </td>
      <td>${{blend != null ? '<span style="color:#16a34a;font-weight:600">'+blend.toFixed(2)+'%</span>' : '—'}}</td>
      <td><span style="background:${{nEtfs >= 3 ? '#dcfce7' : '#f1f5f9'}};color:${{nEtfs >= 3 ? '#15803d' : '#475569'}};padding:2px 8px;border-radius:12px;font-size:12px">${{nEtfs}}</span></td>
      <td>${{sc != null ? scoreBar(sc) : '—'}}</td>
    </tr>`;
  }}).join('');

  // Overlap stocks (3+ ETFs)
  const overlap = C.overlap_stocks.filter(s => s.n >= 3);
  document.getElementById('tbodyOverlap').innerHTML = overlap.slice(0,15).map(s => {{
    const etfStr = s.etfs.join(' + ');
    return `<tr>
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name}}</td>
      <td style="font-size:11px;color:#475569">${{etfStr}}</td>
      <td style="text-align:center"><span style="background:#dcfce7;color:#15803d;padding:2px 8px;border-radius:12px;font-weight:700">${{s.n}}</span></td>
      <td>${{s.wt != null ? s.wt.toFixed(2)+'%' : '—'}}</td>
    </tr>`;
  }}).join('');

  // Blended top 20
  document.getElementById('tbodyBlendTop').innerHTML = C.blended_top20.map((s, i) => {{
    const sc = scoreMap[s.code];
    const etfStr = (s.etfs || []).join(' + ');
    const pct = (s.wt / C.blended_top20[0].wt * 100).toFixed(0);
    return `<tr>
      <td>${{i+1}}</td>
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name}}</td>
      <td>
        <div style="display:flex;align-items:center;gap:6px">
          <div style="width:${{Math.max(4, pct*1.2)}}px;max-width:140px;height:8px;background:#8b5cf6;border-radius:4px"></div>
          <span style="font-weight:600;color:#6d28d9">${{s.wt.toFixed(2)}}%</span>
        </div>
      </td>
      <td style="font-size:11px;color:#475569">${{etfStr}}</td>
      <td>${{sc != null ? scoreBar(sc) : '—'}}</td>
    </tr>`;
  }}).join('');
}}

// ════════════════════════════════ VALUATION REFRESH ══════════════════════════
function initValRefresh() {{
  const B = BWIBBU2;
  const refreshed = B.all_refreshed || [];
  const highDiv   = B.high_div_ge45 || [];
  const cheapPE   = B.cheap_pe_lt15 || [];
  const expanded  = B.pe_expanded   || [];
  const contracted= B.pe_contracted || [];
  const SCORE_MAP = {{}};
  STOCKS.forEach(s => {{ if (s.score != null) SCORE_MAP[s.code] = s.score; }});

  document.getElementById('kpiBwibbuCount').textContent = B.total_matched;
  document.getElementById('kpiHighDiv').textContent     = highDiv.length;

  if (expanded[0]) {{
    document.getElementById('kpiPeExpand').textContent     = expanded[0].pe_new != null ? expanded[0].pe_new.toFixed(1)+'x' : '—';
    document.getElementById('kpiPeExpandName').textContent = expanded[0].code + ' ' + expanded[0].name;
  }}
  if (contracted[0]) {{
    document.getElementById('kpiPeContract').textContent     = contracted[0].pe_new != null ? contracted[0].pe_new.toFixed(1)+'x' : '—';
    document.getElementById('kpiPeContractName').textContent = contracted[0].code + ' ' + contracted[0].name;
  }}

  // Key signal rows (hardcoded insights from analysis)
  const signals = [
    {{ type:'📈 膨脹', code:'3037', name:'欣興', old:74.0, new:142.8, delta:'+68.78x', note:'AI基板漲價，估值過高' }},
    {{ type:'📈 膨脹', code:'6770', name:'力積電', old:6.0, new:45.8, delta:'+39.73x', note:'Q1非常規確認，實際P/E高' }},
    {{ type:'📈 膨脹', code:'1303', name:'南亞', old:15.4, new:48.0, delta:'+32.63x', note:'股價大漲，估值拉升' }},
    {{ type:'📈 膨脹', code:'2408', name:'南亞科', old:11.7, new:35.4, delta:'+23.62x', note:'DRAM復甦已完全定價' }},
    {{ type:'📉 收縮', code:'4938', name:'和碩', old:41.8, new:22.3, delta:'-19.51x', note:'盈利大幅改善，值得重看' }},
    {{ type:'📉 收縮', code:'2609', name:'陽明', old:32.4, new:17.3, delta:'-15.17x', note:'航運盈利回升' }},
    {{ type:'📉 收縮', code:'2603', name:'長榮', old:15.4, new:10.3, delta:'-5.05x', note:'⭐ 最便宜航運+殖利率6.78%' }},
    {{ type:'📉 收縮', code:'1102', name:'亞泥', old:15.3, new:11.5, delta:'-3.80x', note:'水泥低估+殖利率6.70%' }},
  ];
  const allMap = {{}};
  (B.all_refreshed||[]).forEach(r => allMap[r.code] = r);

  document.getElementById('tbodyValSignals').innerHTML = signals.map(s => {{
    const isExpand = s.type.includes('膨脹');
    const r = allMap[s.code] || {{}};
    const divStr = r.div_new != null ? r.div_new.toFixed(2)+'%' : '—';
    return `<tr>
      <td>${{isExpand
        ? '<span class="badge badge-bearish">'+s.type+'</span>'
        : '<span class="badge badge-bullish">'+s.type+'</span>'
      }}</td>
      <td><strong>${{s.code}}</strong></td>
      <td>${{s.name}}</td>
      <td>${{s.old.toFixed(1)}}x</td>
      <td><strong style="color:${{isExpand?'#dc2626':'#16a34a'}}">${{s.new.toFixed(1)}}x</strong></td>
      <td><span class="${{isExpand?'neg':'pos'}}">${{s.delta}}</span></td>
      <td>${{divStr}}</td>
      <td style="font-size:12px;color:#475569">${{s.note}}</td>
    </tr>`;
  }}).join('');

  // High dividend
  document.getElementById('tbodyHighDiv').innerHTML = highDiv.map(r => {{
    const rr = allMap[r.code] || {{}};
    const sc = SCORE_MAP[r.code];
    return `<tr>
      <td><strong>${{r.code}}</strong></td>
      <td>${{r.name}}</td>
      <td><strong class="pos">${{r.div_new.toFixed(2)}}%</strong></td>
      <td>${{rr.pe_new != null ? rr.pe_new.toFixed(1)+'x' : '—'}}</td>
      <td>${{rr.pb_new != null ? rr.pb_new.toFixed(2)+'x' : '—'}}</td>
      <td>${{sc != null ? scoreBar(sc) : '—'}}</td>
    </tr>`;
  }}).join('');

  // Cheap P/E
  document.getElementById('tbodyCheapPE').innerHTML = cheapPE.map(r => {{
    const rr = allMap[r.code] || {{}};
    const delta = (r.pe_old && r.pe_new) ? (r.pe_new - r.pe_old) : null;
    return `<tr>
      <td><strong>${{r.code}}</strong></td>
      <td>${{r.name}}</td>
      <td><strong style="color:#16a34a">${{r.pe_new.toFixed(1)}}x</strong></td>
      <td>${{r.pe_old != null ? r.pe_old.toFixed(1)+'x' : '—'}}</td>
      <td>${{delta != null ? `<span class="${{delta<0?'pos':'neg'}}">${{delta>=0?'+':''}}${{delta.toFixed(1)}}x</span>` : '—'}}</td>
      <td>${{rr.div_new != null ? rr.div_new.toFixed(2)+'%' : '—'}}</td>
    </tr>`;
  }}).join('');
}}

// ════════════════════════════════ RELATIVE STRENGTH ══════════════════════════
function initRelStrength() {{
  const R   = RSDATA;
  const all = R.all_rs || [];
  const fv  = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct = (v,d=1) => {{
    if (v==null) return '<td>—</td>';
    const col = v>=10?'#c2410c':v>=3?'#16a34a':v>=-3?'#374151':v>=-10?'#ca8a04':'#dc2626';
    return `<td style="color:${{col}};font-weight:${{Math.abs(v)>=5?'700':'400'}}">${{v>=0?'+':''}}${{fv(v,d)}}%</td>`;
  }};

  const out = (R.outperformers_60d||[]).length;
  const und = (R.underperformers_60d||[]).length;
  const combo = (R.dna_rs_combo||[]).length;
  document.getElementById('rsMetaCards').innerHTML = [
    {{label:'📈 60日跑贏指數', count:out, note:'>+5%超額報酬', bg:'#f0fdf4', col:'#14532d'}},
    {{label:'📉 60日跑輸指數', count:und, note:'<-5%超額報酬', bg:'#fef2f2', col:'#7c2d12'}},
    {{label:'🎯 DNA+正RS組合', count:combo, note:'DNA≥3 + RS>0', bg:'#f5f3ff', col:'#4c1d95'}},
  ].map(c=>`<div class="kpi-card" style="background:${{c.bg}};border:1px solid rgba(0,0,0,.08)">
    <div class="kpi-label" style="color:${{c.col}}">${{c.label}}</div>
    <div class="kpi-value" style="color:${{c.col}}">${{c.count}}</div>
    <div style="font-size:11px;color:#64748b;margin-top:4px">${{c.note}}</div>
  </div>`).join('');

  document.getElementById('tbodyDnaRs').innerHTML = (R.dna_rs_combo||[]).slice(0,15).map(r=>`
    <tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td><b>${{r.code}}</b></td><td>${{r.name.split(' ')[0]}}</td>
      ${{pct(r.ret_60d)}}
      <td style="font-weight:700;color:${{(r.rs_60d||0)>=20?'#c2410c':'#16a34a'}}">
        ${{(r.rs_60d>=0?'+':'')}}${{fv(r.rs_60d)}}%</td>
      ${{pct(r.rs_20d)}}
      <td style="font-weight:700">${{r.bull_signs!=null?r.bull_signs+'/6':'—'}}</td>
      <td style="color:${{(r.pct_from_52w_high||0)>-10?'#ca8a04':'#94a3b8'}}">
        ${{r.pct_from_52w_high!=null?(r.pct_from_52w_high>=0?'+':'')+fv(r.pct_from_52w_high)+'%':'—'}}</td>
      <td style="font-size:12px">${{r.final||'—'}}</td>
    </tr>`).join('');

  document.getElementById('tbodyAllRs').innerHTML = all.slice(0,30).map((r,i)=>`
    <tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td style="color:#94a3b8;font-size:12px">${{i+1}}</td>
      <td><b>${{r.code}}</b></td><td style="font-size:13px">${{r.name.split(' ')[0]}}</td>
      ${{pct(r.ret_60d)}}
      <td style="color:#64748b;font-size:12px">${{(r.idx_ret_60d>=0?'+':'')}}${{fv(r.idx_ret_60d)}}%</td>
      <td style="font-weight:700;color:${{(r.rs_60d||0)>=20?'#c2410c':(r.rs_60d||0)>=0?'#16a34a':'#dc2626'}}">
        ${{(r.rs_60d>=0?'+':'')}}${{fv(r.rs_60d)}}%</td>
      ${{pct(r.rs_20d)}}
      <td style="color:${{(r.pct_from_52w_high||0)>-5?'#ca8a04':'#94a3b8'}};font-size:12px">
        ${{r.pct_from_52w_high!=null?(r.pct_from_52w_high>=0?'+':'')+fv(r.pct_from_52w_high)+'%':'—'}}</td>
      <td style="font-size:12px">${{r.final||'—'}}</td>
    </tr>`).join('');

  document.getElementById('tbodyCorrPairs').innerHTML = (R.high_corr_pairs||[]).map(p=>`
    <tr>
      <td><b>${{p.a}}</b></td><td>${{p.name_a.split(' ')[0]}}</td>
      <td><b>${{p.b}}</b></td><td>${{p.name_b.split(' ')[0]}}</td>
      <td style="font-weight:700;color:${{Math.abs(p.r)>=0.85?'#dc2626':Math.abs(p.r)>=0.75?'#ca8a04':'#374151'}}">
        ${{fv(p.r,2)}}</td>
      <td style="font-size:12px;color:#64748b">
        ${{Math.abs(p.r)>=0.8?'⚠️ 高度集中風險':'🔶 注意分散'}}</td>
    </tr>`).join('');
}}

// ════════════════════════════════ ETF COMPARISON ═════════════════════════════
function initEtfCompare() {{
  const E  = ETFCOMP;
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct= (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;

  const ratingColor = {{
    '🔥 強力推薦': {{bg:'#fef2f2',border:'#ef4444',text:'#7f1d1d'}},
    '📈 積極看多': {{bg:'#f0fdf4',border:'#22c55e',text:'#14532d'}},
    '⬛ 中性偏多': {{bg:'#f8fafc',border:'#94a3b8',text:'#334155'}},
    '📉 偏空謹慎': {{bg:'#fafafa',border:'#94a3b8',text:'#64748b'}},
  }};

  // Scorecards
  document.getElementById('etfScorecards').innerHTML = (E.etfs||[]).map(e => {{
    const rc = ratingColor[e.rating] || ratingColor['⬛ 中性偏多'];
    const barW = Math.round((e.avg_grand - 40) / 30 * 100);
    const topSecs = (e.top_sectors||[]).slice(0,2).map(s=>`${{s.sector}}(${{s.pct.toFixed(0)}}%)`).join('·');
    return `<div onclick="window._showEtfHoldings('${{e.etf_code}}')"
      style="border:2px solid ${{rc.border}};border-radius:12px;padding:14px;
             background:${{rc.bg}};cursor:pointer;transition:transform 0.1s"
      onmouseover="this.style.transform='scale(1.02)'"
      onmouseout="this.style.transform='scale(1)'">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <b style="font-size:18px;color:${{rc.text}}">${{e.etf_code}}</b>
        <span style="font-size:11px;color:#64748b">${{e.n_holdings}}支</span>
      </div>
      <div style="font-size:12px;color:#64748b;margin-bottom:8px">${{e.etf_name}}</div>
      <div style="font-size:24px;font-weight:800;color:${{rc.text}};margin-bottom:4px">
        ${{e.avg_grand.toFixed(1)}}
        <span style="font-size:12px;font-weight:400;color:#64748b">信念分</span>
      </div>
      <div style="background:#e2e8f0;border-radius:4px;height:6px;margin-bottom:8px">
        <div style="width:${{Math.min(100,Math.max(0,barW))}}%;height:6px;background:${{rc.border}};border-radius:4px"></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px;color:#64748b">
        <span>PE: ${{e.wt_pe!=null?fv(e.wt_pe,1)+'x':'—'}}</span>
        <span style="color:#16a34a;font-weight:700">殖: ${{e.wt_div_yield!=null?fv(e.wt_div_yield,2)+'%':'—'}}</span>
        <span>DNA: ${{fv(e.avg_dna_signals,1)}}/6</span>
        <span>RS60: ${{e.avg_rs_60d!=null?pct(e.avg_rs_60d):'—'}}</span>
      </div>
      <div style="margin-top:6px;font-size:11px;color:#94a3b8">${{topSecs}}</div>
      <div style="margin-top:6px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:12px;font-weight:700;color:${{rc.text}}">${{e.rating}}</span>
        ${{e.triple_holdings>0?`<span style="font-size:11px;background:#fee2e2;padding:2px 6px;border-radius:8px;color:#991b1b">💎×${{e.triple_holdings}}</span>`:''}}</div>
    </div>`;
  }}).join('');

  // Comparison table
  document.getElementById('tbodyEtfCompare').innerHTML = (E.etfs||[]).map((e,i) => {{
    const top = i===0;
    return `<tr onclick="window._showEtfHoldings('${{e.etf_code}}')" style="cursor:pointer${{top?';background:#fffbeb':''}}">
      <td><b style="color:${{top?'#c2410c':'#374151'}}">${{e.etf_code}}</b></td>
      <td style="font-size:13px">${{e.etf_name}}</td>
      <td style="font-size:12px;color:#64748b">${{e.theme}}</td>
      <td style="text-align:center">${{e.n_holdings}}</td>
      <td style="font-weight:700;color:${{e.avg_grand>=60?'#c2410c':e.avg_grand>=55?'#16a34a':'#374151'}}">${{fv(e.avg_grand,1)}}</td>
      <td style="text-align:center">${{fv(e.avg_dna_signals,1)}}/6</td>
      <td style="color:#64748b">${{e.wt_pe!=null?fv(e.wt_pe,1)+'x':'—'}}</td>
      <td style="color:#16a34a;font-weight:${{e.wt_div_yield>=4?'700':'400'}}">${{e.wt_div_yield!=null?fv(e.wt_div_yield,2)+'%':'—'}}</td>
      <td style="color:${{(e.avg_rs_60d||0)>=0?'#16a34a':'#dc2626'}}">${{e.avg_rs_60d!=null?pct(e.avg_rs_60d):'—'}}</td>
      <td style="color:${{e.pct_above_ma>=70?'#16a34a':e.pct_above_ma>=50?'#374151':'#ca8a04'}};font-weight:600">${{fv(e.pct_above_ma,0)}}%</td>
      <td style="font-weight:700;color:#c2410c">${{e.triple_holdings>0?'💎×'+e.triple_holdings:'—'}}</td>
      <td style="font-size:12px">${{e.rating}}</td>
    </tr>`;
  }}).join('');

  // ETF holdings drill-down
  window._showEtfHoldings = (code) => {{
    const e = (E.etfs||[]).find(x=>x.etf_code===code);
    if (!e) return;
    document.getElementById('etfHoldingsCard').style.display = 'block';
    document.getElementById('etfHoldingsTitle').textContent = `${{code}} ${{e.etf_name}} — 成分股 (${{e.n_holdings}}支)`;
    document.getElementById('tbodyEtfHoldings').innerHTML = (e.all_holdings||[]).map(h=>{{
      const fc = h.final&&h.final.includes('TRIPLE')?'#c2410c':h.final&&h.final.includes('STRONG')?'#2563eb':'#374151';
      return `<tr>
        <td style="font-weight:700;color:#0c4a6e">${{fv(h.weight_pct,1)}}%</td>
        <td><b>${{h.code}}</b></td>
        <td style="font-size:13px">${{h.name.split(' ')[0]}}</td>
        <td style="font-weight:700;color:#1e3a5f">${{h.grand!=null?fv(h.grand,0):'—'}}</td>
        <td style="text-align:center">${{h.bull_signs!=null?h.bull_signs+'/6':'—'}}</td>
        <td style="color:#64748b">${{h.pe!=null?fv(h.pe,1)+'x':'—'}}</td>
        <td style="color:#16a34a">${{h.div_yield!=null?fv(h.div_yield,2)+'%':'—'}}</td>
        <td style="font-size:12px;color:${{fc}}">${{h.final||'—'}}</td>
      </tr>`;
    }}).join('');
    document.getElementById('etfHoldingsCard').scrollIntoView({{behavior:'smooth'}});
  }};

  // ── Q1 2026 Financial Report section ──────────────────────────────────────
  const Q = ETF4Q || {{}};
  const etf4qList = ['0050','0056','00878','00713','006208'];

  document.getElementById('tbodyEtfQ1').innerHTML = etf4qList.map(code => {{
    const e = (Q.etfs||{{}})[code];
    if (!e) return '';
    const revColor = (e.avg_rev_yoy||0) >= 0 ? '#16a34a' : '#dc2626';
    return `<tr onclick="window._showEtfHoldings('${{code}}')" style="cursor:pointer">
      <td><b style="color:#1e3a5f">${{code}}</b></td>
      <td style="text-align:center">${{e.stock_count}}</td>
      <td style="text-align:center;color:#16a34a;font-weight:600">${{e.eps_coverage}}</td>
      <td style="font-weight:700;color:#1e3a5f">${{fv(e.avg_eps_q1,2)}}</td>
      <td style="color:#64748b">${{e.avg_pe!=null?fv(e.avg_pe,1)+'x':'—'}}</td>
      <td style="color:#16a34a;font-weight:${{(e.avg_div_yield||0)>=4?'700':'400'}}">${{e.avg_div_yield!=null?fv(e.avg_div_yield,2)+'%':'—'}}</td>
      <td style="color:${{revColor}};font-weight:600">${{e.avg_rev_yoy!=null?(e.avg_rev_yoy>=0?'+':'')+fv(e.avg_rev_yoy,1)+'%':'—'}}</td>
      <td style="font-weight:700;color:#c2410c">${{e.triple_confirmed&&e.triple_confirmed.length>0?'💎×'+e.triple_confirmed.length:'—'}}</td>
      <td style="text-align:center">${{e.buy_count||0}}</td>
    </tr>`;
  }}).join('');

  document.getElementById('etfQ1TopGrid').innerHTML = etf4qList.map(code => {{
    const e = (Q.etfs||{{}})[code];
    if (!e) return '';
    const tops    = (e.top_eps||[]).slice(0,3);
    const triples = (e.triple_confirmed||[]);
    const revColor = (e.avg_rev_yoy||0) >= 0 ? '#16a34a' : '#dc2626';
    return `<div class="card" style="padding:14px;border-top:3px solid #3b82f6">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <b style="font-size:17px;color:#1e3a5f">${{code}} Q1 2026</b>
        <span style="font-size:12px;color:#64748b">${{e.eps_coverage}} EPS涵蓋</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px;margin-bottom:8px">
        <span>平均Q1 EPS: <b style="color:#1e3a5f">${{fv(e.avg_eps_q1,2)}}</b></span>
        <span>PE: <b>${{e.avg_pe!=null?fv(e.avg_pe,1)+'x':'—'}}</b></span>
        <span>殖利率: <b style="color:#16a34a">${{e.avg_div_yield!=null?fv(e.avg_div_yield,2)+'%':'—'}}</b></span>
        <span>營收YoY: <b style="color:${{revColor}}">${{e.avg_rev_yoy!=null?(e.avg_rev_yoy>=0?'+':'')+fv(e.avg_rev_yoy,1)+'%':'—'}}</b></span>
      </div>
      <div style="font-size:11px;font-weight:700;color:#374151;margin-bottom:4px;border-top:1px solid #e2e8f0;padding-top:6px">EPS最高</div>
      ${{tops.map(s=>`<div style="display:flex;justify-content:space-between;font-size:12px;padding:2px 0;border-bottom:1px solid #f1f5f9">
        <span><b>${{s.code}}</b> ${{(s.name||'').split(' ')[0]}}</span>
        <span style="font-weight:700;color:#c2410c">${{fv(s.eps,2)}}</span>
      </div>`).join('')}}
      ${{triples.length>0?`<div style="margin-top:8px;font-size:11px;background:#fff5f5;border-radius:6px;padding:4px 8px;color:#7f1d1d">💎 TRIPLE: ${{triples.map(t=>`${{t.code}}`).join(' · ')}}</div>`:''}}
    </div>`;
  }}).join('');
}}

// ════════════════════════════════ OTC ANALYSIS ═══════════════════════════════
function initOtcAnalysis() {{
  const O  = OTC_ANALYSIS || {{}};
  const ov = O.overall || {{}};
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct= (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;

  // KPIs
  document.getElementById('otcKpis').innerHTML = [
    {{label:'上櫃總數',   value:(ov.total||0)+'家',              sub:'TPEX OTC'}},
    {{label:'Q1獲利家數', value:(ov.profitable||0)+'家',         sub:`虧損${{ov.loss||0}}家`}},
    {{label:'獲利率',     value:ov.total?((ov.profitable/ov.total*100).toFixed(1)+'%'):'—', sub:'Q1 EPS>0'}},
    {{label:'中位Q1 EPS', value:fv(ov.median_eps,2),            sub:'元/股'}},
    {{label:'中位營收YoY',value:pct(ov.median_rev_yoy),         sub:'4月年增'}},
    {{label:'中位毛利率', value:fv(ov.median_gross_margin)+'%', sub:'Q1 2026'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div><div class="kpi-val">${{k.value}}</div><div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  // Sector table
  const sectors = (O.sectors||[]).filter(s=>s.sector&&s.median_eps!=null).sort((a,b)=>(b.median_eps||0)-(a.median_eps||0));
  document.getElementById('tbodyOtcSectors').innerHTML = sectors.map((s,i) => {{
    const profRate = s.count ? (s.profitable/s.count*100).toFixed(0)+'%' : '—';
    const top3     = (s.top_eps||[]).slice(0,3).map(t=>`<b>${{t.code}}</b>`).join(' ');
    const yoyClr   = (s.median_rev_yoy||0)>=0?'#16a34a':'#dc2626';
    return `<tr>
      <td style="font-weight:600">${{s.sector}}</td>
      <td style="text-align:center">${{s.count}}</td>
      <td style="text-align:center">${{s.profitable}}</td>
      <td style="font-weight:700;color:${{(s.profitable/s.count)>=0.7?'#16a34a':s.profitable/s.count>=0.5?'#d97706':'#dc2626'}}">${{profRate}}</td>
      <td style="font-weight:700;color:${{(s.median_eps||0)>1?'#c2410c':(s.median_eps||0)>0?'#16a34a':'#dc2626'}}">${{fv(s.median_eps,2)}}</td>
      <td style="color:${{yoyClr}}">${{s.median_rev_yoy!=null?pct(s.median_rev_yoy):'—'}}</td>
      <td style="color:#64748b">${{s.median_gm!=null?fv(s.median_gm)+'%':'—'}}</td>
      <td style="font-size:11px;color:#64748b">${{top3}}</td>
    </tr>`;
  }}).join('');

  // Top EPS table
  document.getElementById('tbodyOtcTopEps').innerHTML = (O.top_eps||[]).slice(0,15).map((c,i)=>`<tr>
    <td style="color:#94a3b8">${{i+1}}</td>
    <td><b>${{c.code}}</b></td>
    <td style="font-size:11px">${{(c.name||'').split(' ')[0]}}</td>
    <td style="font-weight:700;color:#c2410c">${{fv(c.eps,2)}}</td>
    <td style="color:#16a34a">${{c.gross_margin!=null?fv(c.gross_margin)+'%':'—'}}</td>
  </tr>`).join('');

  // Top gross margin table
  document.getElementById('tbodyOtcTopGm').innerHTML = (O.top_gross_margin||[]).slice(0,15).map((c,i)=>`<tr>
    <td style="color:#94a3b8">${{i+1}}</td>
    <td><b>${{c.code}}</b></td>
    <td style="font-size:11px">${{(c.name||'').split(' ')[0]}}</td>
    <td style="font-weight:700;color:#16a34a">${{fv(c.gross_margin)}}%</td>
    <td style="color:#c2410c">${{c.eps!=null?fv(c.eps,2):'—'}}</td>
  </tr>`).join('');

  // Top revenue YoY table
  document.getElementById('tbodyOtcTopYoy').innerHTML = (O.top_rev_yoy||[]).slice(0,15).map((c,i)=>`<tr>
    <td style="color:#94a3b8">${{i+1}}</td>
    <td><b>${{c.code}}</b></td>
    <td style="font-size:11px">${{(c.name||'').split(' ')[0]}}</td>
    <td style="font-weight:700;color:#16a34a">+${{fv(c.rev_yoy,1)}}%</td>
    <td style="color:#c2410c">${{c.eps!=null?fv(c.eps,2):'—'}}</td>
  </tr>`).join('');
}}

// ════════════════════════════════ DNA產業熱圖 (嵌入DNA篩選頁) ═════════════
function initDnaHeat() {{
  const D = DNA_FULLMKT || {{}};
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const heatEl = document.getElementById('dnaSecHeat');
  if (!heatEl) return;
  const maxBs = Math.max(...(D.sector_summary||[]).map(s=>s.avg_bull_signs||0), 1);
  heatEl.innerHTML = (D.sector_summary||[]).slice(0,28).map(s => {{
    const ratio = (s.avg_bull_signs||0) / maxBs;
    const bg    = ratio > 0.7 ? '#166534' : ratio > 0.5 ? '#15803d' : ratio > 0.35 ? '#1e3a5f' : '#1e293b';
    const col   = ratio > 0.5 ? '#86efac' : ratio > 0.35 ? '#93c5fd' : '#94a3b8';
    return `<div style="padding:4px 8px;border-radius:4px;background:${{bg}};cursor:pointer;font-size:11px;color:${{col}}"
      onclick="document.getElementById('dsSectorFilter').value='${{s.sector}}';renderDnaScreen()">
      ${{s.sector}}<br><b>${{fv(s.avg_bull_signs,1)}}</b>訊 ${{fv(s.bull_pct,0)}}%▲</div>`;
  }}).join('');
}}

// ════════════════════════════════ TRIPLE CONFIRMED REPORT ════════════════════
function initTripleReport() {{
  const T   = TRIPLEREPORTS;
  const fv  = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct = (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;
  const colPct = (v) => v>=10?'#c2410c':v>=3?'#16a34a':v>=-3?'#374151':v>=-10?'#ca8a04':'#dc2626';

  document.getElementById('tripleCardsContainer').innerHTML =
    (T.reports||[]).map(r => {{
      const sb = r.score_breakdown || {{}};
      const va = r.valuation       || {{}};
      const mo = r.momentum        || {{}};
      const rv = r.relative_strength || {{}};
      const bt = r.backtest        || {{}};
      const my = r.may_outlook     || {{}};
      const dna= r.dna_signals     || [];

      const dnaRow = dna.map(s=>
        `<div style="display:flex;align-items:center;gap:6px;padding:3px 0;border-bottom:1px solid #f1f5f9">
           <span style="font-size:16px">${{s.ok?'✅':'⬜'}}</span>
           <span style="font-size:13px;color:${{s.ok?'#065f46':'#94a3b8'}};font-weight:${{s.ok?'600':'400'}}">${{s.signal}}</span>
           ${{s.value!=null?`<span style="margin-left:auto;font-size:12px;color:#64748b">${{s.value}}</span>`:''}}
         </div>`).join('');

      const scoreBar = (pts,max=25) => {{
        const w = Math.round(pts/max*100);
        const col = pts>=20?'#16a34a':pts>=12?'#2563eb':pts>=6?'#ca8a04':'#dc2626';
        return `<div style="background:#e2e8f0;border-radius:4px;height:8px;margin:2px 0">
          <div style="width:${{w}}%;height:8px;background:${{col}};border-radius:4px"></div></div>`;
      }};

      return `<div style="border:2px solid #fca5a5;border-radius:16px;padding:20px;margin-bottom:20px;
                           background:linear-gradient(135deg,#fff5f5,#fffbeb)">

        <!-- Header -->
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px">
          <div>
            <div style="font-size:28px;font-weight:900;color:#7f1d1d">${{r.code}}</div>
            <div style="font-size:18px;font-weight:700;color:#374151">${{r.name.split(' ')[0]}}</div>
            <div style="font-size:13px;color:#64748b;margin-top:2px">${{r.sector}}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:42px;font-weight:900;color:#c2410c;line-height:1">${{r.grand_total.toFixed(0)}}</div>
            <div style="font-size:11px;color:#64748b">/ 100 綜合得分</div>
            <div style="margin-top:6px;font-size:13px;font-weight:700;background:#fee2e2;padding:4px 10px;border-radius:12px;color:#7f1d1d">
              ${{r.final}}</div>
          </div>
        </div>

        <!-- Score bars -->
        <div style="background:#fff;border-radius:10px;padding:12px;margin-bottom:14px">
          <div style="font-size:12px;font-weight:700;color:#374151;margin-bottom:8px">得分分解</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            ${{[['基本面','fundamental'],['技術DNA','technical'],['估值','valuation'],['動能','momentum']].map(([label,key])=>
              `<div>
                <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:2px">
                  <span>${{label}}</span><span style="font-weight:700;color:#374151">${{(sb[key]||0).toFixed(0)}}/25</span>
                </div>
                ${{scoreBar(sb[key]||0)}}
              </div>`).join('')}}
          </div>
        </div>

        <!-- 4-column data grid -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">
          <!-- Valuation -->
          <div style="background:#fff;border-radius:10px;padding:10px">
            <div style="font-size:11px;color:#64748b;font-weight:700;margin-bottom:6px">📊 估值</div>
            <div style="font-size:11px;color:#374151">PE: <b>${{va.pe!=null?fv(va.pe,1)+'x':'—'}}</b></div>
            <div style="font-size:11px;color:#374151">PB: <b>${{va.pb!=null?fv(va.pb,2)+'x':'—'}}</b></div>
            <div style="font-size:11px;color:#16a34a;font-weight:700">殖: ${{va.div_yield!=null?fv(va.div_yield,2)+'%':'—'}}</div>
            <div style="font-size:11px;color:#374151;margin-top:4px">收盤: ${{va.close!=null?fv(va.close,1):'—'}}</div>
            <div style="font-size:11px;color:#64748b">MA30: ${{va.ma30!=null?fv(va.ma30,1):'—'}}</div>
          </div>
          <!-- Momentum -->
          <div style="background:#fff;border-radius:10px;padding:10px">
            <div style="font-size:11px;color:#64748b;font-weight:700;margin-bottom:6px">⚡ 動能</div>
            <div style="font-size:11px">vs MA30:
              <b style="color:${{(mo.pct_vs_ma||0)>=0?'#16a34a':'#dc2626'}}">${{pct(mo.pct_vs_ma)}}</b></div>
            <div style="font-size:11px">vs 基準:
              <b style="color:${{(mo.pct_vs_prior||0)>=0?'#16a34a':'#dc2626'}}">${{pct(mo.pct_vs_prior)}}</b></div>
            <div style="font-size:11px;margin-top:4px">RS20d:
              <b style="color:${{colPct(rv.rs_20d||0)}}">${{pct(rv.rs_20d)}}</b></div>
            <div style="font-size:11px">RS60d:
              <b style="color:${{colPct(rv.rs_60d||0)}}">${{pct(rv.rs_60d)}}</b></div>
            <div style="font-size:11px;color:${{(rv.pct_from_52w_high||0)>=-3?'#c2410c':'#64748b'}}">
              52wH: ${{pct(rv.pct_from_52w_high)}}</div>
          </div>
          <!-- Backtest -->
          <div style="background:#fff;border-radius:10px;padding:10px">
            <div style="font-size:11px;color:#64748b;font-weight:700;margin-bottom:6px">🔬 回測</div>
            <div style="font-size:11px">20d均: <b style="color:${{(bt.avg_20d||0)>=0?'#16a34a':'#dc2626'}}">${{bt.avg_20d!=null?pct(bt.avg_20d):'—'}}</b></div>
            <div style="font-size:11px">20d勝: <b style="color:${{(bt.win_20d||0)>=55?'#16a34a':'#ca8a04'}}">${{bt.win_20d!=null?fv(bt.win_20d,0)+'%':'—'}}</b></div>
            <div style="font-size:11px;margin-top:4px">60d均: <b style="color:${{(bt.avg_60d||0)>=0?'#16a34a':'#dc2626'}}">${{bt.avg_60d!=null?pct(bt.avg_60d):'—'}}</b></div>
            <div style="font-size:11px">60d勝: <b style="color:${{(bt.win_60d||0)>=55?'#16a34a':'#ca8a04'}}">${{bt.win_60d!=null?fv(bt.win_60d,0)+'%':'—'}}</b></div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">觸發次數: ${{bt.num_signals||0}}</div>
          </div>
          <!-- May Outlook -->
          <div style="background:#fff;border-radius:10px;padding:10px">
            <div style="font-size:11px;color:#64748b;font-weight:700;margin-bottom:6px">📅 5月預測</div>
            <div style="font-size:12px;font-weight:700;color:#065f46">${{my.verdict||'—'}}</div>
            <div style="font-size:11px;margin-top:4px">4月YoY:
              <b style="color:${{(my.apr_yoy||0)>=20?'#c2410c':'#374151'}}">${{my.apr_yoy!=null?pct(my.apr_yoy,0):'—'}}</b></div>
            <div style="font-size:11px">趨勢: ${{my.accel||'—'}}</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">預估: ${{my.est_range}}</div>
          </div>
        </div>

        <!-- DNA signals -->
        <div style="background:#fff;border-radius:10px;padding:12px;margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div style="font-size:12px;font-weight:700;color:#374151">🧬 大飆股DNA訊號</div>
            <div style="font-size:18px;font-weight:900;color:${{r.bull_signs>=5?'#c2410c':r.bull_signs>=3?'#16a34a':'#ca8a04'}}">
              ${{r.bull_signs}}/6</div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 12px">${{dnaRow}}</div>
        </div>

        <!-- Investment thesis -->
        <div style="background:linear-gradient(135deg,#fffbeb,#fef3c7);border-radius:10px;padding:12px;
                    border:1px solid #fde68a">
          <div style="font-size:11px;color:#92400e;font-weight:700;margin-bottom:4px">💡 投資論點</div>
          <div style="font-size:13px;color:#78350f;font-weight:600">${{r.thesis}}</div>
          ${{r.portfolio_weight!=null?`<div style="margin-top:6px;font-size:11px;color:#64748b">最大夏普組合建議持倉: <b>${{fv(r.portfolio_weight,1)}}%</b></div>`:''}}
        </div>
      </div>`;
    }}).join('');
}}

// ════════════════════════════════ MAY REVENUE PREVIEW ════════════════════════
function initMayPreview() {{
  const M  = MAYPREVIEW;
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct= (v,d=0) => {{
    if (v==null) return '<td>—</td>';
    const col = v>=50?'#c2410c':v>=15?'#16a34a':v>=-5?'#374151':v>=-20?'#ca8a04':'#dc2626';
    return `<td style="color:${{col}};font-weight:${{Math.abs(v)>=15?'700':'400'}}">${{v>=0?'+':''}}${{fv(v,0)}}%</td>`;
  }};
  const accelBadge = a => {{
    if (!a) return '—';
    const m = {{ACCELERATING:'🔼 加速',DECELERATING:'🔽 減速',STABLE:'➡️ 穩定'}};
    return m[a] || a;
  }};

  // Chips
  const sm = M.summary || {{}};
  document.getElementById('mayChips').innerHTML = [
    {{label:'🔥 超預期強勢', count:sm.beat||0,    col:'#065f46', bg:'#d1fae5'}},
    {{label:'⬛ 符合預期',   count:sm.in_line||0,  col:'#1e3a5f', bg:'#dbeafe'}},
    {{label:'⚠️ 衰退風險',  count:sm.miss||0,     col:'#7c2d12', bg:'#fee2e2'}},
    {{label:'📅 預計發布',  count:'6/10',         col:'#064e3b', bg:'#a7f3d0'}},
  ].map(c=>
    `<div style="padding:8px 16px;border-radius:20px;background:${{c.bg}};color:${{c.col}};font-weight:700;font-size:14px">
       ${{c.label}} <span style="font-size:18px;margin-left:4px">${{c.count}}</span>
     </div>`).join('');

  // TRIPLE preview
  document.getElementById('tbodyTriplePreview').innerHTML = (M.triple_preview||[]).map(r=>`
    <tr style="background:#fffbeb">
      <td><b style="color:#92400e">${{r.code}}</b></td>
      <td style="font-weight:700">${{r.name.split(' ')[0]}}</td>
      ${{pct(r.apr_yoy)}}
      ${{pct(r.apr_cum_yoy)}}
      ${{pct(r.apr_mom)}}
      <td style="font-size:12px">${{accelBadge(r.apr_accel)}}</td>
      <td style="color:#064e3b">
        ${{r.may_est_low!=null?r.may_est_low+'–'+r.may_est_high+'億':'—'}}</td>
      <td style="font-weight:700;color:${{r.rev_score>=4?'#c2410c':r.rev_score>=2?'#16a34a':'#374151'}}">
        ${{r.outlook}}</td>
    </tr>`).join('');

  // Beat candidates (score >= 4)
  const strong_beat = (M.beat_candidates||[]).filter(r=>r.rev_score>=4).slice(0,15);
  document.getElementById('tbodyBeatCandidates').innerHTML = strong_beat.map(r=>`
    <tr>
      <td><b>${{r.code}}</b></td>
      <td style="font-size:13px">${{r.name.split(' ')[0]}}</td>
      ${{pct(r.apr_yoy)}}
      ${{pct(r.apr_mom)}}
      <td style="font-size:12px">${{accelBadge(r.apr_accel)}}</td>
      <td style="font-weight:700;color:#1e3a5f">${{r.grand!=null?fv(r.grand,0):'—'}}</td>
      <td style="text-align:center">${{r.bull_signs}}/6</td>
      <td style="font-size:12px;color:#065f46;font-weight:600">${{r.outlook}}</td>
    </tr>`).join('');

  // Miss risks
  document.getElementById('tbodyMissRisks').innerHTML = (M.miss_risks||[]).map(r=>`
    <tr>
      <td><b>${{r.code}}</b></td>
      <td style="font-size:13px">${{r.name.split(' ')[0]}}</td>
      ${{pct(r.apr_yoy)}}
      ${{pct(r.apr_mom)}}
      <td style="font-size:12px">${{accelBadge(r.apr_accel)}}</td>
      <td style="font-weight:700;color:#374151">${{r.grand!=null?fv(r.grand,0):'—'}}</td>
      <td style="font-size:12px;color:#dc2626;font-weight:600">${{r.outlook}}</td>
    </tr>`).join('');
}}

// ════════════════════════════════ WATCH ALERTS ═══════════════════════════════
function initWatchAlerts() {{
  const W  = WATCHALERTS;
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct= (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;

  // Summary chips
  const sm = W.summary || {{}};
  const chips = [
    {{label:'🚀 即將TRIPLE', count: sm.almost_triple||0, col:'#c2410c', bg:'#fee2e2'}},
    {{label:'🧬 DNA 5/6',   count: sm.dna_5of6||0,      col:'#7c3aed', bg:'#ede9fe'}},
    {{label:'📈 突破均線',   count: sm.ma_crossing||0,   col:'#065f46', bg:'#d1fae5'}},
    {{label:'🏔 創52週高',   count: sm.near_52w_high||0, col:'#1d4ed8', bg:'#dbeafe'}},
    {{label:'💎 TRIPLE',    count: sm.triple_confirmed||0,col:'#92400e',bg:'#fef3c7'}},
  ];
  document.getElementById('alertChips').innerHTML = chips.map(c =>
    `<div style="padding:8px 16px;border-radius:20px;background:${{c.bg}};color:${{c.col}};
                 font-weight:700;font-size:14px">
      ${{c.label}} <span style="font-size:18px;margin-left:4px">${{c.count}}</span>
    </div>`
  ).join('');

  // A: Almost Triple
  document.getElementById('tbodyAlmostTriple').innerHTML = (W.almost_triple||[]).map(r => `
    <tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td style="font-weight:700;color:#1e3a5f">${{fv(r.grand,1)}}</td>
      <td style="font-weight:700;color:${{r.grand_gap<=1?'#dc2626':r.grand_gap<=4?'#d97706':'#374151'}}">
        ${{r.grand_gap>0?'+'+fv(r.grand_gap,1):'達標!'}}</td>
      <td style="text-align:center">${{r.bull_signs}}/6</td>
      <td style="color:#64748b">${{r.pe!=null?fv(r.pe,1)+'x':'—'}}</td>
      <td style="color:#64748b">${{r.div!=null?fv(r.div,2)+'%':'—'}}</td>
      <td style="font-size:12px">${{r.final||'—'}}</td>
      <td style="font-size:12px;color:#7c3aed;font-weight:600">${{r.needs||'—'}}</td>
    </tr>`).join('');

  // B: DNA 5/6
  document.getElementById('tbodyDna5of6').innerHTML = (W.dna_5of6||[]).map(r => `
    <tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td style="font-weight:700;text-align:center">${{r.bull_signs}}/6</td>
      <td style="color:#c2410c;font-weight:600">${{r.missing||'—'}}</td>
      <td style="color:#1e3a5f;font-weight:700">${{r.grand!=null?fv(r.grand,0):'—'}}</td>
      <td style="font-size:12px">${{r.final||r.verdict||'—'}}</td>
    </tr>`).join('');

  // C: MA Crossing
  document.getElementById('tbodyMaCross').innerHTML = (W.ma_crossing||[]).map(r => `
    <tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td>${{r.close!=null?fv(r.close,1):'—'}}</td>
      <td style="color:#64748b">${{r.ma30!=null?fv(r.ma30,1):'—'}}</td>
      <td style="font-weight:700;color:#d97706">${{pct(r.pct_vs_ma)}}</td>
      <td style="font-weight:700;color:#16a34a">${{pct(r.pct_vs_prior)}}</td>
      <td style="color:#1e3a5f;font-weight:700">${{r.grand!=null?fv(r.grand,0):'—'}}</td>
      <td style="font-size:12px">${{r.final||'—'}}</td>
    </tr>`).join('');

  // D: Near 52w High
  document.getElementById('tbodyNear52w').innerHTML = (W.near_52w_high||[]).map(r => `
    <tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td style="font-weight:700;color:${{(r.pct_from_52w_high||0)>=-1?'#16a34a':'#374151'}}">
        ${{pct(r.pct_from_52w_high)}}</td>
      <td style="font-weight:700;color:#c2410c">${{pct(r.rs_60d)}}</td>
      <td style="color:#374151">${{pct(r.ret_60d)}}</td>
      <td style="text-align:center">${{r.bull_signs}}/6</td>
      <td style="color:#1e3a5f;font-weight:700">${{r.grand!=null?fv(r.grand,0):'—'}}</td>
      <td style="font-size:12px">${{r.final||'—'}}</td>
    </tr>`).join('');

  // E: Triple snapshot
  document.getElementById('tbodyTripleSnap').innerHTML = (W.triple_upside||[]).map(r => `
    <tr style="background:#fffbeb;cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖">
      <td><b style="color:#92400e">${{r.code}}</b></td>
      <td style="font-weight:700">${{r.name.split(' ')[0]}}</td>
      <td style="font-weight:800;color:#c2410c;font-size:16px">${{fv(r.grand,0)}}</td>
      <td style="text-align:center">${{r.bull_signs}}/6</td>
      <td style="color:#64748b">${{r.pe!=null?fv(r.pe,1)+'x':'—'}}</td>
      <td style="color:#16a34a;font-weight:700">${{r.div!=null?fv(r.div,2)+'%':'—'}}</td>
      <td style="color:${{(r.rs_60d||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">
        ${{r.rs_60d!=null?pct(r.rs_60d):'—'}}</td>
      <td style="font-weight:700;color:${{r.upside_pct!=null&&r.upside_pct>20?'#c2410c':r.upside_pct!=null&&r.upside_pct>0?'#16a34a':'#64748b'}}">
        ${{r.upside_pct!=null?'+'+fv(r.upside_pct)+'%':'待計算'}}</td>
    </tr>`).join('');
}}

// ════════════════════════════════ SECTOR HEATMAP ═════════════════════════════
function initSectorMap() {{
  const S   = SECTORDATA;
  const fv  = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const sectors = S.sectors || [];

  // Signal → color mapping
  const sigColor = {{
    '🔥 強勢': {{bg:'#fef2f2', border:'#ef4444', text:'#7f1d1d'}},
    '📈 偏多': {{bg:'#f0fdf4', border:'#22c55e', text:'#14532d'}},
    '⬛ 中性': {{bg:'#f8fafc', border:'#94a3b8', text:'#334155'}},
    '📉 偏空': {{bg:'#fafafa', border:'#94a3b8', text:'#64748b'}},
  }};

  // Heatmap cards
  document.getElementById('sectorGrid').innerHTML = sectors.map(r => {{
    const sc = sigColor[r.signal] || sigColor['⬛ 中性'];
    const barW = r.avg_grand ? Math.round((r.avg_grand - 30) / 40 * 100) : 0;
    const topStocks = (r.stocks||[]).slice(0,3).map(s=>s.code).join(' · ');
    return `<div onclick="window._showSector('${{r.sector}}')"
               style="border:2px solid ${{sc.border}};border-radius:12px;padding:14px;
                      background:${{sc.bg}};cursor:pointer;transition:transform 0.1s"
               onmouseover="this.style.transform='scale(1.02)'"
               onmouseout="this.style.transform='scale(1)'">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <b style="color:${{sc.text}};font-size:15px">${{r.sector}}</b>
        <span style="font-size:12px;color:#64748b">${{r.n_stocks}}支</span>
      </div>
      <div style="font-size:22px;font-weight:800;color:${{sc.text}};margin-bottom:6px">
        ${{r.avg_grand!=null?r.avg_grand.toFixed(0):'—'}}
        <span style="font-size:13px;font-weight:400;color:#64748b">信念分</span>
      </div>
      <div style="background:#e2e8f0;border-radius:4px;height:6px;margin-bottom:8px">
        <div style="width:${{barW}}%;height:6px;background:${{sc.border}};border-radius:4px"></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px;color:#64748b">
        <span>DNA: ${{r.avg_bull_signs!=null?r.avg_bull_signs.toFixed(1):'—'}}/6</span>
        <span>RS60: ${{r.avg_rs_60d!=null?(r.avg_rs_60d>=0?'+':'')+r.avg_rs_60d.toFixed(1)+'%':'—'}}</span>
        <span>PE: ${{r.avg_pe!=null?r.avg_pe.toFixed(1)+'x':'—'}}</span>
        <span>殖利率: ${{r.avg_yield!=null?r.avg_yield.toFixed(2)+'%':'—'}}</span>
      </div>
      <div style="margin-top:8px;font-size:11px;color:#94a3b8">${{topStocks}}</div>
      <div style="margin-top:6px;font-size:13px;font-weight:700;color:${{sc.text}}">${{r.signal}}</div>
      ${{r.triple_confirmed>0?`<div style="margin-top:4px;font-size:11px;background:#fee2e2;padding:2px 6px;border-radius:8px;display:inline-block;color:#991b1b">🚀 ${{r.triple_confirmed}} TRIPLE</div>`:''}}</div>`;
  }}).join('');

  // Summary table
  document.getElementById('tbodySectors').innerHTML = sectors.map((r,i) => {{
    const rsCol = (r.avg_rs_60d||0)>=10?'#16a34a':(r.avg_rs_60d||0)>=-10?'#374151':'#dc2626';
    return `<tr onclick="window._showSector('${{r.sector}}')" style="cursor:pointer">
      <td><b>${{r.sector}}</b></td>
      <td style="text-align:center">${{r.n_stocks}}</td>
      <td style="font-weight:700;color:#1e3a5f">${{r.avg_grand!=null?r.avg_grand.toFixed(1):'—'}}</td>
      <td style="text-align:center">${{r.avg_bull_signs!=null?r.avg_bull_signs.toFixed(1)+'/6':'—'}}</td>
      <td style="color:${{rsCol}};font-weight:600">
        ${{r.avg_rs_60d!=null?(r.avg_rs_60d>=0?'+':'')+r.avg_rs_60d.toFixed(1)+'%':'—'}}</td>
      <td style="color:#64748b">${{r.avg_pe!=null?r.avg_pe.toFixed(1)+'x':'—'}}</td>
      <td style="color:#64748b">${{r.avg_yield!=null?r.avg_yield.toFixed(2)+'%':'—'}}</td>
      <td style="font-weight:700;color:#c2410c">${{r.triple_confirmed>0?'🚀×'+r.triple_confirmed:'—'}}</td>
      <td style="font-size:13px">${{r.signal}}</td>
    </tr>`;
  }}).join('');

  // Sector detail on click
  window._showSector = (sectorName) => {{
    const r = sectors.find(x => x.sector === sectorName);
    if (!r) return;
    document.getElementById('sectorDetail').style.display = 'block';
    document.getElementById('sectorDetailTitle').textContent = `🏭 ${{sectorName}} — 個股明細 (${{r.n_stocks}}支)`;
    document.getElementById('tbodySectorStocks').innerHTML = (r.stocks||[]).map(s => {{
      const finalCol = s.final&&s.final.includes('TRIPLE')?'#c2410c':s.final&&s.final.includes('STRONG')?'#2563eb':'#374151';
      return `<tr>
        <td><b>${{s.code}}</b></td>
        <td style="font-size:13px">${{s.name.split(' ')[0]}}</td>
        <td style="font-weight:700;color:#1e3a5f">${{s.grand!=null?s.grand.toFixed(0):'—'}}</td>
        <td style="text-align:center">${{s.bull_signs!=null?s.bull_signs+'/6':'—'}}</td>
        <td style="color:${{(s.rs_60d||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">
          ${{s.rs_60d!=null?(s.rs_60d>=0?'+':'')+s.rs_60d.toFixed(1)+'%':'—'}}</td>
        <td style="color:#64748b">${{s.pe!=null?s.pe.toFixed(1)+'x':'—'}}</td>
        <td style="color:#64748b">${{s.div_yield!=null?s.div_yield.toFixed(2)+'%':'—'}}</td>
        <td style="font-size:12px;color:${{finalCol}}">${{s.final||'—'}}</td>
      </tr>`;
    }}).join('');
    document.getElementById('sectorDetail').scrollIntoView({{behavior:'smooth'}});
  }};
}}

// ════════════════════════════════ PORTFOLIO OPTIMIZER ════════════════════════
function initPortOpt() {{
  const P     = PORTOPT;
  const fv    = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct   = (v,d=1,bold=false) => {{
    if (v==null) return '—';
    const col = v>=20?'#c2410c':v>=5?'#16a34a':v>=-5?'#374151':v>=-15?'#ca8a04':'#dc2626';
    const fw  = (bold||Math.abs(v)>=5) ? '700' : '400';
    return `<span style="color:${{col}};font-weight:${{fw}}">${{v>=0?'+':''}}${{fv(v,d)}}%</span>`;
  }};

  const STRATS = [
    {{key:'max_sharpe', label:'最大夏普率', color:'#0ea5e9'}},
    {{key:'min_vol',    label:'最小波動率', color:'#10b981'}},
    {{key:'risk_parity',label:'風險平價',   color:'#8b5cf6'}},
    {{key:'conviction', label:'信念加權',   color:'#f59e0b'}},
  ];
  let activeStrat = 'max_sharpe';

  function renderStrat(key) {{
    activeStrat = key;
    const meta  = (P.portfolios_meta||[]).find(m=>m.label===STRATS.find(s=>s.key===key).label)||{{}};
    const alloc = P[key]||{{}};
    const items = alloc.allocations||[];

    // KPI cards
    document.getElementById('portKpiCards').innerHTML = [
      {{label:'📈 預期年化報酬', val: meta.ann_return_pct!=null? (meta.ann_return_pct>=0?'+':'')+fv(meta.ann_return_pct)+'%':'—', col:'#0f172a'}},
      {{label:'📊 年化波動率',   val: meta.ann_vol_pct!=null? fv(meta.ann_vol_pct)+'%':'—',                                  col:'#1e3a5f'}},
      {{label:'⚡ 夏普比率',    val: meta.sharpe!=null? fv(meta.sharpe,2):'—',                                              col:'#065f46'}},
      {{label:'🏢 持股數',      val: items.length+'支',                                                                      col:'#4c1d95'}},
    ].map(c=>`<div class="kpi-card" style="background:#f8fafc;border:2px solid #e2e8f0">
      <div class="kpi-label">${{c.label}}</div>
      <div class="kpi-value" style="color:${{c.col}};font-size:22px">${{c.val}}</div>
    </div>`).join('');

    // Allocation table
    document.getElementById('tbodyPortAlloc').innerHTML = items.map((a,i)=>{{
      const barW = Math.round(a.weight_pct * 4);
      const finCol = a.final&&a.final.includes('TRIPLE')?'#c2410c':a.final&&a.final.includes('STRONG')?'#2563eb':'#374151';
      return `<tr>
        <td><b>${{a.code}}</b></td>
        <td style="font-size:13px">${{a.name.split(' ')[0]}}</td>
        <td>
          <div style="display:flex;align-items:center;gap:6px">
            <div style="width:${{barW}}px;height:8px;background:#0ea5e9;border-radius:4px;min-width:4px"></div>
            <b style="color:#0f172a">${{fv(a.weight_pct,1)}}%</b>
          </div>
        </td>
        <td>${{pct(a.exp_ret_pct)}}</td>
        <td style="color:#64748b">${{fv(a.vol_pct)}}%</td>
        <td style="font-weight:700;color:#1e3a5f">${{fv(a.grand,0)}}</td>
        <td style="text-align:center">${{a.bull_signs!=null?a.bull_signs+'/6':'—'}}</td>
        <td style="font-size:12px;color:${{finCol}}">${{a.final||'—'}}</td>
      </tr>`;
    }}).join('');
  }}

  // Strategy selector buttons
  document.getElementById('portStratBtns').innerHTML = STRATS.map(s=>
    `<button onclick="window._poRender('${{s.key}}')"
      style="padding:6px 14px;border-radius:20px;border:2px solid ${{s.color}};
             background:${{s.key===activeStrat?s.color:'#fff'}};
             color:${{s.key===activeStrat?'#fff':s.color}};font-weight:700;cursor:pointer;font-size:13px">
      ${{s.label}}</button>`
  ).join('');
  window._poRender = (key) => {{
    renderStrat(key);
    // Update button styles
    STRATS.forEach(s => {{
      const btns = document.querySelectorAll('#portStratBtns button');
      btns.forEach(b => {{
        if (b.textContent.trim() === s.label) {{
          b.style.background = s.key===key ? s.color : '#fff';
          b.style.color      = s.key===key ? '#fff'  : s.color;
        }}
      }});
    }});
  }};

  // Concentration risk
  document.getElementById('tbodyPortRisk').innerHTML = (P.concentration_risk||[]).map(p=>`
    <tr>
      <td><b>${{p.a}}</b></td><td>${{p.name_a.split(' ')[0]}}</td>
      <td><b>${{p.b}}</b></td><td>${{p.name_b.split(' ')[0]}}</td>
      <td style="font-weight:700;color:${{Math.abs(p.r)>=0.85?'#dc2626':Math.abs(p.r)>=0.75?'#ca8a04':'#374151'}}">
        ${{fv(p.r,2)}}</td>
      <td style="font-size:12px">${{Math.abs(p.r)>=0.8?'⚠️ 高度集中':'🔶 適度分散'}}</td>
    </tr>`).join('');

  // Draw efficient frontier
  const ef = P.efficient_frontier||[];
  if (ef.length > 1) {{
    const canvas = document.getElementById('efCanvas');
    if (canvas && canvas.getContext) {{
      const ctx2 = canvas.getContext('2d');
      canvas.width  = canvas.offsetWidth  || 600;
      canvas.height = canvas.offsetHeight || 200;
      const W = canvas.width, H = canvas.height, PAD = 30;
      const vols = ef.map(p=>p.vol), rets = ef.map(p=>p.ret);
      const minV = Math.min(...vols), maxV = Math.max(...vols)*1.1;
      const minR = Math.min(...rets)*0.8, maxR = Math.max(...rets)*1.1;
      const sx = v => PAD + (v-minV)/(maxV-minV)*(W-2*PAD);
      const sy = r => H-PAD - (r-minR)/(maxR-minR)*(H-2*PAD);
      // Gradient fill
      const grad = ctx2.createLinearGradient(0,0,W,0);
      grad.addColorStop(0,'rgba(16,185,129,0.15)');
      grad.addColorStop(1,'rgba(14,165,233,0.15)');
      ctx2.fillStyle = '#0f172a'; ctx2.fillRect(0,0,W,H);
      // Curve
      ctx2.beginPath(); ctx2.strokeStyle='#38bdf8'; ctx2.lineWidth=2;
      ef.forEach((p,i) => i===0 ? ctx2.moveTo(sx(p.vol),sy(p.ret)) : ctx2.lineTo(sx(p.vol),sy(p.ret)));
      ctx2.stroke();
      // Axes labels
      ctx2.fillStyle='#94a3b8'; ctx2.font='11px sans-serif'; ctx2.textAlign='center';
      ctx2.fillText('← 波動率低                高 →', W/2, H-4);
      ctx2.save(); ctx2.translate(12, H/2); ctx2.rotate(-Math.PI/2);
      ctx2.fillText('← 報酬低      高 →', 0, 0); ctx2.restore();
    }}
  }}

  renderStrat(activeStrat);
}}

// ════════════════════════════════ BACKTEST ═══════════════════════════════════
function initBacktest() {{
  const B = BACKTEST;
  const agg = B.aggregate || {{}};
  const per = B.per_stock  || [];

  const fv  = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct = (v,d=1) => v==null?'<td>—</td>':`<td style="color:${{v>=0?'#16a34a':'#dc2626'}};font-weight:600">${{v>=0?'+':''}}${{fv(v,d)}}%</td>`;
  const win = v => v==null?'<td>—</td>':`<td style="color:${{v>=60?'#16a34a':v>=50?'#ca8a04':'#dc2626'}};font-weight:600">${{fv(v,0)}}%</td>`;

  const horizons = [['10d','10日'],['20d','20日'],['60d','60日']];
  document.getElementById('btAggCards').innerHTML = horizons.map(([k,label]) => {{
    const a = agg[k] || {{}};
    const col = (a.avg||0) >= 5 ? '#065f46' : (a.avg||0) >= 0 ? '#1e40af' : '#7c2d12';
    return `<div class="kpi-card" style="background:#f0fdf4;border:1px solid #86efac">
      <div class="kpi-label">${{label}}平均報酬</div>
      <div class="kpi-value" style="color:${{col}}">${{(a.avg>=0?'+':'')}}${{fv(a.avg)}}%</div>
      <div style="font-size:12px;color:#374151;margin-top:6px">
        勝率 <b>${{fv(a.win_pct,0)}}%</b> | 中位數 ${{(a.median>=0?'+':'')}}${{fv(a.median)}}%
        | n=${{a.n||0}}
      </div>
    </div>`;
  }}).join('');

  document.getElementById('tbodyBacktest').innerHTML = per.slice(0,25).map((r,i) => `
    <tr>
      <td style="color:#94a3b8;font-size:12px">${{i+1}}</td>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td style="text-align:center">${{r.num_signals}}</td>
      ${{pct(r.avg_10d)}}${{win(r.win_10d)}}
      ${{pct(r.avg_20d)}}${{win(r.win_20d)}}
      ${{pct(r.avg_60d)}}${{win(r.win_60d)}}
      <td style="font-size:12px">${{r.current_verdict||'—'}}</td>
    </tr>`).join('');

  // Currently signaling stocks with good historical track record
  const nowSignaling = per.filter(r =>
    r.current_verdict && (r.current_verdict.includes('大飆股') || r.current_verdict.includes('BULL') || r.current_verdict.includes('上攻'))
  ).sort((a,b) => (b.avg_20d||0) - (a.avg_20d||0));

  document.getElementById('tbodyBtNow').innerHTML = nowSignaling.slice(0,15).map(r => `
    <tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td style="color:${{(r.avg_20d||0)>=10?'#c2410c':(r.avg_20d||0)>=5?'#1e40af':'#374151'}};font-weight:700">
        ${{(r.avg_20d>=0?'+':'')}}${{fv(r.avg_20d)}}%</td>
      <td style="color:${{(r.win_20d||0)>=65?'#16a34a':(r.win_20d||0)>=50?'#ca8a04':'#dc2626'}};font-weight:700">
        ${{fv(r.win_20d,0)}}%</td>
      <td>${{r.num_signals}}</td>
      <td style="font-size:12px">${{r.current_verdict}}</td>
    </tr>`).join('');
}}

// ════════════════════════════════ SOP BACKTEST ═══════════════════════════════
let _sopActiveCap = '1m';
let _sopChartInst = null;

function sopShowCap(cap) {{
  _sopActiveCap = cap;
  ['1m','2m'].forEach(k => {{
    const btn = document.getElementById(`sopCapBtn${{k}}`);
    if (!btn) return;
    if (k === cap) {{
      btn.style.background = '#1e40af'; btn.style.color = '#fff';
      btn.style.border = 'none';
    }} else {{
      btn.style.background = '#1e293b'; btn.style.color = '#94a3b8';
      btn.style.border = '1px solid #334155';
    }}
  }});
  _sopRenderCap();
}}

function _sopRenderCap() {{
  const B = SOP_BACKTEST || {{}};
  const r = _sopActiveCap === '1m' ? (B.result_1m || {{}}) : (B.result_2m || {{}});
  const fv = (v, d=1, fb='—') => v == null ? fb : Number(v).toFixed(d);
  const pct = v => v == null ? '—' : (v >= 0 ? '+' : '') + fv(v) + '%';
  const col = v => v == null ? '#94a3b8' : v >= 0 ? '#22c55e' : '#ef4444';
  const initCap = r.initial_capital || (_sopActiveCap==='1m' ? 1000000 : 2000000);
  const finalVal = r.final_value || initCap;

  // KPI cards
  const kpis = [
    {{ label:'總報酬率', val:pct(r.total_return_pct), color:col(r.total_return_pct), sub:`年化 ${{pct(r.annualized_return_pct)}}` }},
    {{ label:'最大回撤', val:(r.max_drawdown_pct ? '-'+fv(r.max_drawdown_pct)+'%' : '—'), color:'#f87171', sub:'峰谷最大跌幅' }},
    {{ label:'勝率', val:(r.win_rate != null ? fv(r.win_rate,0)+'%' : '—'), color:r.win_rate>=55?'#22c55e':r.win_rate>=45?'#fbbf24':'#ef4444', sub:`交易 ${{r.closed_trades||0}} 筆` }},
    {{ label:'最終資產', val:finalVal.toLocaleString('zh-TW',{{maximumFractionDigits:0}})+'元',
       color:col(r.total_return_pct), sub:`初始 ${{initCap.toLocaleString('zh-TW')}}元` }},
  ];
  document.getElementById('sopKpiCards').innerHTML = kpis.map(k => `
    <div class="kpi-card" style="background:#0f172a;border:1px solid #334155">
      <div class="kpi-label">${{k.label}}</div>
      <div class="kpi-value" style="color:${{k.color}};font-size:22px">${{k.val}}</div>
      <div class="kpi-sub">${{k.sub}}</div>
    </div>`).join('');

  // Equity chart (ECharts)
  const eq = r.equity_curve || [];
  if (eq.length && typeof echarts !== 'undefined') {{
    if (!_sopChartInst) {{
      _sopChartInst = echarts.init(document.getElementById('sopChartEl'), 'dark');
    }}
    const dates  = eq.map(e => e.date);
    const values = eq.map(e => e.value);
    _sopChartInst.setOption({{
      backgroundColor: '#0c1220',
      grid: {{ left:60, right:20, top:30, bottom:40 }},
      xAxis: {{ type:'category', data:dates, axisLabel:{{ fontSize:10, color:'#94a3b8' }} }},
      yAxis: {{ type:'value', axisLabel:{{ formatter: v => (v/10000).toFixed(0)+'萬', fontSize:10, color:'#94a3b8' }} }},
      series: [{{
        type:'line', data:values, smooth:true, symbol:'none', lineStyle:{{width:2,color:'#38bdf8'}},
        areaStyle:{{color:{{ type:'linear', x:0,y:0,x2:0,y2:1, colorStops:[
          {{offset:0,color:'rgba(56,189,248,0.25)'}}, {{offset:1,color:'rgba(56,189,248,0.02)'}}
        ]}}}},
        markLine:{{ silent:true, data:[{{ yAxis:initCap, label:{{formatter:'初始',color:'#fbbf24'}}, lineStyle:{{color:'#fbbf24',type:'dashed'}} }}] }},
      }}],
      tooltip:{{ trigger:'axis', formatter: p => `${{p[0].name}}<br>資產: ${{Number(p[0].value).toLocaleString('zh-TW')}} 元` }},
    }});
  }}

  // Monthly returns heatmap
  const mo = r.monthly_returns || [];
  document.getElementById('sopMonthlyGrid').innerHTML = mo.map(m => {{
    const rv = m.return;
    const bg = rv >= 5 ? '#14532d' : rv >= 2 ? '#166534' : rv >= 0 ? '#15803d55' : rv >= -2 ? '#7f1d1d55' : rv >= -5 ? '#991b1b' : '#7f1d1d';
    const fc = rv >= 0 ? '#86efac' : '#fca5a5';
    return `<div style="width:80px;padding:6px 8px;border-radius:6px;background:${{bg}};text-align:center;font-size:12px">
      <div style="color:#94a3b8;font-size:10px">${{m.month}}</div>
      <div style="color:${{fc}};font-weight:700">${{rv>=0?'+':''}}${{rv.toFixed(1)}}%</div>
    </div>`;
  }}).join('');

  // Trade log
  const trades = r.trades || [];
  const pnlCol = v => v >= 0 ? '#22c55e' : '#ef4444';
  document.getElementById('sopTradesTbody').innerHTML = trades.map(t => `
    <tr>
      <td style="font-weight:700;color:#60a5fa">${{t.code}}</td>
      <td>${{t.name||''}}</td>
      <td style="font-size:11px">${{t.entry_date}}</td>
      <td style="text-align:right">${{t.entry_price}}</td>
      <td style="font-size:11px">${{t.exit_date||'持倉中'}}</td>
      <td style="text-align:right">${{t.exit_price}}</td>
      <td style="text-align:right">${{(t.shares||0).toLocaleString()}}</td>
      <td style="text-align:right;color:${{pnlCol(t.pnl||0)}};font-weight:600">${{(t.pnl||0).toLocaleString('zh-TW')}}</td>
      <td style="text-align:right;color:${{pnlCol(t.pnl_pct||0)}};font-weight:700">${{(t.pnl_pct||0)>=0?'+':''}}${{(t.pnl_pct||0).toFixed(2)}}%</td>
      <td style="font-size:11px;color:#94a3b8">${{t.exit_reason||''}}</td>
    </tr>`).join('');
}}

function initSopBacktest() {{
  const B = SOP_BACKTEST || {{}};

  // Disclaimer
  const disc = document.getElementById('sopDisclaimer');
  if (disc && B.disclaimer) disc.textContent = B.disclaimer;

  // Gap analysis
  const ga = B.gap_analysis || {{}};
  const gaps = ga.gaps || [];
  const matches = ga.matches || [];
  const sevCol = s => s.includes('🔴') ? '#ef4444' : s.includes('🟡') ? '#fbbf24' : '#22c55e';
  const gapHtml = `
    <div style="margin-bottom:12px;font-size:13px;color:#94a3b8">
      <b style="color:#f1f5f9">現行DNA系統</b>: 進場 = ${{ga.current_dna?.entry||'—'}} | 出場 = ${{ga.current_dna?.exit||'—'}}
    </div>
    <div style="margin-bottom:12px;font-size:13px;color:#94a3b8">
      <b style="color:#f1f5f9">SOP標準</b>: 進場Step1 = ${{ga.sop?.step1_market||'—'}} / Step2 = ${{ga.sop?.step2_stock||'—'}} | 出場 = ${{ga.sop?.exit_individual||'—'}}
    </div>
    <table class="data-table" style="font-size:12px">
      <thead><tr><th>嚴重性</th><th>差異項目</th><th>說明</th></tr></thead>
      <tbody>
        ${{gaps.map(g => `<tr>
          <td style="color:${{sevCol(g.sev)}};font-weight:700;white-space:nowrap">${{g.sev}}</td>
          <td style="font-weight:600;color:#e2e8f0">${{g.title}}</td>
          <td style="color:#94a3b8;font-size:11px">${{g.desc}}</td>
        </tr>`).join('')}}
      </tbody>
    </table>`;
  const gapEl = document.getElementById('sopGapTable');
  if (gapEl) gapEl.innerHTML = gapHtml;

  const matchHtml = `
    <table class="data-table" style="font-size:12px">
      <thead><tr><th>信號/條件</th><th>相容性</th><th>說明</th></tr></thead>
      <tbody>
        ${{matches.map(m => `<tr>
          <td style="font-weight:600;color:#a5f3fc">${{m.signal}}</td>
          <td style="color:${{m.compat.includes('完全')?'#22c55e':'#fbbf24'}};font-weight:700">${{m.compat}}</td>
          <td style="color:#94a3b8;font-size:11px">${{m.note}}</td>
        </tr>`).join('')}}
      </tbody>
    </table>`;
  const matchEl = document.getElementById('sopMatchTable');
  if (matchEl) matchEl.innerHTML = matchHtml;

  // DNA signals comparison table
  const sigs = ga.current_dna?.signals || [];
  if (sigs.length) {{
    const sigHtml = `<div style="margin-top:16px">
      <div class="section-title" style="margin-bottom:8px">DNA信號 vs SOP需求</div>
      <table class="data-table" style="font-size:12px">
        <thead><tr><th>信號</th><th>名稱</th><th>現況</th><th>備註</th></tr></thead>
        <tbody>
          ${{sigs.map(s => `<tr>
            <td style="font-weight:700;color:#818cf8">${{s.id}}</td>
            <td style="color:#e2e8f0">${{s.name}}</td>
            <td style="font-weight:700;color:${{s.status.includes('✅')?'#22c55e':'#f87171'}}">${{s.status}}</td>
            <td style="color:#94a3b8;font-size:11px">${{s.note}}</td>
          </tr>`).join('')}}
        </tbody>
      </table>
    </div>`;
    if (gapEl) gapEl.innerHTML += sigHtml;
  }}

  // Render 1M by default
  sopShowCap('1m');
}}

// ════════════════════════════════ AI VALUE CHAIN ═════════════════════════════
function initAiChain() {{
  const C = CHAINDATA;
  const aiLayers = C.layers.filter(l => l.id.startsWith('L'));
  const allLayers = C.layers;

  // KPI grid: top AI layers by score
  const topLayers = [...aiLayers].sort((a,b) => (b.avg_score||0) - (a.avg_score||0)).slice(0,4);
  document.getElementById('chainKpiGrid').innerHTML = topLayers.map(l => {{
    const shortLabel = l.label.split('—')[0].trim();
    const scoreCol = l.avg_score >= 55 ? '#6d28d9' : l.avg_score >= 45 ? '#16a34a' : l.avg_score >= 35 ? '#f59e0b' : '#64748b';
    return `<div class="kpi-card" style="background:linear-gradient(135deg,#eff6ff,#dbeafe)">
      <div class="kpi-label" style="color:#1d4ed8;font-size:11px">${{shortLabel}}</div>
      <div class="kpi-value" style="color:${{scoreCol}}">${{l.avg_score != null ? l.avg_score.toFixed(0) : '—'}}</div>
      <div class="kpi-sub">分 | 上漲 ${{l.avg_upside != null ? (l.avg_upside>=0?'+':'')+l.avg_upside.toFixed(0)+'%' : '—'}}</div>
    </div>`;
  }}).join('');

  // Bar chart: avg score per layer
  const maxScore = Math.max(...aiLayers.map(l => l.avg_score || 0), 70);
  document.getElementById('chainBarChart').innerHTML = aiLayers.map(l => {{
    const shortLabel = l.label.split('—')[0].trim().replace('Layer ','L');
    const barW = l.avg_score ? Math.round(l.avg_score / maxScore * 100) : 0;
    const barCol = l.avg_score >= 55 ? '#7c3aed' : l.avg_score >= 45 ? '#16a34a' : l.avg_score >= 35 ? '#f59e0b' : '#94a3b8';
    const upTxt = l.avg_upside != null ? `<span class="${{(l.avg_upside||0)>=0?'pos':'neg'}}">${{(l.avg_upside>=0?'+':'')+l.avg_upside.toFixed(0)}}%</span>` : '';
    return `<div class="bar-row" style="margin-bottom:8px">
      <div class="bar-label" style="width:100px;font-size:12px">${{shortLabel}}</div>
      <div class="bar-track" style="flex:1">
        <div class="bar-fill" style="width:${{barW}}%;background:${{barCol}};min-width:4px">
          ${{l.avg_score != null ? l.avg_score.toFixed(0) : '—'}}分
        </div>
      </div>
      <div style="width:80px;text-align:right;font-size:12px;margin-left:8px">${{upTxt}} P/E ${{l.avg_pe != null ? l.avg_pe.toFixed(0)+'x' : '—'}}</div>
    </div>`;
  }}).join('');

  // Per-layer detail cards
  const container = document.getElementById('chainLayerCards');
  container.innerHTML = allLayers.map(l => {{
    if (!l.stocks || !l.stocks.length) return '';
    const shortLabel = l.label;
    const isAI = l.id.startsWith('L');
    const borderCol = isAI ? l.theme : '#94a3b8';

    const stockRows = l.stocks.map(s => {{
      const vbadge = s.verdict ? verdictBadge(s.verdict) : '—';
      const scoreTxt = s.score != null ? scoreBar(s.score) : '—';
      const upTxt = s.upside != null
        ? `<span class="${{s.upside >= 10 ? 'pos' : s.upside < 0 ? 'neg' : ''}}">${{s.upside >= 0 ? '+' : ''}}${{s.upside.toFixed(0)}}%</span>`
        : '—';
      const cumTxt = s.cum_yoy != null
        ? `<span class="${{s.cum_yoy >= 0 ? 'pos' : 'neg'}}">${{s.cum_yoy >= 0 ? '+' : ''}}${{s.cum_yoy.toFixed(0)}}%</span>`
        : '—';
      return `<tr>
        <td><strong>${{s.code}}</strong></td>
        <td>${{s.name}}</td>
        <td>${{scoreTxt}}</td>
        <td>${{s.fwd_pe != null ? s.fwd_pe.toFixed(1)+'x' : '—'}}</td>
        <td>${{upTxt}}</td>
        <td>${{cumTxt}}</td>
        <td><span class="${{s.risk <= 15 ? 'pos' : s.risk >= 40 ? 'neg' : ''}}">${{s.risk}}</span></td>
        <td>${{vbadge}}</td>
      </tr>`;
    }}).join('');

    return `<div class="card" style="border-left:4px solid ${{borderCol}};margin-bottom:16px">
      <div class="card-pad" style="border-bottom:1px solid #f1f5f9">
        <div class="section-title" style="color:${{borderCol}}">${{shortLabel}}</div>
        <div style="font-size:12px;color:#64748b;margin-top:2px">${{l.desc}}</div>
        <div style="font-size:11px;color:#94a3b8;margin-top:4px">
          ${{l.n}}支 | 平均分 <strong>${{l.avg_score != null ? l.avg_score.toFixed(0) : '—'}}</strong> |
          平均P/E ${{l.avg_pe != null ? l.avg_pe.toFixed(1)+'x' : '—'}} |
          平均上漲空間 ${{l.avg_upside != null ? (l.avg_upside>=0?'+':'')+l.avg_upside.toFixed(1)+'%' : '—'}} |
          買進 ${{l.buy_count}}/${{l.n}}
        </div>
      </div>
      <div class="tbl-wrap">
        <table><thead><tr>
          <th>代號</th><th>名稱</th><th>分數</th><th>預估P/E</th><th>目標上漲</th><th>4月累計YoY</th><th>風險分</th><th>評級</th>
        </tr></thead>
        <tbody>${{stockRows}}</tbody>
        </table>
      </div>
    </div>`;
  }}).join('');
}}

// ════════════════════════════════ MOMENTUM ═══════════════════════════════════
function initMomentum() {{
  const M = MOMENTUM;
  const sc = M.signal_counts || {{}};
  const cards = [
    {{label:'🚀 STRONG UP', count:sc.STRONG_UP||0, color:'#14532d', bg:'#dcfce7'}},
    {{label:'📈 UP',        count:sc.UP||0,        color:'#1e3a5f', bg:'#dbeafe'}},
    {{label:'⬛ NEUTRAL',   count:sc.NEUTRAL||0,   color:'#374151', bg:'#f3f4f6'}},
    {{label:'📉 DOWN',      count:sc.DOWN||0,      color:'#7c2d12', bg:'#fee2e2'}},
    {{label:'💥 STRONG DOWN',count:sc.STRONG_DOWN||0,color:'#450a0a',bg:'#fecaca'}},
  ];
  document.getElementById('momSignalCards').innerHTML = cards.map(c => `
    <div class="kpi-card" style="background:${{c.bg}};border:1px solid rgba(0,0,0,.08)">
      <div class="kpi-label" style="color:${{c.color}}">${{c.label}}</div>
      <div class="kpi-value" style="color:${{c.color}}">${{c.count}}</div>
    </div>`).join('');

  const fv = (v, d=1) => v == null ? '—' : Number(v).toFixed(d);
  const pctCell = v => {{
    if (v == null) return '<td>—</td>';
    const cls = v > 0 ? 'color:#16a34a' : v < 0 ? 'color:#dc2626' : '';
    return `<td style="${{cls}};font-weight:600">${{v>=0?'+':''}}${{fv(v)}}%</td>`;
  }};
  const sigBadge = s => {{
    const map = {{STRONG_UP:'🚀',UP:'📈',NEUTRAL:'⬛',DOWN:'📉',STRONG_DOWN:'💥'}};
    return `<td>${{map[s]||s}}</td>`;
  }};

  const gainRow = m => `<tr><td><b>${{m.code}}</b></td><td>${{m.name.split(' ')[0]}}</td>
    <td>¥${{fv(m.prior_price)}}</td><td><b>¥${{fv(m.close)}}</b></td>
    ${{pctCell(m.pct_vs_prior)}}${{pctCell(m.pct_vs_ma)}}${{sigBadge(m.signal)}}</tr>`;

  document.getElementById('tbodyGainers').innerHTML = (M.top_gainers||[]).map(gainRow).join('');
  document.getElementById('tbodyLosers').innerHTML  = (M.top_losers||[]).map(gainRow).join('');

  document.getElementById('tbodyConvMom').innerHTML = (M.conviction_updates||[]).map(m => {{
    let thesis = '✅ 仍有效';
    if ((m.pct_vs_prior||0) > 20)  thesis = '⚠️ 已大漲 — 重新評估';
    if ((m.pct_vs_prior||0) < -10) thesis = '🟢 更好進場點';
    return `<tr><td><b>${{m.code}}</b></td><td>${{m.name.split(' ')[0]}}</td>
      <td>¥${{fv(m.prior_price)}}</td><td><b>¥${{fv(m.close)}}</b></td>
      ${{pctCell(m.pct_vs_prior)}}${{pctCell(m.pct_vs_ma)}}<td>${{thesis}}</td></tr>`;
  }}).join('');

  document.getElementById('tbodyAboveMA').innerHTML = (M.above_ma||[]).map(m =>
    `<tr><td><b>${{m.code}}</b></td><td>${{m.name.split(' ')[0]}}</td>
     <td>¥${{fv(m.close)}}</td><td>¥${{fv(m.ma30)}}</td>
     ${{pctCell(m.pct_vs_ma)}}${{sigBadge(m.signal)}}</tr>`
  ).join('');
}}

// ════════════════════════════════ DNA SCREEN ═══════════════════════════════
let _dsData = []; let _dsSortKey = 'bull_signs'; let _dsSortAsc = false;

function initDnaScreen() {{
  const D = DNA_FULLMKT || {{}};
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);

  document.getElementById('dnaScreenDate').textContent = D.data_date ? `數據日期: ${{D.data_date}}` : '';
  document.getElementById('dsTotal').textContent      = (D.total||0).toLocaleString();
  document.getElementById('dsWithPrice').textContent  = (D.with_price||0).toLocaleString();
  document.getElementById('dsStrong').textContent     = (D.strong_bull||[]).length;
  const bull3 = (D.all_results||[]).filter(r=>r.bull_signs===3||r.bull_signs===4).length;
  document.getElementById('dsBull').textContent       = bull3;
  document.getElementById('dsWeak').textContent       = D.weak_count||0;

  const sectors = [...new Set((D.all_results||[]).map(r=>r.sector||'其他').filter(Boolean))].sort();
  const sel = document.getElementById('dsSectorFilter');
  sectors.forEach(s => {{ const o=document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); }});

  _dsData = D.all_results || [];
  renderDnaScreen();
}}

function dsSort(key) {{
  if (_dsSortKey===key) {{ _dsSortAsc = !_dsSortAsc; }}
  else {{ _dsSortKey=key; _dsSortAsc=false; }}
  renderDnaScreen();
}}

function dsResetFilters() {{
  document.getElementById('dsMktFilter').value    = 'all';
  document.getElementById('dsSignalFilter').value = '3';
  document.getElementById('dsSectorFilter').value = 'all';
  document.getElementById('dsSearch').value       = '';
  closeDsModal();
  renderDnaScreen();
}}

function closeDsModal() {{
  document.getElementById('dsModal').style.display = 'none';
  if (window._dsEChart) {{ try {{ window._dsEChart.dispose(); }} catch(e){{}} window._dsEChart = null; }}
}}

document.addEventListener('keydown', e => {{ if (e.key==='Escape') {{ closeDsModal(); closeBBModal(); }} }});

// ════════════════════════ BOLLINGER BANDS MODAL (overview) ══════════════════
function closeBBModal() {{
  document.getElementById('bbModal').style.display = 'none';
  if (window._bbChart) {{ try {{ window._bbChart.dispose(); }} catch(e){{}} window._bbChart = null; }}
}}

function showBBChart(code, name) {{
  document.getElementById('bbModal').style.display = 'block';
  document.getElementById('bbModalTitle').textContent = code + '  ' + name;
  document.getElementById('bbChartEl').innerHTML = '<div style="color:#94a3b8;text-align:center;padding-top:60px;font-size:14px">載入中...</div>';
  loadSeriesMap().then(sm => {{
    const s = sm[code];
    if (!s || !s.d || s.d.length < 25) {{
      document.getElementById('bbChartEl').innerHTML = '<div style="color:#f87171;text-align:center;padding-top:60px">無法取得K線資料</div>';
      return;
    }}
    renderBBChart(code, s);
  }}).catch(() => {{
    document.getElementById('bbChartEl').innerHTML = '<div style="color:#f87171;text-align:center;padding-top:60px">資料載入失敗</div>';
  }});
}}

function renderBBChart(code, s) {{
  const raw = s.d.slice(-120);  // last 120 trading days
  const dates = raw.map(r => r[0]);
  // s.d format: [date, open, close, low, high]
  const closes = raw.map(r => r[2]);
  const N = 20;

  // Bollinger Bands (20, 2)
  const upper = [], mid = [], lower = [];
  for (let i = 0; i < closes.length; i++) {{
    if (i < N - 1) {{ upper.push(null); mid.push(null); lower.push(null); continue; }}
    const sl = closes.slice(i - N + 1, i + 1);
    const m = sl.reduce((a,b) => a+b, 0) / N;
    const sd = Math.sqrt(sl.reduce((a,b) => a+(b-m)**2, 0) / N);
    mid.push(+m.toFixed(2));
    upper.push(+(m + 2*sd).toFixed(2));
    lower.push(+(m - 2*sd).toFixed(2));
  }}

  const ohlc = raw.map(r => [r[1], r[2], r[3], r[4]]);  // [open, close, low, high] → ECharts format

  const el = document.getElementById('bbChartEl');
  if (window._bbChart) {{ try {{ window._bbChart.dispose(); }} catch(e){{}} }}
  const chart = echarts.init(el, 'dark');
  window._bbChart = chart;

  chart.setOption({{
    backgroundColor: '#0c1220',
    animation: false,
    tooltip: {{ trigger:'axis', axisPointer:{{type:'cross'}}, backgroundColor:'#1e293b', borderColor:'#3b82f6', textStyle:{{color:'#e2e8f0',fontSize:11}} }},
    legend: {{ top:4, right:8, textStyle:{{color:'#94a3b8',fontSize:11}}, data:['K線','BB上軌','BB中軌','BB下軌'] }},
    grid: {{ top:40, left:60, right:20, bottom:60 }},
    xAxis: {{ type:'category', data:dates, axisLabel:{{color:'#64748b',fontSize:10, rotate:30, interval: Math.floor(dates.length/8)}}, axisLine:{{lineStyle:{{color:'#334155'}}}} }},
    yAxis: {{ type:'value', scale:true, axisLabel:{{color:'#64748b',fontSize:10}}, splitLine:{{lineStyle:{{color:'#1e293b'}}}} }},
    dataZoom: [
      {{ type:'inside', start:0, end:100 }},
      {{ type:'slider', bottom:4, height:20, borderColor:'#334155', textStyle:{{color:'#64748b',fontSize:9}}, start:0, end:100 }}
    ],
    series: [
      {{ name:'K線', type:'candlestick', data:ohlc,
        itemStyle:{{ color:'#ef4444', color0:'#22c55e', borderColor:'#ef4444', borderColor0:'#22c55e' }} }},
      {{ name:'BB上軌', type:'line', data:upper, smooth:true, symbol:'none',
        lineStyle:{{color:'#f59e0b',width:1,type:'dashed'}}, itemStyle:{{color:'#f59e0b'}} }},
      {{ name:'BB中軌', type:'line', data:mid, smooth:true, symbol:'none',
        lineStyle:{{color:'#60a5fa',width:1.5}}, itemStyle:{{color:'#60a5fa'}} }},
      {{ name:'BB下軌', type:'line', data:lower, smooth:true, symbol:'none',
        lineStyle:{{color:'#f59e0b',width:1,type:'dashed'}}, itemStyle:{{color:'#f59e0b'}},
        areaStyle:{{color:'rgba(245,158,11,0.04)'}} }}
    ]
  }});
}}

function renderDnaScreen() {{
  const fv = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct= (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;

  const mkt  = document.getElementById('dsMktFilter').value;
  const sig  = document.getElementById('dsSignalFilter').value;
  const sec  = document.getElementById('dsSectorFilter').value;
  const srch = (document.getElementById('dsSearch').value||'').toLowerCase();

  let rows = _dsData.filter(r => {{
    if (mkt !== 'all' && r.market !== mkt) return false;
    if (sec !== 'all' && (r.sector||'其他') !== sec) return false;
    if (sig === '6'    && r.bull_signs < 6) return false;
    if (sig === '5'    && r.bull_signs < 5) return false;
    if (sig === '4'    && r.bull_signs < 4) return false;
    if (sig === '3'    && r.bull_signs < 3) return false;
    if (sig === 'weak' && r.bull_signs > 1) return false;
    if (srch && !r.code.toLowerCase().includes(srch) && !(r.name||'').toLowerCase().includes(srch)) return false;
    return true;
  }});

  const k = _dsSortKey; const asc = _dsSortAsc;
  rows.sort((a,b) => {{
    const av = a[k], bv = b[k];
    if (av==null && bv==null) return 0;
    if (av==null) return 1; if (bv==null) return -1;
    return asc ? av-bv : bv-av;
  }});

  document.getElementById('dsCount').textContent = `顯示 ${{rows.length}} 筆`;

  const verdictColor = v => v.includes('🚀')?'#22c55e':v.includes('📈')?'#86efac':v.includes('📉')?'#f87171':'#94a3b8';
  const diColor  = v => v==null?'#94a3b8':v>50?'#22c55e':v>30?'#86efac':'#e2e8f0';
  const rsi4Color= v => v==null?'#94a3b8':v>77?'#22c55e':v>60?'#86efac':'#e2e8f0';
  const wr50Color= v => v==null?'#94a3b8':v<20?'#22c55e':v>80?'#f87171':'#e2e8f0';
  const rsiColor = v => v==null?'#94a3b8':v>57?'#22c55e':v<35?'#f87171':'#e2e8f0';
  const vrColor  = v => v==null?'#94a3b8':v>=150?'#22c55e':v>=100?'#86efac':'#e2e8f0';
  const sigDot   = ok => ok?'<span style="color:#22c55e">●</span>':'<span style="color:#374151">○</span>';

  const rowMap = {{}};
  document.getElementById('tbodyDnaScreen').innerHTML = rows.map((r,i) => {{
    rowMap[r.code] = r;
    return `<tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看詳細DNA分析">
      <td style="color:#94a3b8">${{i+1}}</td>
      <td><b style="color:#fb923c">${{r.code}}</b></td>
      <td style="font-size:11px">${{(r.name||'').substring(0,8)}}</td>
      <td style="font-size:11px;color:${{r.market==='OTC'?'#a78bfa':'#94a3b8'}}">${{r.market}}</td>
      <td style="font-size:10px;color:#64748b;max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{r.sector||'—'}}</td>
      <td style="text-align:center">
        ${{sigDot(r.s1_ok)}}${{sigDot(r.s2_ok)}}${{sigDot(r.s3_ok)}}${{sigDot(r.s4_ok)}}${{sigDot(r.s5_ok)}}${{sigDot(r.s6_ok)}}
        <span style="font-weight:700;color:${{r.bull_signs>=5?'#c2410c':r.bull_signs>=3?'#ca8a04':'#94a3b8'}}">${{r.bull_signs}}</span>
      </td>
      <td style="color:${{diColor(r.mo_di1)}};font-weight:700">${{fv(r.mo_di1,1)}}</td>
      <td style="color:${{rsi4Color(r.mo_rsi4)}};font-weight:700">${{fv(r.mo_rsi4,1)}}</td>
      <td style="color:${{wr50Color(r.wr50)}};font-weight:700">${{fv(r.wr50,1)}}</td>
      <td style="color:${{rsiColor(r.rsi60)}};font-weight:700">${{fv(r.rsi60,1)}}</td>
      <td style="color:${{vrColor(r.wk_vr2)}}">${{fv(r.wk_vr2,0)}}</td>
      <td style="color:${{vrColor(r.mo_vr2)}}">${{fv(r.mo_vr2,0)}}</td>
      <td style="color:${{verdictColor(r.verdict)}};font-size:11px">${{r.verdict}}</td>
    </tr>`;
  }}).join('');
  window._dsRowMap = rowMap;
}}

function showDnaScreenDetail(code) {{
  // Try _dsRowMap first (populated when DNA screen tab is visited),
  // then fall back to DNAFULL.results so other pages can also trigger this modal
  let r = (window._dsRowMap||{{}})[code];
  if (!r && typeof DNA_FULLMKT !== 'undefined') {{
    r = (DNA_FULLMKT.all_results||[]).find(x => x.code === code);
  }}
  if (!r) return;
  const fv  = (v,d=1,fb='—') => v==null?fb:Number(v).toFixed(d);
  const pct = (v,d=1) => v==null?'—':`${{v>=0?'+':''}}${{fv(v,d)}}%`;
  const sig = (ok, label, value, unit='', cond='') => {{
    const col = ok ? '#22c55e' : '#64748b';
    const bg  = ok ? '#052e16' : '#0f172a';
    const dot = ok ? '✅' : '○';
    return `<div style="background:${{bg}};border:1px solid ${{ok?'#16a34a':'#334155'}};border-radius:8px;padding:10px 14px;display:flex;align-items:center;gap:10px">
      <span style="font-size:20px">${{dot}}</span>
      <div>
        <div style="color:${{col}};font-weight:700;font-size:13px">${{label}}</div>
        <div style="font-size:12px;color:#94a3b8">${{value!=null?fv(value,2)+unit:'無數據'}} ${{cond?'<span style="color:#64748b">'+cond+'</span>':''}}</div>
      </div>
    </div>`;
  }};

  document.getElementById('dsDetailHeader').innerHTML =
    `<div>
       ${{r.code}} ${{r.name}} <span style="font-size:13px;color:#94a3b8;font-weight:400">[${{r.market}}] ${{r.sector||''}}</span>
       <span style="margin-left:10px;font-size:15px;font-weight:900;color:${{r.bull_signs>=5?'#c2410c':r.bull_signs>=3?'#ca8a04':'#94a3b8'}}">${{r.verdict}}</span>
     </div>`;

  document.getElementById('dsDetailBody').innerHTML = `
    <!-- 6 Signal scorecard -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-bottom:16px">
      ${{sig(r.s1_ok, '① 月 +DI(1) 方向強度', r.mo_di1,  '', '> 50 多方主導')}}
      ${{sig(r.s2_ok, '② 月 RSI(4) 超強動能',  r.mo_rsi4, '', '> 77 強勢區')}}
      ${{sig(r.s3_ok, '③ 日 W%R(50) 動能延伸', r.wr50,    '', '< 20 強勢進場')}}
      ${{sig(r.s4_ok, '④ 日 RSI(60) 中期多頭', r.rsi60,   '', '> 57 確認多頭')}}
      ${{sig(r.s5_ok, '⑤ 週 VR(2) 量能多頭',   r.wk_vr2,  '', '≥ 150 多方爆量')}}
      ${{sig(r.s6_ok, '⑥ 月 VR(2) 月量多頭',   r.mo_vr2,  '', '≥ 150 月線爆量')}}
    </div>
    <!-- Technical snapshot -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:14px">
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">收盤價</div>
        <div style="font-size:18px;font-weight:700;color:#e2e8f0">${{r.close!=null?fv(r.close,2):'—'}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">月+DI(1)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.mo_di1||0)>50?'#22c55e':'#94a3b8'}}">${{fv(r.mo_di1,1)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">月RSI(4)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.mo_rsi4||0)>77?'#22c55e':'#94a3b8'}}">${{fv(r.mo_rsi4,1)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">日W%R(50)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.wr50||100)<20?'#22c55e':(r.wr50||0)>80?'#f87171':'#94a3b8'}}">${{fv(r.wr50,1)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">日RSI(60)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.rsi60||0)>57?'#22c55e':'#94a3b8'}}">${{fv(r.rsi60,1)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">週VR(2)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.wk_vr2||0)>=150?'#22c55e':'#94a3b8'}}">${{fv(r.wk_vr2,0)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">月VR(2)</div>
        <div style="font-size:18px;font-weight:700;color:${{(r.mo_vr2||0)>=150?'#22c55e':'#94a3b8'}}">${{fv(r.mo_vr2,0)}}</div>
      </div>
      <div style="background:#0f172a;border-radius:6px;padding:8px 12px;text-align:center">
        <div style="font-size:11px;color:#94a3b8">訊號 / 6</div>
        <div style="font-size:24px;font-weight:900;color:${{r.bull_signs>=5?'#c2410c':r.bull_signs>=3?'#ca8a04':'#94a3b8'}}">${{r.bull_signs}}<span style="font-size:14px;color:#64748b">/6</span></div>
      </div>
    </div>
    <!-- ECharts K-line chart -->
    <div style="margin-bottom:12px">
      <div style="font-size:12px;color:#64748b;margin-bottom:6px">📊 K線圖 + W%R(50) + RSI(60) + 月+DI(1) + 月RSI(4)</div>
      <div id="dsChart" style="width:100%;height:440px;background:#0f172a;border-radius:8px"></div>
    </div>
    <!-- Fundamental reference -->
    ${{(r.pe||r.eps_q1||r.rev_yoy)?`<div style="background:#0f172a;border-radius:6px;padding:10px 14px;font-size:12px;color:#94a3b8">
      <b style="color:#e2e8f0">基本面參考：</b>
      ${{r.pe ?'P/E='+fv(r.pe,1)+' ':''}}${{r.pb ?'P/B='+fv(r.pb,2)+' ':''}}
      ${{r.yield?'殖利率='+fv(r.yield,1)+'% ':''}}${{r.eps_q1?'Q1 EPS='+fv(r.eps_q1,2)+'元 ':''}}
      ${{r.rev_yoy!=null?(r.rev_yoy>=0?'營收YoY+':'營收YoY')+fv(r.rev_yoy,1)+'%':''}}
    </div>`:''}}`;

  document.getElementById('dsModal').style.display = 'block';
  renderDnaChart(code);
}}

var _smPromise = null;
function loadSeriesMap() {{
  if (_smPromise) return _smPromise;
  _smPromise = fetch('series_map.json').then(r=>r.json()).catch(()=>({{}}));
  return _smPromise;
}}

function renderDnaChart(code) {{
  const el = document.getElementById('dsChart');
  if (!el || typeof echarts === 'undefined') return;
  if (window._dsEChart) {{ try {{ window._dsEChart.dispose(); }} catch(e){{}} window._dsEChart = null; }}
  el.innerHTML = '<div style="color:#64748b;text-align:center;padding:60px 20px;font-size:13px">⏳ 載入圖表資料中...</div>';
  loadSeriesMap().then(sm => {{
    const s = sm[code];
    el.innerHTML = '';
    if (!s || !s.d || s.d.length === 0) {{
      el.innerHTML = '<div style="color:#64748b;text-align:center;padding:60px 20px;font-size:13px">此股票無K線序列數據<br><span style="font-size:11px">（僅3訊號以上股票儲存圖表數據）</span></div>';
      return;
    }}
    const chart = echarts.init(el, null, {{renderer:'canvas'}});
    window._dsEChart = chart;
  const dates   = s.d.map(x=>x[0]);
  const candles = s.d.map(x=>[x[1],x[2],x[3],x[4]]);
  const wrVals  = (s.wr    ||[]).map(x=>x[1]);
  const wrDts   = (s.wr    ||[]).map(x=>x[0]);
  const rsiVals = (s.rsi60 ||[]).map(x=>x[1]);
  const rsiDts  = (s.rsi60 ||[]).map(x=>x[0]);
  const diVals  = (s.m_di  ||[]).map(x=>x[1]);
  const diDts   = (s.m_di  ||[]).map(x=>x[0]);
  const r4Vals  = (s.m_rsi4||[]).map(x=>x[1]);
  const r4Dts   = (s.m_rsi4||[]).map(x=>x[0]);
  const hasMo   = diVals.length > 0;
  const ax = {{axisLine:{{lineStyle:{{color:'#334155'}}}},axisLabel:{{color:'#64748b',fontSize:10}},splitLine:{{lineStyle:{{color:'#1e293b'}}}}}};
  const grids  = hasMo
    ? [{{left:55,right:12,top:24,height:'40%'}},{{left:55,right:12,top:'49%',height:'11%'}},{{left:55,right:12,top:'63%',height:'11%'}},{{left:55,right:12,top:'77%',height:'11%'}},{{left:55,right:12,top:'91%',height:'7%'}}]
    : [{{left:55,right:12,top:24,height:'56%'}},{{left:55,right:12,top:'64%',height:'15%'}},{{left:55,right:12,top:'82%',height:'15%'}}];
  const xAxes = hasMo
    ? [{{type:'category',data:dates, gridIndex:0,...ax,axisLabel:{{show:false}}}},{{type:'category',data:wrDts,gridIndex:1,...ax,axisLabel:{{show:false}}}},{{type:'category',data:rsiDts,gridIndex:2,...ax,axisLabel:{{show:false}}}},{{type:'category',data:diDts,gridIndex:3,...ax,axisLabel:{{show:false}}}},{{type:'category',data:r4Dts,gridIndex:4,...ax,axisLabel:{{color:'#64748b',fontSize:9}}}}]
    : [{{type:'category',data:dates,gridIndex:0,...ax,axisLabel:{{show:false}}}},{{type:'category',data:wrDts,gridIndex:1,...ax,axisLabel:{{show:false}}}},{{type:'category',data:rsiDts,gridIndex:2,...ax,axisLabel:{{color:'#64748b',fontSize:9}}}}];
  const yAxes = hasMo
    ? [{{gridIndex:0,scale:true,...ax}},{{gridIndex:1,min:-100,max:0,...ax}},{{gridIndex:2,min:0,max:100,...ax}},{{gridIndex:3,min:0,...ax}},{{gridIndex:4,min:0,max:100,...ax}}]
    : [{{gridIndex:0,scale:true,...ax}},{{gridIndex:1,min:-100,max:0,...ax}},{{gridIndex:2,min:0,max:100,...ax}}];
  const ml = (yv,col,lbl) => ({{silent:true,lineStyle:{{color:col,type:'dashed',width:1}},data:[{{yAxis:yv,label:{{formatter:String(lbl),color:col,fontSize:9}}}}]}});
  chart.setOption({{
    animation:false, backgroundColor:'#0f172a',
    tooltip:{{trigger:'axis',axisPointer:{{type:'cross'}},backgroundColor:'#1e293b',borderColor:'#334155',textStyle:{{color:'#e2e8f0',fontSize:11}}}},
    grid:grids, xAxis:xAxes, yAxis:yAxes,
    series:[
      {{name:'K線',type:'candlestick',xAxisIndex:0,yAxisIndex:0,data:candles,itemStyle:{{color:'#ef4444',color0:'#22c55e',borderColor:'#ef4444',borderColor0:'#22c55e'}}}},
      {{name:'W%R(50)',type:'line',xAxisIndex:1,yAxisIndex:1,data:wrVals,lineStyle:{{color:'#a78bfa',width:1.5}},symbol:'none',markLine:ml(-20,'#22c55e','-20')}},
      {{name:'RSI(60)',type:'line',xAxisIndex:2,yAxisIndex:2,data:rsiVals,lineStyle:{{color:'#f59e0b',width:1.5}},symbol:'none',markLine:ml(57,'#22c55e','57')}},
      ...(hasMo?[
        {{name:'月+DI(1)',type:'line',xAxisIndex:3,yAxisIndex:3,data:diVals,lineStyle:{{color:'#38bdf8',width:1.5}},symbol:'none',markLine:ml(50,'#c2410c','50')}},
        {{name:'月RSI(4)',type:'line',xAxisIndex:4,yAxisIndex:4,data:r4Vals,lineStyle:{{color:'#fb923c',width:1.5}},symbol:'none',markLine:ml(77,'#c2410c','77')}},
      ]:[]),
    ],
  }},true);
  }});
}}

// ════════════════════════════════ GRAND UNIFIED ═══════════════════════════
function initGrandUnified() {{
  const G = GRANDDATA;
  const all = G.all_ranked || [];

  const meta = [
    {{label:'🚀 TRIPLE CONFIRMED', count:(G.triple_confirmed||[]).length, bg:'#1e3a5f', color:'#fff'}},
    {{label:'✅ STRONG BUY',       count:(G.strong_buy||[]).length,       bg:'#14532d', color:'#fff'}},
    {{label:'📈 BUY',              count:(G.buy||[]).length,              bg:'#1e40af', color:'#fff'}},
    {{label:'⬛ WATCH/HOLD',       count:all.filter(r=>['👀 WATCH','⬛ HOLD'].some(v=>r.final.includes(v.split(' ')[1]))).length, bg:'#374151', color:'#fff'}},
  ];
  document.getElementById('grandMetaCards').innerHTML = meta.map(c => `
    <div class="kpi-card" style="background:${{c.bg}};border:none">
      <div class="kpi-label" style="color:${{c.color}}">${{c.label}}</div>
      <div class="kpi-value" style="color:${{c.color}};font-size:24px">${{c.count}}</div>
    </div>`).join('');

  const fv  = (v,d=1) => v==null?'—':Number(v).toFixed(d);
  const pct = v => v==null?'<td>—</td>':`<td style="color:${{v>=0?'#16a34a':'#dc2626'}};font-weight:600">${{v>=0?'+':''}}${{fv(v)}}%</td>`;
  const scoreBar = (v,max=25) => {{
    const pctW = Math.round((v||0)/max*100);
    const col = pctW>=75?'#16a34a':pctW>=50?'#2563eb':'#94a3b8';
    return `<td><div style="display:flex;align-items:center;gap:4px">
      <div style="width:40px;height:6px;background:#f1f5f9;border-radius:3px">
        <div style="width:${{pctW}}%;height:100%;background:${{col}};border-radius:3px"></div>
      </div><span style="font-size:11px">${{fv(v)}}</span></div></td>`;
  }};
  const verdictBadge = v => {{
    const bg = v.includes('TRIPLE')?'#7c2d12':v.includes('STRONG')?'#14532d':v.includes('BUY')?'#1e40af':v.includes('WATCH')?'#374151':'#6b7280';
    return `<td><span style="background:${{bg}};color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600">${{v}}</span></td>`;
  }};

  const topStocks = [...(G.triple_confirmed||[]), ...(G.strong_buy||[])];
  document.getElementById('tbodyGrandTop').innerHTML = topStocks.map((r,i) => `
    <tr>
      <td style="font-weight:700;color:#c2410c">${{i+1}}</td>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name.split(' ')[0]}}</td>
      <td>¥${{fv(r.close||0)}}</td>
      <td style="font-weight:700;font-size:15px;color:${{r.grand>=70?'#c2410c':r.grand>=60?'#1e40af':'#374151'}}">${{fv(r.grand)}}</td>
      ${{scoreBar(r.fund_pts)}}
      ${{scoreBar(r.tech_pts)}}
      ${{scoreBar(r.val_pts)}}
      ${{scoreBar(r.mom_pts)}}
      <td>${{fv(r.pe)}}x</td>
      <td style="color:${{(r.div_yield||0)>=4.5?'#16a34a':'#374151'}}">${{fv(r.div_yield)}}%</td>
      ${{pct(r.pct_prior)}}
      <td>${{r.bull_signs!=null?r.bull_signs+'/6':'—'}}</td>
      ${{verdictBadge(r.final)}}
    </tr>`).join('');

  document.getElementById('tbodyGrandAll').innerHTML = all.map((r,i) => `
    <tr>
      <td style="color:#94a3b8;font-size:12px">${{i+1}}</td>
      <td><b>${{r.code}}</b></td>
      <td style="font-size:13px">${{r.name.split(' ')[0]}}</td>
      <td style="font-weight:${{r.grand>=65?'700':'400'}};color:${{r.grand>=70?'#c2410c':r.grand>=60?'#1e40af':'#374151'}}">${{fv(r.grand)}}</td>
      <td style="font-size:12px">${{fv(r.fund_pts)}}</td>
      <td style="font-size:12px">${{fv(r.tech_pts)}}</td>
      <td style="font-size:12px">${{fv(r.val_pts)}}</td>
      <td style="font-size:12px">${{fv(r.mom_pts)}}</td>
      <td style="font-size:12px">${{fv(r.pe)}}x</td>
      <td style="font-size:12px;color:${{(r.div_yield||0)>=4.5?'#16a34a':'inherit'}}">${{fv(r.div_yield)}}%</td>
      ${{verdictBadge(r.final)}}
    </tr>`).join('');
}}

// ════════════════════════════════ MONDAY PLAN ════════════════════════════
function initMondayPlan() {{
  const M = MONDAYPLAN;
  const s = M.summary || {{}};
  const cats = M.categories || {{}};

  // KPIs
  document.getElementById('mpKpis').innerHTML = [
    {{label:'TRIPLE持倉', val:s.triple_count||0, color:'#c2410c', sub:'最高優先'}},
    {{label:'近TRIPLE', val:s.near_triple||0, color:'#1d4ed8', sub:'≤5pts缺口'}},
    {{label:'DNA 5/6', val:s.dna_56_count||0, color:'#7c3aed', sub:'缺1信號'}},
    {{label:'品質逢低', val:s.quality_dips||0, color:'#15803d', sub:'A+品質近MA'}},
    {{label:'營收催化', val:s.rev_catalysts||0, color:'#0891b2', sub:'6月10日'}},
    {{label:'行業龍頭', val:s.sector_leaders||0, color:'#374151', sub:'各產業最佳'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:24px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  // Checklist
  const typeStyle = t =>
    t==='critical'?'background:#fee2e2;border-left:3px solid #dc2626':
    t==='data_update'?'background:#eff6ff;border-left:3px solid #3b82f6':
    t==='execution'?'background:#f0fdf4;border-left:3px solid #22c55e':
    t==='alert'?'background:#fffbeb;border-left:3px solid #f59e0b':
    'background:#f8fafc;border-left:3px solid #94a3b8';
  document.getElementById('mpChecklist').innerHTML =
    `<div style="display:grid;gap:6px">` +
    (M.checklist||[]).map(c=>`
      <div style="${{typeStyle(c.type)}};border-radius:0 6px 6px 0;padding:8px 14px;display:flex;align-items:flex-start;gap:12px">
        <span style="font-weight:700;font-size:13px;white-space:nowrap;color:#374151;min-width:70px">${{c.time}}</span>
        <div>
          <div style="font-weight:600;font-size:13px">${{c.task}}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px">${{c.why}}</div>
        </div>
      </div>`).join('') + `</div>`;

  // Category blocks
  const fv = (v,d=1,s='') => v==null?'—':Number(v).toFixed(d)+s;
  const catDefs = [
    {{key:'triple_confirmed', label:'🚀 TRIPLE CONFIRMED — 持倉追蹤', bg:'#7f1d1d', color:'#fff'}},
    {{key:'near_triple',      label:'⚡ 近TRIPLE升評 — 觀察觸發',    bg:'#1e3a5f', color:'#fff'}},
    {{key:'dna_56',           label:'🧬 DNA 5/6 — 缺1信號突破股',    bg:'#4c1d95', color:'#fff'}},
    {{key:'quality_dips',     label:'💎 A+品質逢低 — 週一入場機會',   bg:'#14532d', color:'#fff'}},
    {{key:'rev_accel',        label:'📈 6月10日營收催化劑',           bg:'#0c4a6e', color:'#fff'}},
    {{key:'sector_leaders',   label:'🏆 行業龍頭 — 各產業最佳',       bg:'#1c1917', color:'#fff'}},
  ];

  document.getElementById('mpCategories').innerHTML = catDefs.map(cd => {{
    const stocks = cats[cd.key] || [];
    if (!stocks.length) return '';
    return `<div class="card" style="margin-bottom:12px">
      <div class="card-pad" style="background:${{cd.bg}};color:${{cd.color}};border-radius:10px 10px 0 0">
        <div style="font-weight:700;font-size:14px">${{cd.label}}
          <span style="float:right;opacity:.7;font-size:13px">${{stocks.length}} 股</span></div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;padding:12px">
        ${{stocks.map(s=>`
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:10px 12px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <b style="font-size:15px">${{s.code}}</b>
              <span style="font-size:12px;color:#64748b">${{s.name}}</span>
              <span style="margin-left:auto;font-size:13px;font-weight:700;color:${{(s.grand||0)>=70?'#c2410c':(s.grand||0)>=60?'#1d4ed8':'#374151'}}">${{fv(s.grand)}}</span>
            </div>
            <div style="font-size:12px;color:#374151;margin-bottom:4px">${{s.action||'—'}}</div>
            ${{s.watch_level?`<div style="font-size:11px;color:#94a3b8">支撐: ${{s.watch_level}}</div>`:''}}
            ${{s.missing_signal?`<div style="font-size:11px;color:#7c3aed">缺: ${{s.missing_signal}}</div>`:''}}
            ${{s.pct_vs_ma!=null?`<div style="font-size:11px;color:${{s.pct_vs_ma>=0?'#16a34a':'#dc2626'}}">vs MA: ${{s.pct_vs_ma>=0?'+':''}}${{fv(s.pct_vs_ma,1)}}%</div>`:''}}
            ${{s.apr_yoy!=null?`<div style="font-size:11px;color:#16a34a">4月YoY: +${{fv(s.apr_yoy,0)}}%</div>`:''}}
          </div>`).join('')}}
      </div>
    </div>`;
  }}).join('');
}}

// ═══════════════════════════════ DIVIDEND INCOME ══════════════════════════
function initDivIncome() {{
  const D   = DIVINCOME;
  const ps  = D.portfolio_summary || {{}};
  const pos = D.positions || [];
  const pk  = D.income_picks || [];
  const fv  = (v,d=1,s='') => v==null?'—':Number(v).toFixed(d)+s;

  document.getElementById('diKpis').innerHTML = [
    {{label:'年股息總收入', val:'$'+(ps.total_annual_div_income||0).toLocaleString(), color:'#15803d', sub:'TWD 100萬組合'}},
    {{label:'月均股息',    val:'$'+(ps.monthly_income_est||0).toLocaleString(),       color:'#0891b2', sub:'月均現金流'}},
    {{label:'投資部位殖利率',val:fv(ps.portfolio_yield_pct,2,'%'),                   color:'#7c3aed', sub:'含現金為1.46%'}},
    {{label:'配息股票數',  val:ps.n_dividend_stocks||0,                               color:'#374151', sub:'有殖利率股'}},
    {{label:'7月除息',    val:'$'+((ps.monthly_schedule||{{}})['2026-07']||0).toLocaleString(), color:'#c2410c', sub:'主要除息月'}},
    {{label:'高殖利率精選',val:pk.length,                                             color:'#d97706', sub:'殖利率>4%+EQ≥6'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:${{typeof k.val==='number'?'22':'16'}}px;font-weight:700">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  const susColor = s =>
    s==='非常穩健'?'#15803d':s==='穩健'?'#0891b2':s==='普通'?'#374151':'#d97706';
  const tierColor = t =>
    t==='超高殖利率'?'#c2410c':t==='高殖利率'?'#d97706':t==='中等殖利率'?'#0891b2':'#94a3b8';

  document.getElementById('diBody').innerHTML = pos.map(p => `<tr>
    <td><b>${{p.code}}</b></td>
    <td>${{p.name}}</td>
    <td style="text-align:right;font-weight:700;color:${{(p.div_yield_pct||0)>=4?'#c2410c':(p.div_yield_pct||0)>=3?'#d97706':'#374151'}}">${{fv(p.div_yield_pct,2,'%')}}</td>
    <td style="text-align:right">${{p.div_per_share?'$'+fv(p.div_per_share,2):'—'}}</td>
    <td style="text-align:right;font-weight:700;color:#15803d">${{p.total_div_income?'$'+p.total_div_income.toLocaleString():'—'}}</td>
    <td style="text-align:right;color:#64748b">${{fv(p.alloc_pct,2)}}%</td>
    <td><span style="font-size:12px;color:#374151">${{p.ex_month_est||'—'}}</span></td>
    <td><span style="font-size:12px;font-weight:600;color:${{susColor(p.div_sustainability)}}">${{p.div_sustainability||'—'}}</span></td>
    <td><span style="font-size:11px;padding:2px 5px;border-radius:4px;background:#f1f5f9;color:${{tierColor(p.yield_tier)}}">${{p.yield_tier||'—'}}</span></td>
  </tr>`).join('');

  const sched = ps.monthly_schedule || {{}};
  const maxAmt = Math.max(...Object.values(sched), 1);
  document.getElementById('diSchedule').innerHTML = Object.entries(sched)
    .sort((a,b)=>a[0].localeCompare(b[0]))
    .map(([mo,amt]) => `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
        <div style="width:70px;font-size:13px;font-weight:600;color:#374151">${{mo}}</div>
        <div style="flex:1;background:#f1f5f9;border-radius:4px;height:18px">
          <div style="width:${{(amt/maxAmt*100).toFixed(0)}}%;height:18px;background:#15803d;border-radius:4px;
               display:flex;align-items:center;padding-left:6px">
            <span style="font-size:11px;color:#fff;font-weight:700;white-space:nowrap">
              ${{amt.toLocaleString()}}</span>
          </div>
        </div>
      </div>`).join('');

  document.getElementById('diPicks').innerHTML = pk.slice(0,6).map(p=>
    `<div style="display:flex;justify-content:space-between;padding:6px 0;
        border-bottom:1px solid #f1f5f9;font-size:13px">
      <span><b>${{p.code}}</b> ${{p.name}}</span>
      <span style="font-weight:700;color:#c2410c">${{fv(p.div_yield_pct,2,'%')}}</span>
    </div>`).join('');
}}

// ═══════════════════════════════ SCENARIO ANALYSIS ════════════════════════
function initScenario() {{
  const S   = SCENARIO;
  const rm  = S.risk_metrics || {{}};
  const sc  = S.scenarios    || [];
  const st  = S.stress_tests || [];
  const ps  = S.position_scenarios || [];
  const fv  = (v,d=1,s='',plus=false) => {{
    if (v==null) return '—';
    const n = Number(v).toFixed(d);
    return (plus&&v>=0?'+':'')+n+s;
  }};
  const retColor = v => (v==null)?'#94a3b8':(v>=0?'#16a34a':'#dc2626');

  document.getElementById('scKpis').innerHTML = [
    {{label:'期望值(含現金)', val:fv(rm.expected_value_with_cash,2,'%',true), color:retColor(rm.expected_value_with_cash), sub:'25%牛+50%基+25%熊'}},
    {{label:'持倉期望值',    val:fv(rm.expected_value_invested,2,'%',true),  color:retColor(rm.expected_value_invested),  sub:'60日加權平均'}},
    {{label:'Sharpe代理',   val:fv(rm.sharpe_proxy,2),                      color:'#7c3aed', sub:'報酬/風險比值'}},
    {{label:'VaR (5%)',     val:fv(rm.var_5pct,2,'%',true),                 color:'#dc2626', sub:'最壞5%情況'}},
    {{label:'最大回撤估計',  val:fv(rm.max_drawdown_estimate,2,'%',true),    color:'#dc2626', sub:'相關性飆升情境'}},
    {{label:'現金緩衝',      val:'20%',                                      color:'#0891b2', sub:'組合保護層'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:20px;font-weight:700">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  const scColors = ['#15803d','#0891b2','#dc2626'];
  document.getElementById('scScenarios').innerHTML = `<div style="display:grid;gap:10px">` +
    sc.map((s,i) => {{
      const barW = Math.max(2, Math.min(100, Math.abs(s.port_return) * 5));
      return `<div style="background:#f8fafc;border-radius:8px;padding:12px 14px;
          border-left:4px solid ${{scColors[i]}}">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <div style="font-weight:700;font-size:14px">${{s.name}}</div>
            <div style="font-size:12px;color:#64748b;margin-top:2px">${{s.description}}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:20px;font-weight:800;color:${{retColor(s.port_return)}}">${{fv(s.port_return,2,'%',true)}}</div>
            <div style="font-size:11px;color:#94a3b8">${{s.probability}}</div>
          </div>
        </div>
        <div style="margin-top:8px;background:#e2e8f0;border-radius:4px;height:6px">
          <div style="width:${{barW}}%;height:6px;background:${{scColors[i]}};border-radius:4px"></div>
        </div>
        <div style="font-size:11px;color:#64748b;margin-top:6px">
          ${{(s.triggers||[]).slice(0,3).map(t=>`<span style="margin-right:8px">• ${{t}}</span>`).join('')}}
        </div>
      </div>`;
    }}).join('') + `</div>`;

  document.getElementById('scStress').innerHTML = `<div style="display:grid;gap:8px">` +
    st.map(s => {{
      const isNeg = s.port_impact < 0;
      return `<div style="background:#f8fafc;border-radius:8px;padding:10px 14px;
          border-left:3px solid ${{isNeg?'#dc2626':'#16a34a'}}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div style="flex:1">
            <div style="font-weight:700;font-size:13px">${{s.name}}</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px">${{s.mitigation}}</div>
          </div>
          <div style="text-align:right;margin-left:12px;flex-shrink:0">
            <div style="font-size:18px;font-weight:800;color:#dc2626">${{fv(s.port_impact,2,'%',true)}}</div>
            <div style="font-size:11px;color:#94a3b8">${{s.probability}}</div>
          </div>
        </div>
      </div>`;
    }}).join('') + `</div>`;

  const top20 = ps.slice(0,20);
  document.getElementById('scBody').innerHTML = top20.map(p => `<tr>
    <td><b>${{p.code}}</b></td>
    <td>${{p.name}}</td>
    <td style="font-size:12px;color:#64748b">${{p.sector}}</td>
    <td style="text-align:right;font-weight:700">${{fv(p.alloc,2)}}%</td>
    <td style="text-align:right;font-weight:700;color:#16a34a">${{fv(p.bull_ret,1,'%',true)}}</td>
    <td style="text-align:right;font-weight:700;color:#0891b2">${{fv(p.base_ret,1,'%',true)}}</td>
    <td style="text-align:right;font-weight:700;color:#dc2626">${{fv(p.bear_ret,1,'%',true)}}</td>
    <td style="text-align:right;color:${{p.sector==='金融保險'?'#dc2626':'#94a3b8'}};font-weight:${{p.sector==='金融保險'?'700':'400'}}">${{fv(p.stress_fin,1,'%',true)}}</td>
    <td style="text-align:right;color:#dc2626">${{fv(p.max_loss_pct,1,'%',true)}}</td>
    <td><span style="font-size:11px;padding:2px 6px;border-radius:4px;
        background:${{p.final.includes('TRIPLE')?'#fef2f2':p.final.includes('BUY')?'#f0fdf4':'#f8fafc'}};
        color:${{p.final.includes('TRIPLE')?'#c2410c':p.final.includes('BUY')?'#16a34a':'#64748b'}}">${{p.final}}</span></td>
  </tr>`).join('');
}}

// ═══════════════════════════════ PREMARKET CHECKLIST ══════════════════════
function initPremarket() {{
  const PM  = PREMARKET;
  const cl  = PM.checklist || [];
  const sm  = PM.summary || {{}};
  const fv  = (v,d=1,s='') => v==null?'—':Number(v).toFixed(d)+s;

  document.getElementById('pmKpis').innerHTML = [
    {{label:'持倉總數',   val:sm.total_positions||0, color:'#374151', sub:'36個建議倉位'}},
    {{label:'P1 TRIPLE',  val:sm.p1_triple||0,        color:'#c2410c', sub:'最高優先'}},
    {{label:'P2 近升評',  val:sm.p2_near||0,          color:'#d97706', sub:'距TRIPLE≤5分'}},
    {{label:'P3 DNA5/6',  val:sm.p3_dna56||0,         color:'#7c3aed', sub:'缺1個信號'}},
    {{label:'P4 BUY建倉', val:sm.p4_buy||0,           color:'#0891b2', sub:'≥55分'}},
    {{label:'P5 觀察',    val:sm.p5_watch||0,          color:'#94a3b8', sub:'<55分'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:22px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  const pGroups = [
    {{p:1,label:'🔴 P1 — TRIPLE CONFIRMED 持倉追蹤',  bg:'#7f1d1d', color:'#fff'}},
    {{p:2,label:'🟠 P2 — 近升評股 觀察觸發',          bg:'#1e3a5f', color:'#fff'}},
    {{p:3,label:'🟡 P3 — DNA 5/6 缺1信號',            bg:'#4c1d95', color:'#fff'}},
    {{p:4,label:'🟢 P4 — BUY 條件建倉',               bg:'#14532d', color:'#fff'}},
    {{p:5,label:'⚪ P5 — 觀察倉位',                   bg:'#334155', color:'#fff'}},
  ];

  document.getElementById('pmGroups').innerHTML = pGroups.map(pg => {{
    const group = cl.filter(c => c.priority === pg.p);
    if (!group.length) return '';
    return `<div class="card" style="margin-bottom:14px">
      <div class="card-pad" style="background:${{pg.bg}};color:${{pg.color}};border-radius:10px 10px 0 0;padding:10px 16px">
        <span style="font-weight:700;font-size:14px">${{pg.label}}</span>
        <span style="float:right;font-size:13px;opacity:.8">${{group.length}} 股</span>
      </div>
      <div style="overflow-x:auto"><table class="data-table">
        <thead><tr style="background:#f8fafc">
          <th>代號</th><th>名稱</th><th>Grand</th><th>DNA</th><th>EQ</th>
          <th style="text-align:right">收盤</th><th style="text-align:right">MA30</th>
          <th style="text-align:right">止損</th><th style="text-align:right">緩衝%</th>
          <th>入場策略</th>
          <th style="text-align:right">入場價</th><th style="text-align:right">TP1</th>
          <th style="text-align:right">建議%</th><th>DNA監控</th>
        </tr></thead>
        <tbody>
        ${{group.map(c => {{
          const stopBuf = c.stop_buffer_pct != null
            ? `<span style="color:${{c.stop_buffer_pct>5?'#16a34a':'#f59e0b'}};font-weight:700">+${{fv(c.stop_buffer_pct,1)}}%</span>`
            : '—';
          const dnaNote = c.s3_note
            ? `<span style="color:#f59e0b;font-size:11px">${{c.s3_note}}</span>`
            : (c.missing_dna&&c.missing_dna.length
              ? `<span style="color:#7c3aed;font-size:11px">缺:${{c.missing_dna.join(',')}}</span>`
              : '<span style="color:#16a34a;font-size:11px">✓ 6/6</span>');
          const upgradeNote = (c.pts_to_upgrade!=null&&c.pts_to_upgrade<5)
            ? `<div style="font-size:11px;color:#0369a1">↑距下一評級 ${{fv(c.pts_to_upgrade,1)}}分</div>`
            : '';
          return `<tr>
            <td><b>${{c.code}}</b></td>
            <td style="white-space:nowrap">${{c.name}}</td>
            <td style="text-align:right;font-weight:700;color:${{c.grand>=70?'#c2410c':c.grand>=60?'#1d4ed8':'#374151'}}">${{fv(c.grand,1)}}</td>
            <td style="text-align:center">${{c.bull_signs}}/6</td>
            <td style="text-align:center;color:${{c.eq_score>=9?'#15803d':c.eq_score>=7?'#0891b2':'#94a3b8'}}">${{c.eq_score||'—'}}</td>
            <td style="text-align:right">${{fv(c.close,1)}}</td>
            <td style="text-align:right;color:#64748b">${{fv(c.ma30,1)}}</td>
            <td style="text-align:right;color:#dc2626">${{fv(c.stop,1)}}</td>
            <td style="text-align:right">${{stopBuf}}</td>
            <td>
              <span style="font-size:12px;font-weight:600;color:#374151">${{c.entry_action}}</span>
              <div style="font-size:11px;color:#64748b">${{c.entry_note}}</div>
              ${{upgradeNote}}
            </td>
            <td style="text-align:right;font-weight:700;color:#0369a1">${{fv(c.entry_level,1)}}</td>
            <td style="text-align:right;color:#16a34a">${{fv(c.tp1,1)}}</td>
            <td style="text-align:right;font-weight:700">${{fv(c.alloc_pct,2)}}%</td>
            <td>${{dnaNote}}</td>
          </tr>`;
        }}).join('')}}
        </tbody>
      </table></div>
    </div>`;
  }}).join('');
}}

// ═══════════════════════════════ SECTOR ROTATION ══════════════════════════
function initSecRotation() {{
  const R   = SECROTATION;
  const secs= R.sectors || [];
  const sm  = R.summary || {{}};
  const fv  = (v,d=1,s='') => v==null?'—':Number(v).toFixed(d)+s;

  const phaseColor = p =>
    p==='領漲'?'#15803d':p==='改善中'?'#0891b2':p==='中性'?'#374151':
    p==='落後'?'#d97706':'#dc2626';
  const trendColor = t =>
    t.includes('升溫')?'#16a34a':t.includes('降溫')?'#dc2626':'#64748b';

  document.getElementById('srKpis').innerHTML = [
    {{label:'板塊總數',  val:sm.n_sectors||0,  color:'#374151', sub:'已分析板塊'}},
    {{label:'增持板塊',  val:sm.n_buy||0,       color:'#15803d', sub:'BUY訊號'}},
    {{label:'中性板塊',  val:sm.n_neutral||0,   color:'#0891b2', sub:'WATCH/NEUTRAL'}},
    {{label:'落後板塊',  val:sm.n_reduce||0,    color:'#d97706', sub:'HOLD/REDUCE'}},
    {{label:'領先板塊',  val:secs[0]?.sector||'—', color:'#c2410c', sub:'最高旋轉分'}},
    {{label:'落後板塊',  val:secs[secs.length-1]?.sector||'—', color:'#94a3b8', sub:'最低旋轉分'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:${{typeof k.val==='number'?'24':'16'}}px;font-weight:700">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  document.getElementById('srMatrix').innerHTML = secs.map(s => {{
    const m   = s.medians || {{}};
    const bar = Math.round(s.rotation_score / 100 * 100);
    const topStocks = (s.stocks||[]).slice(0,4);
    return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;
              border-left:4px solid ${{phaseColor(s.phase)}}">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <div>
          <span style="font-weight:700;font-size:15px">${{s.sector}}</span>
          <span style="font-size:12px;color:#64748b;margin-left:6px">${{s.n_stocks}}股</span>
        </div>
        <span style="font-weight:700;font-size:16px;color:${{phaseColor(s.phase)}}">${{s.phase}}</span>
      </div>
      <div style="background:#f1f5f9;border-radius:4px;height:6px;margin-bottom:10px">
        <div style="width:${{bar}}%;height:6px;background:${{phaseColor(s.phase)}};border-radius:4px;
             transition:width .4s"></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;font-size:12px;margin-bottom:8px">
        <div><span style="color:#94a3b8">RS20:</span> <b style="color:${{(m.rs_20||0)>=0?'#16a34a':'#dc2626'}}">${{fv(m.rs_20)}}</b></div>
        <div><span style="color:#94a3b8">RS60:</span> <b style="color:${{(m.rs_60||0)>=0?'#16a34a':'#dc2626'}}">${{fv(m.rs_60)}}</b></div>
        <div><span style="color:#94a3b8">RS120:</span> <b style="color:${{(m.rs_120||0)>=0?'#16a34a':'#dc2626'}}">${{fv(m.rs_120)}}</b></div>
        <div><span style="color:#94a3b8">4月YoY:</span> <b>${{fv(m.apr_yoy)}}%</b></div>
        <div><span style="color:#94a3b8">vs MA:</span> <b>${{fv(m.pct_vs_ma30)}}%</b></div>
        <div><span style="color:#94a3b8">趨勢:</span> <b style="color:${{trendColor(s.rs_trend||'')}}">${{s.rs_trend||'—'}}</b></div>
      </div>
      <div style="font-size:12px;font-weight:700;color:${{s.signal_color||'#64748b'}};margin-bottom:6px">
        ${{s.rotation_signal}}</div>
      <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px">
        ${{(s.tags||[]).map(t=>`<span style="font-size:11px;padding:2px 6px;background:#f1f5f9;border-radius:4px;color:#374151">${{t}}</span>`).join('')}}
      </div>
      <div style="font-size:11px;color:#64748b">
        ${{topStocks.map(st=>`<span style="margin-right:6px">${{st.code}}(RS${{fv(st.rs_60,0)}})</span>`).join('')}}
      </div>
    </div>`;
  }}).join('');

  document.getElementById('srTrades').innerHTML = (R.rotation_trades||[]).length === 0
    ? '<p style="color:#94a3b8;font-size:13px">暫無明確輪動交易建議（各板塊均在改善中）</p>'
    : `<div style="display:grid;gap:8px">` +
      (R.rotation_trades||[]).slice(0,6).map(t=>
        `<div style="padding:10px 14px;background:#f8fafc;border-radius:8px;
              border-left:3px solid ${{t.confidence==='高'?'#c2410c':'#0891b2'}}">
          <span style="font-size:13px;font-weight:700;color:#374151">
            ${{t.rotate_from}} → ${{t.rotate_to}}</span>
          <span style="font-size:11px;margin-left:8px;padding:2px 6px;border-radius:4px;
            background:${{t.confidence==='高'?'#fef2f2':'#eff6ff'}};
            color:${{t.confidence==='高'?'#c2410c':'#1d4ed8'}}">${{t.confidence}}信心</span>
          <div style="font-size:12px;color:#64748b;margin-top:4px">${{t.rationale}}</div>
        </div>`).join('') + `</div>`;
}}

// ═══════════════════════════════ POSITION SIZING ══════════════════════════
function initPosSize() {{
  const P   = POSSIZE;
  const ps  = P.portfolio_summary || {{}};
  const pos = P.positions || [];
  const inv = pos.filter(p => (p.alloc_pct_norm||0) >= 0.5);
  const fv  = (v,d=1,s='') => v==null?'—':Number(v).toFixed(d)+s;

  document.getElementById('psKpis').innerHTML = [
    {{label:'持倉股數',      val:ps.n_positions||0,          color:'#374151', sub:'建議倉位'}},
    {{label:'核心持倉',      val:ps.core_positions||0,       color:'#c2410c', sub:'≥10%分配'}},
    {{label:'主要持倉',      val:ps.major_positions||0,      color:'#1d4ed8', sub:'6-10%分配'}},
    {{label:'衛星持倉',      val:ps.satellite_positions||0,  color:'#7c3aed', sub:'1-6%分配'}},
    {{label:'總投入%',       val:(ps.total_invested_pct||0)+'%', color:'#0891b2', sub:'20%現金'}},
    {{label:'預期60日報酬',  val:(ps.expected_60d_return||0)+'%', color:'#16a34a', sub:'加權平均'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:22px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  const tierColor = t =>
    t==='核心持倉'?'#c2410c':t==='主要持倉'?'#1d4ed8':t==='衛星持倉'?'#7c3aed':'#94a3b8';

  const rows = inv.map(p => {{
    const alloc = p.alloc_pct_norm || 0;
    const bar   = `<div style="display:flex;align-items:center;gap:6px">
      <div style="width:${{Math.round(alloc*6)}}px;height:8px;background:${{tierColor(p.risk_tier)}};border-radius:4px;min-width:4px"></div>
      <b style="color:${{tierColor(p.risk_tier)}}">${{fv(alloc,2)}}%</b></div>`;
    const lots  = p.lots ? `${{p.lots}}張` : '—';
    const twd   = p.actual_twd ? `${{(p.actual_twd/10000).toFixed(1)}}萬` : '—';
    const stop  = p.stop_level ? `${{fv(p.stop_level,1)}} (${{fv(p.stop_pct,1)}}%)` : '—';
    return `<tr>
      <td><b>${{p.code}}</b></td>
      <td>${{p.name.split(' ')[0]}}</td>
      <td style="font-size:12px;color:#64748b">${{p.sector}}</td>
      <td><span style="font-size:11px;padding:2px 6px;border-radius:4px;background:${{
        p.final.includes('TRIPLE')?'#fef2f2':p.final.includes('BUY')?'#f0fdf4':'#f8fafc'
      }};color:${{
        p.final.includes('TRIPLE')?'#c2410c':p.final.includes('BUY')?'#16a34a':'#64748b'
      }}">${{p.final}}</span></td>
      <td>${{bar}}</td>
      <td style="text-align:right">${{twd}}</td>
      <td style="text-align:right">${{lots}}</td>
      <td style="text-align:center"><span style="font-size:11px;color:${{tierColor(p.risk_tier)}};font-weight:700">${{p.risk_tier}}</span></td>
      <td style="text-align:right;color:#64748b;font-size:12px">${{fv(p.kelly_half,1)}}%</td>
      <td style="text-align:right;color:#16a34a;font-size:12px">${{p.win_60d?p.win_60d+'%':'—'}}</td>
      <td style="text-align:right;font-size:12px;color:${{(p.avg_60d||0)>=0?'#16a34a':'#dc2626'}}">${{p.avg_60d!=null?((p.avg_60d>=0?'+':'')+fv(p.avg_60d,1)+'%'):'—'}}</td>
      <td style="text-align:right;font-weight:700;color:${{p.grand>=70?'#c2410c':p.grand>=60?'#1d4ed8':'#374151'}}">${{fv(p.grand,1)}}</td>
      <td style="text-align:center;font-size:12px">${{p.eq_grade||'—'}}</td>
      <td style="font-size:12px;color:#dc2626">${{stop}}</td>
    </tr>`;
  }}).join('');
  document.getElementById('psBody').innerHTML = rows;

  // Sector bars
  const secAlloc = ps.sector_allocation || {{}};
  const secSorted = Object.entries(secAlloc).sort((a,b)=>b[1]-a[1]);
  const maxSec = secSorted[0]?.[1] || 1;
  document.getElementById('psSectors').innerHTML = secSorted.map(([sec,pct])=>
    `<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
      <div style="width:90px;font-size:12px;color:#374151;text-align:right;flex-shrink:0">${{sec}}</div>
      <div style="flex:1;background:#f1f5f9;border-radius:4px;height:14px">
        <div style="width:${{(pct/maxSec*100).toFixed(0)}}%;height:14px;background:#3b82f6;border-radius:4px"></div>
      </div>
      <div style="width:40px;font-size:12px;font-weight:700;color:#1d4ed8">${{fv(pct,1)}}%</div>
    </div>`).join('');

  // Methodology
  const m = P.methodology || {{}};
  document.getElementById('psMethod').innerHTML = Object.entries(m).map(
    ([k,v])=>`<div><b>${{k}}</b>: ${{v}}</div>`).join('');
}}

// ═══════════════════════════════ INSTITUTIONAL FLOWS ══════════════════════
function initInstFlows() {{
  const IF  = INSTFLOWS;
  const tri = IF.triple_flows   || [];
  const hb  = IF.heavy_buy      || [];
  const div = IF.bullish_divergence || [];
  const all = IF.universe_flows || [];
  const sum = IF.summary        || {{}};

  // KPIs
  document.getElementById('ifKpis').innerHTML = [
    ['📅 資料日期', IF.data_date || '—', '#1e293b'],
    ['📈 大量買超', (sum.heavy_buy_count || 0) + ' 支', '#16a34a'],
    ['📉 大量賣超', (sum.heavy_sell_count || 0) + ' 支', '#dc2626'],
    ['🔔 看漲背離', (sum.bullish_divergence || 0) + ' 支', '#7c3aed'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  // TRIPLE flows
  document.getElementById('ifTriple').innerHTML = tri.length ? tri.map(r => {{
    const fc = r.total_net > 0 ? '#16a34a' : '#dc2626';
    const icon = r.total_net > 0 ? '▲' : '▼';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f1f5f9">
      <div>
        <b style="font-size:14px">${{r.code}}</b>
        <span style="font-size:13px;color:#475569;margin-left:4px">${{r.name}}</span>
        <span style="font-size:11px;background:#fef2f2;color:#dc2626;padding:1px 6px;border-radius:4px;margin-left:6px">Grand ${{r.grand}}</span>
      </div>
      <div style="text-align:right">
        <div style="color:${{fc}};font-weight:700">${{icon}} ${{r.inst_signal}}</div>
        <div style="font-size:11px;color:#94a3b8">合計 ${{r.total_net > 0 ? '+' : ''}}${{r.total_net.toLocaleString()}}股</div>
        <div style="font-size:11px;color:#94a3b8">外資 ${{r.foreign_net > 0 ? '+' : ''}}${{r.foreign_net.toLocaleString()}}</div>
      </div>
    </div>`;
  }}).join('') : '<div style="color:#94a3b8;padding:20px;text-align:center">無TRIPLE股票資料</div>';

  // Heavy buy
  document.getElementById('ifHeavyBuy').innerHTML = hb.slice(0,8).map(r => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div>
        <b>${{r.code}}</b> <span style="color:#475569;font-size:12px">${{r.name}}</span>
      </div>
      <div style="text-align:right">
        <span style="color:#16a34a;font-weight:700">+${{r.total_net.toLocaleString()}}</span>
        <span style="font-size:11px;color:#64748b;margin-left:6px">Grand ${{r.grand}}</span>
      </div>
    </div>`).join('') || '<div style="color:#94a3b8;text-align:center;padding:20px">無資料</div>';

  // Bullish divergence table
  document.getElementById('ifDivBody').innerHTML = div.map(r => {{
    const maClr = (r.pct_vs_ma||0) >= 0 ? '#16a34a' : '#dc2626';
    const fClr  = r.total_net > 0 ? '#16a34a' : '#dc2626';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td><b>${{r.grand}}</b></td>
      <td style="font-size:11px">${{r.final || '—'}}</td>
      <td style="text-align:right;color:${{r.foreign_net>=0?'#16a34a':'#dc2626'}}">${{(r.foreign_net||0).toLocaleString()}}</td>
      <td style="text-align:right;color:${{r.trust_net>=0?'#16a34a':'#dc2626'}}">${{(r.trust_net||0).toLocaleString()}}</td>
      <td style="text-align:right;font-weight:700;color:${{fClr}}">${{r.total_net > 0 ? '+' : ''}}${{(r.total_net||0).toLocaleString()}}</td>
      <td style="text-align:right;color:${{maClr}}">${{r.pct_vs_ma != null ? (r.pct_vs_ma > 0 ? '+' : '') + r.pct_vs_ma + '%' : '—'}}</td>
      <td><span style="font-size:11px;background:#fdf4ff;color:#7c3aed;padding:1px 6px;border-radius:4px">看漲背離</span></td>
    </tr>`;
  }}).join('');

  // All universe flows table
  document.getElementById('ifAllBody').innerHTML = all.map(r => {{
    const fClr = r.total_net > 0 ? '#16a34a' : r.total_net < 0 ? '#dc2626' : '#64748b';
    const divIcon = r.divergence ? (r.divergence.startsWith('價跌法買') ? '🔔' : '⚠️') : '';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td>${{r.grand || '—'}}</td>
      <td style="text-align:right;font-size:12px;color:${{r.foreign_net>=0?'#16a34a':'#dc2626'}}">${{(r.foreign_net||0).toLocaleString()}}</td>
      <td style="text-align:right;font-size:12px;color:${{r.trust_net>=0?'#16a34a':'#dc2626'}}">${{(r.trust_net||0).toLocaleString()}}</td>
      <td style="text-align:right;font-size:12px;color:${{r.dealer_net>=0?'#16a34a':'#dc2626'}}">${{(r.dealer_net||0).toLocaleString()}}</td>
      <td style="text-align:right;font-weight:700;color:${{fClr}}">${{r.total_net > 0 ? '+' : ''}}${{(r.total_net||0).toLocaleString()}}</td>
      <td style="font-size:11px">${{r.inst_signal || '—'}}</td>
      <td>${{divIcon}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ SECTOR REVENUE MACRO ════════════════════
function initSecMacro() {{
  const SM  = SECMACRO;
  const agg = SM.aggregate || {{}};
  const secs = SM.sector_stats || [];
  const uvs  = SM.universe_vs_sector || [];

  document.getElementById('smKpis').innerHTML = [
    ['🏢 上市家數',   agg.total_companies||0, '#0891b2'],
    ['✅ 正成長比率', (agg.beat_rate_all||0)+'%', '#16a34a'],
    ['🏭 產業數',    agg.total_sectors||0, '#374151'],
    ['⭐ 超越產業Alpha', (SM.outperformers||[]).length+'支', '#7c3aed'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  const momColor = m =>
    m.includes('強勁')?'#16a34a': m.includes('正成長')?'#2563eb':
    m.includes('持平')?'#64748b': m.includes('微衰')?'#f97316':'#dc2626';

  const secRow = s => {{
    const c = momColor(s.momentum);
    const barW = Math.max(0, Math.min(100, (s.median_yoy + 20) / 120 * 100));
    return `<div style="padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <span style="font-size:12px;font-weight:600">${{s.sector}}</span>
          <span style="font-size:10px;color:#94a3b8;margin-left:6px">${{s.count}}家</span>
        </div>
        <b style="color:${{c}};font-size:13px">${{s.median_yoy>0?'+':''}}${{s.median_yoy.toFixed(1)}}%</b>
      </div>
      <div style="height:4px;background:#f1f5f9;border-radius:2px;margin-top:3px">
        <div style="height:4px;width:${{barW}}%;background:${{c}};border-radius:2px"></div>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:1px">正成長率 ${{s.beat_rate}}% · ${{s.momentum}}</div>
    </div>`;
  }};

  document.getElementById('smTop5').innerHTML  = (SM.top5_sectors||[]).map(secRow).join('');
  document.getElementById('smBot5').innerHTML  = (SM.bottom5_sectors||[]).map(secRow).join('');

  document.getElementById('smAlphaBody').innerHTML = uvs.map(r => {{
    const vc = (r.vs_sector||0) > 5 ? '#16a34a' : (r.vs_sector||0) < -5 ? '#dc2626' : '#64748b';
    const fmt = v => v!=null ? (v>0?'+':'')+v.toFixed(1)+'%' : '—';
    return `<tr style="border-bottom:1px solid #f8fafc">
      <td style="padding:4px 8px;font-weight:700">${{r.code}}</td>
      <td style="padding:4px 8px;font-size:12px">${{r.name}}</td>
      <td style="padding:4px 8px;font-size:11px;color:#64748b">${{(r.sector||'').slice(0,6)}}</td>
      <td style="padding:4px 8px;text-align:right;color:${{(r.yoy||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{fmt(r.yoy)}}</td>
      <td style="padding:4px 8px;text-align:right;color:#64748b">${{fmt(r.sector_med)}}</td>
      <td style="padding:4px 8px;text-align:right;font-weight:700;color:${{vc}}">${{fmt(r.vs_sector)}}</td>
      <td style="padding:4px 8px;text-align:right">${{(r.grand||0).toFixed(1)}}</td>
      <td style="padding:4px 8px;font-size:11px">${{(r.final||'').slice(0,14)}}</td>
    </tr>`;
  }}).join('');

  // All 33 sectors as a compact grid
  document.getElementById('smAllSectors').innerHTML =
    `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px">` +
    secs.map(s => {{
      const c = momColor(s.momentum);
      return `<div style="background:#f8fafc;border-radius:6px;padding:8px 10px;border-left:3px solid ${{c}}">
        <div style="font-size:12px;font-weight:600;color:#374151">${{s.sector}}</div>
        <div style="font-size:11px;color:#94a3b8;margin-top:1px">${{s.count}}家 · 正成長${{s.beat_rate}}%</div>
        <div style="font-size:15px;font-weight:700;color:${{c}};margin-top:2px">${{s.median_yoy>0?'+':''}}${{s.median_yoy.toFixed(1)}}%</div>
        <div style="font-size:10px;color:${{c}}">${{s.momentum}}</div>
      </div>`;
    }}).join('') + `</div>`;
}}

// ═══════════════════════════════ CONVICTION MATRIX ═══════════════════════
function initConvMatrix() {{
  const C = CONVICTION;
  const all = C.all_results || [];
  const agg = C.aggregate  || {{}};
  const TIER_COLOR = {{'TIER1-CORE':'#7c3aed','TIER2-HIGH':'#1d4ed8','TIER3-MED':'#15803d','TIER4-LOW':'#64748b','TIER5-WATCH':'#94a3b8'}};

  document.getElementById('convKpis').innerHTML = [
    ['🔥 TIER1 核心', agg.tier1_core+'支', '#7c3aed'],
    ['💎 TIER2 主力', agg.tier2_high+'支', '#1d4ed8'],
    ['✅ TIER3 標準', agg.tier3_med+'支', '#15803d'],
    ['📊 中位確信分', agg.median_score, '#374151'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  const card = r => {{
    const c = TIER_COLOR[r.tier] || '#64748b';
    const mos = r.mos_pct != null ? (r.mos_pct>0?'+':'')+r.mos_pct.toFixed(0)+'%' : '—';
    const q2  = r.q2_growth != null ? (r.q2_growth>0?'+':'')+r.q2_growth.toFixed(0)+'%' : '—';
    return `<div style="padding:6px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><b style="color:${{c}}">${{r.code}}</b> <span style="font-size:12px;color:#475569">${{r.name}}</span>
          ${{r.bonus?'<span style="font-size:10px;color:#7c3aed;background:#f5f3ff;padding:1px 4px;border-radius:3px;margin-left:4px">+'+r.bonus+'</span>':''}}</div>
        <b style="color:${{c}}">${{r.final_score.toFixed(1)}}</b>
      </div>
      <div style="height:4px;background:#f1f5f9;border-radius:2px;margin:4px 0">
        <div style="height:4px;width:${{Math.min(100,r.final_score)}}%;background:${{c}};border-radius:2px"></div>
      </div>
      <div style="font-size:11px;color:#94a3b8">Grand ${{r.grand}} · MoS ${{mos}} · Q2e ${{q2}} · DNA ${{r.bull_signs}}/6</div>
    </div>`;
  }};

  document.getElementById('convTier1').innerHTML = (C.tier1||[]).map(card).join('') || '<div style="color:#94a3b8;text-align:center;padding:12px">無資料</div>';
  document.getElementById('convTier2').innerHTML = (C.tier2||[]).map(card).join('') || '<div style="color:#94a3b8;text-align:center;padding:12px">無資料</div>';

  document.getElementById('convAllBody').innerHTML = all.map(r => {{
    const c = TIER_COLOR[r.tier] || '#94a3b8';
    const f = r.factors || {{}};
    return `<tr style="border-bottom:1px solid #f1f5f9">
      <td style="padding:5px 8px;font-weight:700;color:${{c}}">${{r.code}}</td>
      <td style="padding:5px 8px;font-size:12px">${{r.name}}</td>
      <td style="padding:5px 8px;text-align:right;font-weight:700;color:${{c}}">${{r.final_score.toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f1_grand||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f2_smc||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f3_action||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f4_mos||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f5_q2||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px">${{(f.f6_dna||0).toFixed(1)}}</td>
      <td style="padding:5px 8px;text-align:right;font-size:12px;color:#7c3aed">${{r.bonus>0?'+'+r.bonus.toFixed(1):'—'}}</td>
      <td style="padding:5px 8px;font-size:11px">${{r.label}}</td>
      <td style="padding:5px 8px;font-size:11px;color:#64748b">${{r.size_guide}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ MARGIN OF SAFETY ════════════════════════
function initMoS() {{
  const MOS = MOSDATA;
  const all = MOS.all_results || [];
  const gp  = MOS.best_garp  || [];
  const agg = MOS.aggregate  || {{}};

  const mosColor = m => m >= 40 ? '#15803d' : m >= 25 ? '#16a34a' : m >= 10 ? '#2563eb' : m >= 0 ? '#64748b' : '#dc2626';

  document.getElementById('mosKpis').innerHTML = [
    ['🛡 超高安全(≥40%)', (all.filter(r=>r.mos_pct>=40).length)+'支', '#15803d'],
    ['✅ 高安全(25-40%)',  (all.filter(r=>r.mos_pct>=25&&r.mos_pct<40).length)+'支', '#16a34a'],
    ['⚖ 合理(0-25%)',    (all.filter(r=>r.mos_pct>=0&&r.mos_pct<25).length)+'支', '#64748b'],
    ['❌ 高估(<0%)',      (all.filter(r=>r.mos_pct<0).length)+'支', '#dc2626'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  // Top 10 MoS
  const sorted = [...all].sort((a,b)=>b.mos_pct-a.mos_pct).slice(0,10);
  document.getElementById('mosTopList').innerHTML = sorted.map(r => {{
    const barW = Math.min(100, Math.max(0, r.mos_pct));
    return `<div style="padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px">
        <div><b>${{r.code}}</b> <span style="font-size:12px;color:#475569">${{r.name}}</span></div>
        <b style="color:${{mosColor(r.mos_pct)}}">${{r.mos_pct > 0 ? '+' : ''}}${{r.mos_pct.toFixed(1)}}%</b>
      </div>
      <div style="height:4px;background:#f1f5f9;border-radius:2px">
        <div style="height:4px;width:${{barW}}%;background:${{mosColor(r.mos_pct)}};border-radius:2px"></div>
      </div>
      <div style="font-size:11px;color:#94a3b8;margin-top:2px">現價 ${{r.price}} → 內在值 ${{r.intrinsic_value}} (FairPE ${{r.fair_pe}}x)</div>
    </div>`;
  }}).join('');

  // GARP picks
  document.getElementById('mosGarp').innerHTML = gp.slice(0,8).map(r => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div>
        <b>${{r.code}}</b> <span style="font-size:12px;color:#475569">${{r.name}}</span>
        <div style="font-size:11px;color:#64748b">EPS加速 ${{r.eps_accel!=null?(r.eps_accel>0?'+':'')+r.eps_accel.toFixed(0)+'%':'—'}} · Grand ${{r.grand}}</div>
      </div>
      <div style="text-align:right">
        <div style="color:#15803d;font-weight:700">MoS ${{r.mos_pct > 0 ? '+' : ''}}${{r.mos_pct.toFixed(1)}}%</div>
        <div style="font-size:11px;color:#94a3b8">${{r.safety.split(' ').slice(1).join(' ')}}</div>
      </div>
    </div>`).join('') || '<div style="color:#94a3b8;text-align:center;padding:16px">無資料</div>';

  // Full table
  const allSorted = [...all].sort((a,b)=>b.mos_pct-a.mos_pct);
  document.getElementById('mosAllBody').innerHTML = allSorted.map(r => {{
    const mc = mosColor(r.mos_pct);
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td style="font-size:11px;color:#94a3b8">${{r.sector}}</td>
      <td style="text-align:right">${{r.price?.toFixed(1) || '—'}}</td>
      <td style="text-align:right;font-weight:700;color:${{mc}}">${{r.intrinsic_value?.toFixed(1) || '—'}}</td>
      <td style="text-align:right;font-weight:700;color:${{mc}}">${{r.mos_pct != null ? (r.mos_pct>0?'+':'')+r.mos_pct.toFixed(1)+'%' : '—'}}</td>
      <td style="font-size:11px">${{r.safety || '—'}}</td>
      <td style="text-align:right">${{r.fair_pe != null ? r.fair_pe.toFixed(1)+'x' : '—'}}</td>
      <td style="text-align:right;font-size:12px">${{r.pe_curr != null ? r.pe_curr.toFixed(1)+'x' : '—'}}</td>
      <td style="text-align:right;font-size:12px;color:${{(r.eps_accel||0)>0?'#16a34a':'#dc2626'}}">${{r.eps_accel != null ? (r.eps_accel>0?'+':'')+r.eps_accel.toFixed(0)+'%' : '—'}}</td>
      <td style="font-size:11px"><span style="color:${{r.eq_grade==='A+'?'#15803d':r.eq_grade==='A'?'#2563eb':'#64748b'}}">${{r.eq_grade || '—'}}</span></td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ DNA TRIGGER CALCULATOR ══════════════════
function initDnaTrigger() {{
  const DT  = DNATRIGGER;
  const all = DT.all_results  || [];
  const p1  = DT.near_triple  || [];
  const sum = DT.summary      || {{}};

  const diffColor = d => d <= 1 ? '#16a34a' : d <= 2 ? '#2563eb' : d <= 3 ? '#f59e0b' : d <= 4 ? '#dc2626' : '#374151';

  // KPIs
  document.getElementById('dtKpis').innerHTML = [
    ['⚡ 接近TRIPLE', (sum.near_triple_count||0)+'支', '#dc2626'],
    ['5/6 股票',     (sum.five_six_count||0)+'支', '#0369a1'],
    ['4/6 股票',     (sum.four_six_count||0)+'支', '#f59e0b'],
    ['S3單一缺失',   (sum.s3_only_count||0)+'支', '#7c3aed'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  // P1 priority list
  document.getElementById('dtP1List').innerHTML = p1.length ? p1.map(r => {{
    const trigerStr = r.s3_trigger_price
      ? `S3觸發價 <b style="color:#0369a1">TWD ${{r.s3_trigger_price.toFixed(1)}}</b> (現 ${{r.close}}, 需漲 <b style="color:#16a34a">+${{r.s3_upside_pct?.toFixed(1)}}%</b>)`
      : '見下方詳情';
    return `<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 14px;margin-bottom:8px;cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖與升評條件">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <b style="font-size:15px">${{r.code}} ${{r.name}}</b>
          <span style="font-size:11px;background:#fef2f2;color:#dc2626;padding:1px 6px;border-radius:4px;margin-left:6px">${{r.bull_signs}}/6 → TRIPLE</span>
        </div>
        <span style="font-size:12px;color:#7c3aed;font-weight:600">${{r.upgrade_label}}</span>
      </div>
      <div style="font-size:13px;color:#374151;margin-top:6px">${{trigerStr}}</div>
      <div style="font-size:11px;color:#94a3b8;margin-top:4px">缺失: ${{r.missing?.join(', ')}} | W%R現值: ${{r.sig_vals?.S3_wr50 ?? '—'}} | Grand: ${{r.grand}}</div>
    </div>`;
  }}).join('') : '<div style="color:#94a3b8;padding:20px;text-align:center">無即將升評股票</div>';

  // Full table
  document.getElementById('dtAllBody').innerHTML = all.map(r => {{
    const d = r.avg_difficulty || 3;
    const dc = diffColor(d);
    const s3t = r.s3_trigger_price ? `TWD ${{r.s3_trigger_price.toFixed(1)}}` : '—';
    const s3u = r.s3_upside_pct != null ? `+${{r.s3_upside_pct.toFixed(1)}}%` : '—';
    return `<tr style="cursor:pointer" onclick="showDnaScreenDetail('${{r.code}}')" title="點擊查看K線圖與升評條件">
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td style="text-align:center">
        <span style="font-size:13px;font-weight:700;color:#2563eb">${{r.bull_signs}}/6</span>
      </td>
      <td style="font-size:12px;color:#dc2626">${{(r.missing||[]).join(', ')}}</td>
      <td style="text-align:right;font-weight:700;color:#0369a1">${{s3t}}</td>
      <td style="text-align:right;color:#16a34a;font-weight:700">${{s3u}}</td>
      <td><span style="font-size:11px;color:${{dc}}">${{r.upgrade_label}}</span></td>
      <td style="font-size:11px;color:#475569">${{r.monday_priority?.split('—')[0] || '—'}}</td>
      <td style="text-align:right">${{r.grand}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ MASTER ACTION SIGNAL ════════════════════
function initActionSig() {{
  const AS  = ACTIONSIG;
  const all = AS.all_signals      || [];
  const bn  = AS.buy_now          || [];
  const nb  = AS.new_buy_signals  || [];
  const sum = AS.summary          || {{}};

  const actionColor = a => {{
    if (a.includes('立即')) return '#dc2626';
    if (a.includes('積極')) return '#16a34a';
    if (a.includes('買進')) return '#2563eb';
    if (a.includes('觀察')) return '#f59e0b';
    if (a.includes('持有')) return '#64748b';
    return '#94a3b8';
  }};

  // KPIs
  document.getElementById('asKpis').innerHTML = [
    ['🚀 立即買進', (sum.buy_now||0)+'支', '#dc2626'],
    ['✅ 積極買進', (sum.accumulate||0)+'支', '#16a34a'],
    ['📈 買進',     (sum.buy||0)+'支', '#2563eb'],
    ['🆕 新機會',   (sum.new_buys||0)+'支', '#7c3aed'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  // Buy now list
  document.getElementById('asBuyNow').innerHTML = bn.map(r => {{
    const q2 = r.q2_growth != null ? (r.q2_growth>0?'+':'')+r.q2_growth.toFixed(0)+'%' : '—';
    const inPos = r.in_position ? `<span style="font-size:10px;background:#f0fdf4;color:#16a34a;padding:1px 5px;border-radius:4px;margin-left:4px">${{r.cur_alloc}}%持倉</span>` : '';
    return `<div style="padding:6px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><b style="font-size:14px">${{r.code}}</b>
          <span style="font-size:13px;color:#475569;margin-left:4px">${{r.name}}</span>${{inPos}}</div>
        <b style="color:#dc2626">${{r.action_score.toFixed(1)}}</b>
      </div>
      <div style="font-size:11px;color:#64748b;margin-top:2px">${{r.rationale}}</div>
      <div style="font-size:11px;color:#94a3b8">Grand ${{r.grand}} · 法人 ${{r.inst_signal||'—'}} · Q2e ${{q2}} · ${{r.val_signal||'—'}}</div>
    </div>`;
  }}).join('') || '<div style="color:#94a3b8;padding:20px;text-align:center">無立即買進信號</div>';

  // New buy signals
  document.getElementById('asNewBuys').innerHTML = nb.map(r => {{
    const q2 = r.q2_growth != null ? (r.q2_growth>0?'+':'')+r.q2_growth.toFixed(0)+'%' : '—';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div>
        <b>${{r.code}}</b> <span style="font-size:12px;color:#475569">${{r.name}}</span>
        <div style="font-size:11px;color:#64748b">${{r.rationale}}</div>
      </div>
      <div style="text-align:right">
        <div style="color:#7c3aed;font-weight:700">${{r.action_score.toFixed(1)}}</div>
        <div style="font-size:11px;color:#94a3b8">Q2e ${{q2}}</div>
      </div>
    </div>`;
  }}).join('') || '<div style="color:#94a3b8;text-align:center;padding:16px">無新買入信號</div>';

  // Full table
  document.getElementById('asAllBody').innerHTML = all.map(r => {{
    const sc = r.action_score;
    const scClr = sc>=70?'#dc2626':sc>=55?'#16a34a':sc>=45?'#2563eb':sc>=35?'#f59e0b':'#94a3b8';
    const posTag = r.in_position
      ? `<span style="font-size:10px;background:#eff6ff;color:#2563eb;padding:1px 4px;border-radius:3px">${{r.cur_alloc}}%</span>`
      : '';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}} ${{posTag}}</td>
      <td style="font-size:11px;color:#94a3b8">${{r.sector}}</td>
      <td style="text-align:right;font-weight:700;color:${{scClr}}">${{sc.toFixed(1)}}</td>
      <td><span style="font-size:11px;color:${{actionColor(r.action)}}">${{r.action}}</span></td>
      <td style="text-align:right;font-size:12px">${{r.comp_a_grand != null ? r.comp_a_grand.toFixed(1) : '—'}}</td>
      <td style="text-align:right;font-size:12px">${{r.comp_b_smc != null ? r.comp_b_smc.toFixed(1) : '—'}}</td>
      <td style="text-align:right;font-size:12px">${{r.comp_c_eps != null ? r.comp_c_eps.toFixed(1) : '—'}}</td>
      <td style="text-align:right;font-size:12px">${{r.comp_d_dna != null ? r.comp_d_dna.toFixed(1) : '—'}}</td>
      <td style="font-size:11px;color:#475569">${{r.rationale}}</td>
      <td style="text-align:right">${{r.cur_alloc > 0 ? r.cur_alloc.toFixed(1)+'%' : '—'}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ SMART MONEY CONFLUENCE ══════════════════
function initSmartMoney() {{
  const SM  = SMARTMONEY;
  const all = SM.all_results        || [];
  const sq  = SM.squeeze_candidates || [];
  const sum = SM.summary            || {{}};

  // KPIs
  document.getElementById('smKpis').innerHTML = [
    ['🔥 強勢匯合', (sum.top_confluence_count || 0) + ' 支', '#b45309'],
    ['🔔 看漲背離', (sum.divergence_buy_count  || 0) + ' 支', '#7c3aed'],
    ['🌀 擠壓候選', (sum.squeeze_candidate_count || 0) + ' 支', '#dc2626'],
    ['⚠ 擁擠多頭', (sum.crowded_long_count     || 0) + ' 支', '#94a3b8'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  // Top 10 confluence
  const top10 = all.slice(0,10);
  document.getElementById('smTopList').innerHTML = top10.map(r => {{
    const pct = Math.round(r.confluence);
    const bar = `<div style="height:4px;background:linear-gradient(90deg,#f59e0b,${{pct>70?'#16a34a':'#3b82f6'}});width:${{pct}}%;border-radius:2px;min-width:4px;max-width:100%"></div>`;
    const divTag = r.divergence ? `<span style="font-size:10px;background:#fdf4ff;color:#7c3aed;padding:1px 5px;border-radius:4px;margin-left:4px">背離</span>` : '';
    return `<div style="padding:6px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
        <div><b>${{r.code}}</b> <span style="color:#475569;font-size:12px">${{r.name}}</span>${{divTag}}</div>
        <div style="font-weight:700;color:#b45309">${{r.confluence.toFixed(1)}}</div>
      </div>
      ${{bar}}
      <div style="font-size:11px;color:#94a3b8;margin-top:2px">${{r.signal}} · Grand ${{r.grand}} · ${{r.inst_signal || '—'}}</div>
    </div>`;
  }}).join('');

  // Squeeze candidates
  document.getElementById('smSqueeze').innerHTML = sq.slice(0,8).map(r => {{
    const sqClr = r.squeeze_score > 80 ? '#dc2626' : r.squeeze_score > 40 ? '#f59e0b' : '#64748b';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div>
        <b>${{r.code}}</b> <span style="font-size:12px;color:#475569">${{r.name}}</span>
        <span style="font-size:10px;background:#fef2f2;color:#dc2626;padding:1px 5px;border-radius:4px;margin-left:4px">${{r.squeeze_label}}</span>
      </div>
      <div style="text-align:right">
        <div style="color:${{sqClr}};font-weight:700">擠壓分 ${{r.squeeze_score.toFixed(0)}}</div>
        <div style="font-size:11px;color:#94a3b8">融券 ${{r.s_today || 0}}張 (${{r.short_ratio || 0}}%)</div>
      </div>
    </div>`;
  }}).join('') || '<div style="color:#94a3b8;padding:20px;text-align:center">無擠壓候選</div>';

  // Full table
  document.getElementById('smAllBody').innerHTML = all.map(r => {{
    const cf = r.confluence;
    const cfClr = cf >= 70 ? '#16a34a' : cf >= 55 ? '#2563eb' : cf >= 40 ? '#f59e0b' : '#94a3b8';
    const divIcon = r.divergence ? '🔔' : '';
    const sqIcon  = r.squeeze_score > 0 ? '🌀' : '';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td style="text-align:right;font-weight:700;color:${{cfClr}}">${{cf.toFixed(1)}}</td>
      <td style="font-size:11px">${{r.signal}}</td>
      <td style="text-align:right;font-size:12px">${{r.flow_pts}}</td>
      <td style="text-align:right;font-size:12px">${{r.fund_pts != null ? r.fund_pts.toFixed(1) : '—'}}</td>
      <td style="text-align:right;font-size:12px">${{r.margin_pts}}</td>
      <td style="text-align:right;font-size:12px">${{r.tech_pts}} ${{divIcon}}</td>
      <td style="text-align:right;font-size:12px">${{r.val_pts}}</td>
      <td style="text-align:right">${{r.grand}}</td>
      <td style="font-size:11px">${{r.final || '—'}}</td>
      <td style="font-size:11px">${{r.inst_signal || '—'}} ${{sqIcon}}</td>
      <td style="font-size:11px;color:${{r.margin_sig==='BULLISH'?'#16a34a':r.margin_sig==='BEARISH'?'#dc2626':'#64748b'}}">${{r.margin_sig || '—'}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ Q2 EPS FORECAST ═════════════════════════
function initQ2Forecast() {{
  const QF  = Q2FCST;
  const all = QF.all_forecasts   || [];
  const acc = QF.accelerating    || [];
  const dv  = QF.deep_value      || [];
  const tri = QF.triple_forecast || [];
  const agg = QF.aggregate       || {{}};

  // KPIs
  document.getElementById('q2Kpis').innerHTML = [
    ['📈 EPS加速', (agg.accelerating || 0) + ' 支', '#0369a1'],
    ['💎 深度低估', (agg.deep_value_growing || 0) + ' 支', '#15803d'],
    ['📊 中位Q2成長', (agg.median_q2_growth_pct > 0 ? '+' : '') + (agg.median_q2_growth_pct || 0).toFixed(1) + '%', '#2563eb'],
    ['💹 中位預估PE', (agg.median_fwd_pe || 0).toFixed(1) + 'x', '#7c3aed'],
  ].map(([l,v,c])=>`
    <div class="kpi-card">
      <div class="kpi-label">${{l}}</div>
      <div class="kpi-value" style="color:${{c}}">${{v}}</div>
    </div>`).join('');

  const valColor = v => {{
    if (!v || v==='—') return '#94a3b8';
    if (v==='超低估'||v==='深度低估') return '#16a34a';
    if (v==='低估') return '#2563eb';
    if (v==='合理') return '#374151';
    return '#dc2626';
  }};

  // Accelerating list
  document.getElementById('q2AccList').innerHTML = acc.slice(0,10).map(r => {{
    const g = (r.q2_eps_growth_pct > 0 ? '+' : '') + r.q2_eps_growth_pct.toFixed(1) + '%';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9">
      <div><b>${{r.code}}</b> <span style="color:#475569;font-size:12px">${{r.name}}</span>
        <span style="font-size:10px;color:#94a3b8;margin-left:4px">${{r.sector}}</span></div>
      <div style="text-align:right">
        <span style="color:#0369a1;font-weight:700">${{g}}</span>
        <span style="font-size:11px;color:${{valColor(r.val_signal)}};margin-left:6px">${{r.val_signal}}</span>
        ${{r.forward_pe_est ? `<div style="font-size:11px;color:#94a3b8">預估PE ${{r.forward_pe_est}}x</div>` : ''}}
      </div>
    </div>`;
  }}).join('') || '<div style="color:#94a3b8;text-align:center;padding:16px">無加速股</div>';

  // TRIPLE forecast
  document.getElementById('q2TripleList').innerHTML = tri.map(r => {{
    const g = (r.q2_eps_growth_pct > 0 ? '+' : '') + r.q2_eps_growth_pct.toFixed(1) + '%';
    return `<div style="padding:8px 0;border-bottom:1px solid #f1f5f9">
      <div style="display:flex;justify-content:space-between">
        <div><b style="font-size:14px">${{r.code}}</b>
          <span style="font-size:13px;color:#475569;margin-left:4px">${{r.name}}</span></div>
        <span style="font-size:12px;background:#fef2f2;color:#dc2626;padding:2px 8px;border-radius:4px">TRIPLE</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-top:6px;font-size:12px">
        <div style="color:#64748b">Q1 EPS<br><b>${{r.q1_eps?.toFixed(2) || '—'}}</b></div>
        <div style="color:#0369a1">Q2e EPS<br><b>${{r.q2_eps_est?.toFixed(2) || '—'}}</b> <span style="color:#16a34a">${{g}}</span></div>
        <div style="color:${{valColor(r.val_signal)}}">預估PE<br><b>${{r.forward_pe_est || '—'}}x</b> — ${{r.val_signal}}</div>
      </div>
    </div>`;
  }}).join('') || '<div style="color:#94a3b8;text-align:center;padding:16px">無資料</div>';

  // Full table — sort by Q2 growth desc
  const sorted = [...all].sort((a,b)=>(b.q2_eps_growth_pct||0)-(a.q2_eps_growth_pct||0));
  document.getElementById('q2AllBody').innerHTML = sorted.map(r => {{
    const g = r.q2_eps_growth_pct;
    const gClr = g > 50 ? '#16a34a' : g > 0 ? '#2563eb' : '#dc2626';
    const accIcon = r.eps_acc ? '⬆' : r.eps_dec ? '⬇' : '';
    const pec = r.pe_change;
    const pecStr = pec != null ? (pec > 0 ? `<span style="color:#dc2626">+${{pec}}</span>` : `<span style="color:#16a34a">${{pec}}</span>`) : '—';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td>${{r.name}}</td>
      <td style="font-size:11px;color:#94a3b8">${{r.sector || '—'}}</td>
      <td style="text-align:right">${{r.q1_eps?.toFixed(2) || '—'}}</td>
      <td style="text-align:right;font-weight:700">${{r.q2_eps_est?.toFixed(2) || '—'}}</td>
      <td style="text-align:right;font-weight:700;color:${{gClr}}">${{g != null ? (g>0?'+':'')+g.toFixed(1)+'%' : '—'}}</td>
      <td style="text-align:center">${{accIcon}}</td>
      <td style="text-align:right;font-size:12px">${{r.fwd_pe_curr != null ? r.fwd_pe_curr.toFixed(1)+'x' : '—'}}</td>
      <td style="text-align:right;font-weight:700;color:${{valColor(r.val_signal)}}">${{r.forward_pe_est != null ? r.forward_pe_est.toFixed(1)+'x' : '—'}}</td>
      <td style="text-align:right">${{pecStr}}</td>
      <td><span style="font-size:11px;color:${{valColor(r.val_signal)}}">${{r.val_signal}}</span></td>
      <td style="text-align:right;font-size:12px">${{r.apr_yoy != null ? (r.apr_yoy>0?'+':'')+r.apr_yoy.toFixed(1)+'%' : '—'}}</td>
    </tr>`;
  }}).join('');
}}

// ═══════════════════════════════ EXPORT ═══════════════════════════════════
function initExport() {{
  const M = EXPORTMANIFEST;
  const s = M.summary || {{}};
  const files = M.files || [];
  const REPORT_DATE = M.date || '{TODAY}';

  const iconMap = {{
    'STOCKS_MASTER.csv':    '📦',
    'STOCKS_SCREENER.csv':  '🔎',
    'STOCKS_FINANCIAL.csv': '📊',
    'STOCKS_TECHNICAL.csv': '🧬',
    'FULL_REPORT.md':       '📝',
  }};
  const colorMap = {{
    'STOCKS_MASTER.csv':    '#1e3a5f',
    'STOCKS_SCREENER.csv':  '#14532d',
    'STOCKS_FINANCIAL.csv': '#7f1d1d',
    'STOCKS_TECHNICAL.csv': '#4c1d95',
    'FULL_REPORT.md':       '#78350f',
  }};

  document.getElementById('exportFiles').innerHTML = files.map(f => {{
    const icon  = iconMap[f.name] || '📄';
    const color = colorMap[f.name] || '#374151';
    const url   = `/reports/${{REPORT_DATE}}/${{f.name}}`;
    return `
      <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px 20px;
                  margin-bottom:10px;display:flex;align-items:center;gap:16px">
        <div style="font-size:28px">${{icon}}</div>
        <div style="flex:1">
          <div style="font-weight:700;font-size:15px;color:${{color}}">${{f.name}}</div>
          <div style="font-size:13px;color:#64748b;margin-top:2px">${{f.desc}}
            &nbsp;·&nbsp; ${{f.rows}} 股 ${{f.cols > 1 ? `× ${{f.cols}} 欄位` : ''}}</div>
        </div>
        <a href="${{url}}" download style="background:${{color}};color:#fff;padding:8px 18px;
           border-radius:7px;font-weight:600;font-size:13px;text-decoration:none;
           transition:opacity .15s" onmouseover="this.style.opacity=.8" onmouseout="this.style.opacity=1">
          ↓ 下載
        </a>
      </div>`;
  }}).join('');

  document.getElementById('exportSummary').innerHTML = [
    {{label:'分析股票總數',   val:s.total_stocks||0,   color:'#374151'}},
    {{label:'TRIPLE CONFIRMED', val:s.triple_confirmed||0, color:'#c2410c'}},
    {{label:'BUY 以上評級',  val:s.buy_or_better||0,  color:'#16a34a'}},
    {{label:'A+ 盈利品質',   val:s.eq_a_plus||0,      color:'#0891b2'}},
    {{label:'近升評 (<5分)', val:s.near_upgrade||0,   color:'#7c3aed'}},
  ].map(k=>`<span style="display:inline-block;margin:4px 12px 4px 0">
    <span style="color:#64748b;font-size:13px">${{k.label}}：</span>
    <span style="font-weight:700;color:${{k.color}};font-size:15px">${{k.val}}</span>
  </span>`).join('');
}}

// ════════════════════════════════ EARNINGS QUALITY ═══════════════════════
function initEarningsQ() {{
  const E = EARNINGSQ;
  const gc = E.grade_counts || {{}};

  document.getElementById('eqKpis').innerHTML = [
    {{label:'A+ 最優質', val:gc['A+']||0, color:'#15803d', sub:'EQ 9-10分'}},
    {{label:'A  優質',   val:gc['A']||0,  color:'#1d4ed8', sub:'EQ 7-8分'}},
    {{label:'B  良好',   val:gc['B']||0,  color:'#d97706', sub:'EQ 5-6分'}},
    {{label:'C/D 偏弱',  val:gc['C_D']||0,color:'#dc2626', sub:'EQ < 5分'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:26px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  renderEQ('all','eq');
  document.getElementById('eqGrade').addEventListener('change', () =>
    renderEQ(document.getElementById('eqGrade').value, document.getElementById('eqSort').value));
  document.getElementById('eqSort').addEventListener('change', () =>
    renderEQ(document.getElementById('eqGrade').value, document.getElementById('eqSort').value));
}}

function renderEQ(gradeFilter, sortBy) {{
  const E = EARNINGSQ;
  let rows = [...(E.all_stocks||[])];

  if (gradeFilter === 'A+')   rows = rows.filter(r => r.eq_score >= 9);
  else if (gradeFilter === 'A')  rows = rows.filter(r => r.eq_score >= 7 && r.eq_score < 9);
  else if (gradeFilter === 'B')  rows = rows.filter(r => r.eq_score >= 5 && r.eq_score < 7);
  else if (gradeFilter === 'CD') rows = rows.filter(r => r.eq_score < 5);

  if (sortBy === 'eq')     rows.sort((a,b) => (b.eq_score||0)-(a.eq_score||0) || (b.grand||0)-(a.grand||0));
  else if (sortBy === 'grand')  rows.sort((a,b) => (b.grand||0)-(a.grand||0));
  else if (sortBy === 'accel')  rows.sort((a,b) => ((b.key_metrics?.eps_accel||0)-(a.key_metrics?.eps_accel||0)));
  else if (sortBy === 'margin') rows.sort((a,b) => ((b.key_metrics?.op_margin||0)-(a.key_metrics?.op_margin||0)));

  const fv = (v,d=1,suf='') => v==null?'—':Number(v).toFixed(d)+suf;
  const dot = v => v ? `<span style="color:#16a34a;font-size:14px">●</span>` :
                       `<span style="color:#e2e8f0;font-size:14px">○</span>`;

  const gradeColor = g => g.includes('A+') ? '#15803d' : g.includes('A ') ? '#1d4ed8' :
                          g.includes('B')  ? '#d97706' : '#dc2626';
  const eqBar = n => {{
    const w = Math.round(n/10*100);
    const c = n>=9?'#15803d':n>=7?'#1d4ed8':n>=5?'#d97706':'#dc2626';
    return `<div style="display:flex;align-items:center;gap:6px">
      <div style="width:50px;height:8px;background:#f1f5f9;border-radius:4px">
        <div style="width:${{w}}%;height:100%;background:${{c}};border-radius:4px"></div></div>
      <b style="color:${{c}}">${{n}}</b></div>`;
  }};

  document.getElementById('eqTableTitle').textContent =
    `盈利品質排名 — ${{gradeFilter==='all'?'全部':gradeFilter}} (${{rows.length}} 股)`;

  document.getElementById('tbodyEQ').innerHTML = rows.map(r => {{
    const m  = r.key_metrics || {{}};
    const sc = r.scores || {{}};
    const dots = [sc.EQ1_eps_positive, sc.EQ2_eps_accel_pos, sc.EQ3_accel_strong,
                  sc.EQ4_rev_yoy_pos, sc.EQ5_rev_accel, sc.EQ6_margin_healthy,
                  sc.EQ7_margin_quality, sc.EQ8_fwd_lt_trail, sc.EQ9_div_covered,
                  sc.EQ10_fwd_gt_trail].map(dot).join('');
    const verdBg = r.final&&r.final.includes('TRIPLE')?'#7c2d12':r.final&&r.final.includes('STRONG')?'#14532d':
                   r.final&&r.final.includes('BUY')?'#1e40af':'#374151';
    return `<tr>
      <td><b>${{r.code}}</b></td>
      <td style="font-size:12px">${{(r.name||'').split(' ')[0]}}</td>
      <td>${{eqBar(r.eq_score)}}</td>
      <td><span style="color:${{gradeColor(r.grade)}};font-weight:700;font-size:12px">${{r.grade.split(' ')[0]}}</span></td>
      <td style="color:${{(m.eps_accel||0)>=10?'#16a34a':(m.eps_accel||0)>=0?'#374151':'#dc2626'}};font-weight:600">
        ${{m.eps_accel!=null?(m.eps_accel>=0?'+':'')+fv(m.eps_accel,1)+'%':'—'}}</td>
      <td style="color:${{(m.op_margin||0)>=20?'#16a34a':(m.op_margin||0)>=10?'#374151':'#dc2626'}}">
        ${{fv(m.op_margin,1,'%')}}</td>
      <td style="color:#374151">${{fv(m.net_margin,1,'%')}}</td>
      <td>${{fv(m.fwd_pe,1,'x')}}</td>
      <td style="color:${{(m.div_yield||0)>=4.5?'#16a34a':'inherit'}}">${{fv(m.div_yield,2,'%')}}</td>
      <td style="font-weight:700;color:${{(r.grand||0)>=70?'#c2410c':(r.grand||0)>=60?'#1d4ed8':'#374151'}}">${{fv(r.grand)}}</td>
      <td><span style="background:${{verdBg}};color:#fff;padding:2px 5px;border-radius:3px;font-size:10px">${{r.final||'—'}}</span></td>
      <td style="letter-spacing:2px">${{dots}}</td>
    </tr>`;
  }}).join('') || '<tr><td colspan="12" style="color:#94a3b8;text-align:center;padding:16px">無資料</td></tr>';
}}

// ════════════════════════════════ PEER COMPARISON ════════════════════════
function initPeerComp() {{
  const P = PEERCOMP;
  const sectors = P.sectors || [];

  // Populate sector select
  const sel = document.getElementById('pcSector');
  sectors.forEach(s => {{
    const opt = document.createElement('option');
    opt.value = s.sector; opt.textContent = s.sector + ' (' + s.n_stocks + ')';
    sel.appendChild(opt);
  }});

  // Sector overview cards
  document.getElementById('pcSectorCards').innerHTML = sectors.map(s => {{
    const m = s.medians || {{}};
    const fv = (v,d=1,suf='') => v==null?'—':Number(v).toFixed(d)+suf;
    const bv = s.best_value;  const bg = s.best_grand;
    const by = s.best_yield;  const bG = s.best_growth;
    const hue = m.grand>=60?'#14532d':m.grand>=50?'#1e40af':m.grand>=40?'#374151':'#6b7280';
    return `<div class="card card-pad" style="border-top:3px solid ${{hue}}">
      <div style="font-weight:700;font-size:14px;margin-bottom:6px">${{s.sector}}
        <span style="float:right;font-size:11px;color:#94a3b8">${{s.n_stocks}}股</span></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px;margin-bottom:8px">
        <div><span style="color:#64748b">中位PE</span> <b>${{fv(m.pe,1,'x')}}</b></div>
        <div><span style="color:#64748b">中位殖</span> <b style="color:#16a34a">${{fv(m.div_yield,2,'%')}}</b></div>
        <div><span style="color:#64748b">Grand</span> <b style="color:${{hue}}">${{fv(m.grand,1)}}</b></div>
        <div><span style="color:#64748b">RS60</span> <b>${{m.rs_60d!=null?(m.rs_60d>=0?'+':'')+fv(m.rs_60d,1,'%'):'—'}}</b></div>
      </div>
      <div style="font-size:11px;display:grid;gap:2px">
        ${{bv?`<div>💰 最低PE: <b>${{bv.code}}</b> ${{bv.pe.toFixed(1)}}x</div>`:''}}
        ${{bg?`<div>🏆 最高Grand: <b>${{bg.code}}</b> ${{bg.grand.toFixed(1)}}</div>`:''}}
        ${{by?`<div>💎 最高殖: <b>${{by.code}}</b> ${{by.dy.toFixed(2)}}%</div>`:''}}
        ${{bG?`<div>📈 最高YoY: <b>${{bG.code}}</b> +${{bG.yoy.toFixed(0)}}%</div>`:''}}
      </div>
    </div>`;
  }}).join('');

  renderPeerTable('all','peer_rank');
  document.getElementById('pcSector').addEventListener('change', () =>
    renderPeerTable(document.getElementById('pcSector').value, document.getElementById('pcSort').value));
  document.getElementById('pcSort').addEventListener('change', () =>
    renderPeerTable(document.getElementById('pcSector').value, document.getElementById('pcSort').value));
}}

function renderPeerTable(sectorFilter, sortBy) {{
  const P = PEERCOMP;
  let rows = [];
  (P.sectors||[]).forEach(s => {{
    if (sectorFilter === 'all' || s.sector === sectorFilter)
      rows = rows.concat((s.stocks||[]).map(m => ({{...m, sector_med_pe: (s.medians||{{}}).pe}})));
  }});

  if (sortBy === 'peer_rank') rows.sort((a,b) => (b.peer_rank_score||0)-(a.peer_rank_score||0));
  else if (sortBy === 'grand') rows.sort((a,b) => (b.grand||0)-(a.grand||0));
  else if (sortBy === 'pe_rel') rows.sort((a,b) => ((a.pe_vs_sector||999)-(b.pe_vs_sector||999)));
  else if (sortBy === 'dy')     rows.sort((a,b) => ((b.div_yield||0)-(a.div_yield||0)));
  else if (sortBy === 'rev_yoy') rows.sort((a,b) => ((b.rev_yoy||0)-(a.rev_yoy||0)));

  const fv = (v,d=1) => v==null?'—':Number(v).toFixed(d);
  const pct = v => v==null?'—':`${{v>=0?'+':''}}${{fv(v)}}%`;

  const peRelBadge = v => {{
    if (v==null) return '<td>—</td>';
    const c = v<=-20?'#16a34a':v<=-10?'#2563eb':v>=20?'#dc2626':v>=10?'#d97706':'#64748b';
    const label = v<=-20?'深度折價':v<=-10?'折價':v>=20?'溢價':v>=10?'小溢價':'合理';
    return `<td><span style="color:${{c}};font-weight:600">${{pct(v)}}</span> <span style="font-size:11px;color:#94a3b8">${{label}}</span></td>`;
  }};

  const verdBadge = v => {{
    const bg = v&&v.includes('TRIPLE')?'#7c2d12':v&&v.includes('STRONG')?'#14532d':v&&v.includes('BUY')?'#1e40af':'#374151';
    return `<td><span style="background:${{bg}};color:#fff;padding:2px 5px;border-radius:3px;font-size:10px">${{v||'—'}}</span></td>`;
  }};

  document.getElementById('pcTableTitle').textContent =
    `同業詳細比較 — ${{sectorFilter==='all'?'全部產業':sectorFilter}} (${{rows.length}} 股)`;

  document.getElementById('tbodyPeer').innerHTML = rows.map(r => `<tr>
    <td><b>${{r.code}}</b></td>
    <td style="font-size:12px">${{(r.name||'').split(' ')[0]}}</td>
    <td style="font-size:11px;color:#64748b">${{r.sector}}</td>
    <td style="font-weight:700;color:${{(r.grand||0)>=70?'#c2410c':(r.grand||0)>=60?'#1d4ed8':'#374151'}}">${{fv(r.grand)}}</td>
    <td>${{r.pe?fv(r.pe,1)+'x':'—'}}</td>
    ${{peRelBadge(r.pe_vs_sector)}}
    <td style="color:${{(r.div_yield||0)>=4.5?'#16a34a':'inherit'}}">${{r.div_yield?fv(r.div_yield,2)+'%':'—'}}</td>
    <td style="color:${{(r.rev_yoy||0)>=0?'#16a34a':'#dc2626'}}">${{r.rev_yoy!=null?pct(r.rev_yoy):'—'}}</td>
    <td style="color:${{(r.rs_60d||0)>=0?'#16a34a':'#dc2626'}}">${{r.rs_60d!=null?pct(r.rs_60d):'—'}}</td>
    <td style="font-weight:${{(r.bull_signs||0)>=4?'700':'400'}};color:${{(r.bull_signs||0)>=4?'#c2410c':'#374151'}}">${{r.bull_signs||0}}/6</td>
    ${{verdBadge(r.final)}}
  </tr>`).join('') || '<tr><td colspan="11" style="color:#94a3b8;text-align:center;padding:16px">無資料</td></tr>';
}}

// ════════════════════════════════ SENSITIVITY ════════════════════════════
function initSensitivity() {{
  const S = SENSITIVITY;
  const all = S.all_stocks || [];

  document.getElementById('senKpis').innerHTML = [
    {{label:'近升評 (≤5pts)', val:S.near_upgrade_count||0, color:'#dc2626', sub:'可透過槓桿達成'}},
    {{label:'升評範圍 (≤10pts)', val:S.in_range_count||0, color:'#1d4ed8', sub:'有明確路徑'}},
    {{label:'已達TRIPLE', val:(S.already_triple||[]).length, color:'#16a34a', sub:'最高評級'}},
    {{label:'分析股票數', val:all.length, color:'#374151', sub:'全部成分股'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:26px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  const f = () => renderSensitivity(
    document.getElementById('senFilter').value,
    document.getElementById('senLever').value
  );
  document.getElementById('senFilter').addEventListener('change', f);
  document.getElementById('senLever').addEventListener('change', f);
  renderSensitivity('near','all');
}}

function renderSensitivity(filter, leverFilter) {{
  const S = SENSITIVITY;
  let stocks = S.all_stocks || [];

  if (filter === 'near')   stocks = stocks.filter(s => s.pts_to_next > 0 && s.pts_to_next <= 5 && s.upgradeable_soon);
  else if (filter === 'range')  stocks = stocks.filter(s => s.pts_to_next > 0 && s.pts_to_next <= 10);
  else if (filter === 'triple') stocks = stocks.filter(s => s.next_tier && s.next_tier.includes('TRIPLE'));

  if (leverFilter !== 'all') {{
    stocks = stocks.filter(s => (s.levers||[]).some(l => l.lever === leverFilter));
  }}

  const fv = (v,d=1) => v==null?'—':Number(v).toFixed(d);

  const leverColor = l =>
    l.lever==='估值'?'#1d4ed8': l.lever==='技術DNA'?'#c2410c':
    l.lever==='動能'?'#7c3aed': l.lever==='基本面'?'#16a34a':'#0891b2';
  const leverBg = l =>
    l.lever==='估值'?'#eff6ff': l.lever==='技術DNA'?'#fff7ed':
    l.lever==='動能'?'#f5f3ff': l.lever==='基本面'?'#f0fdf4':'#ecfeff';

  const tierColor = t =>
    t&&t.includes('TRIPLE')?'#7f1d1d':t&&t.includes('STRONG')?'#14532d':
    t&&t.includes('BUY')?'#1e40af':t&&t.includes('WATCH')?'#374151':'#64748b';

  if (!stocks.length) {{
    document.getElementById('senList').innerHTML =
      '<div style="text-align:center;color:#94a3b8;padding:32px">無符合條件股票</div>';
    return;
  }}

  const html = stocks.map(s => {{
    const c = s.current;
    const gap = s.pts_to_next;
    const urgency = gap<=1?'#dc2626':gap<=3?'#d97706':gap<=5?'#1d4ed8':'#374151';
    const scoreW = Math.round(c.grand / 100 * 100);

    return `<div class="card" style="margin-bottom:10px;border-left:4px solid ${{urgency}}">
      <div class="card-pad" style="display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:start">
        <!-- Left: identity + score -->
        <div>
          <div style="font-size:16px;font-weight:800">${{s.code}}</div>
          <div style="font-size:13px;color:#64748b;margin-bottom:8px">${{(s.name||'').split(' ')[0]}}</div>
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
            <div style="font-size:22px;font-weight:900;color:${{urgency}}">${{fv(c.grand,1)}}</div>
            <div style="font-size:11px;color:#94a3b8">/100</div>
          </div>
          <!-- Score components -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;font-size:11px">
            ${{['基本面','技術','估值','動能'].map((label,i)=>{{
              const val = [c.fund,c.tech,c.val,c.mom][i];
              const w = Math.round((val||0)/25*100);
              return `<div style="display:flex;align-items:center;gap:4px">
                <span style="color:#94a3b8;width:26px">${{label.slice(0,2)}}</span>
                <div style="flex:1;height:4px;background:#f1f5f9;border-radius:2px">
                  <div style="width:${{w}}%;height:100%;background:#6366f1;border-radius:2px"></div></div>
                <span style="color:#374151">${{fv(val)}}</span></div>`;
            }}).join('')}}
          </div>
          <div style="margin-top:8px">
            <span style="font-size:11px;background:${{tierColor(c.tier)+'22'}};color:${{tierColor(c.tier)}};padding:2px 6px;border-radius:4px;font-weight:600">
              ${{c.tier}}</span>
          </div>
        </div>
        <!-- Right: upgrade path -->
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
            <span style="font-size:12px;color:#64748b">升至</span>
            <span style="font-size:13px;font-weight:700;color:${{tierColor(s.next_tier)}}">${{s.next_tier||'—'}}</span>
            <span style="background:${{urgency}};color:#fff;font-size:12px;font-weight:700;padding:2px 8px;border-radius:6px;margin-left:auto">
              差 ${{fv(gap,1)}} 分</span>
          </div>
          <!-- Gap bar -->
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
            <div style="flex:1;height:10px;background:#f1f5f9;border-radius:5px;position:relative">
              <div style="width:${{Math.min(100,Math.round(c.grand/100*100))}}%;height:100%;background:${{urgency}};border-radius:5px;opacity:.7"></div>
              ${{gap>0?`<div style="position:absolute;top:0;left:${{Math.min(95,Math.round((c.grand+gap)/100*100))}}%;width:2px;height:100%;background:#94a3b8"></div>`:''}}</div>
            <span style="font-size:11px;color:#94a3b8;white-space:nowrap">${{fv(c.grand+gap,1)}} 目標</span>
          </div>
          <!-- Levers -->
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            ${{(s.levers||[]).slice(0,3).map(l=>`
              <div style="flex:1;min-width:140px;background:${{leverBg(l)}};border:1px solid ${{leverColor(l)+'44'}};
                border-radius:6px;padding:7px 10px">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                  <span style="font-size:11px;font-weight:700;color:${{leverColor(l)}};background:${{leverColor(l)+'22'}};
                    padding:1px 5px;border-radius:3px">${{l.lever}}</span>
                  <span style="font-size:13px;font-weight:700;color:${{leverColor(l)}};margin-left:auto">+${{fv(l.pts_gain,1)}}</span>
                </div>
                <div style="font-size:11px;color:#374151;margin-bottom:2px">${{l.action}}</div>
                <div style="font-size:10px;color:#94a3b8">觸發: ${{l.trigger}}</div>
              </div>`).join('')}}
          </div>
          ${{s.dna_gap_to3>0?`<div style="margin-top:6px;font-size:11px;color:#c2410c">⚠️ DNA信號需達3個以上觸發TRIPLE (現${{c.bull_signs}}/6, 差${{s.dna_gap_to3}}個)</div>`:''}}
          <div style="margin-top:6px;font-size:11px;color:#94a3b8">PE: ${{c.pe?fv(c.pe,1)+'x':'—'}} | 殖利率: ${{c.div_yield?fv(c.div_yield,2)+'%':'—'}} | DNA: ${{c.bull_signs}}/6</div>
        </div>
      </div>
    </div>`;
  }}).join('');

  document.getElementById('senList').innerHTML = html ||
    '<div style="text-align:center;color:#94a3b8;padding:32px">無符合條件股票</div>';
}}

// ════════════════════════════════ CATALYST CALENDAR ══════════════════════
function initCatalyst() {{
  const C = CATALYST;

  // KPIs
  const summary = C.summary || {{}};
  document.getElementById('catKpis').innerHTML = [
    {{label:'股票催化劑', val:summary.stocks_with_catalysts||0, color:'#1d4ed8', sub:'有催化劑個股'}},
    {{label:'週一關鍵事件', val:summary.high_june8||0, color:'#dc2626', sub:'{mondayplan.get("date", TODAY)} 追蹤'}},
    {{label:'5月營收預告', val:summary.revenue_plays||0, color:'#16a34a', sub:'6月10日發布後更新'}},
    {{label:'總體事件', val:(C.macro_events||[]).length, color:'#7c3aed', sub:'含財報/利率/ETF調整'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div>
    <div class="kpi-value" style="color:${{k.color}};font-size:26px">${{k.val}}</div>
    <div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  renderCatalyst('all','all');

  document.getElementById('catFilter').addEventListener('change', () =>
    renderCatalyst(document.getElementById('catFilter').value, document.getElementById('catMonth').value));
  document.getElementById('catMonth').addEventListener('change', () =>
    renderCatalyst(document.getElementById('catFilter').value, document.getElementById('catMonth').value));
}}

function renderCatalyst(filter, monthFilter) {{
  const C = CATALYST;
  const tl = C.timeline || [];
  const macroMap = {{}};
  (C.macro_events||[]).forEach(e => macroMap[e.date] = e);

  let html = '';
  for (const t of tl) {{
    const dt = t.date;
    if (monthFilter !== 'all' && !dt.startsWith(monthFilter)) continue;

    const macro = t.macro || macroMap[dt];
    const evts  = (t.events||[]);

    let filteredEvts = evts;
    if (filter === 'stock')   filteredEvts = evts;
    else if (filter === 'macro') filteredEvts = [];
    else if (filter === 'CRITICAL') filteredEvts = evts.filter(e => (e.priority||'').includes('CRITICAL'));
    else if (filter === 'HIGH')     filteredEvts = evts.filter(e => (e.priority||'').includes('HIGH') || (e.priority||'').includes('CRITICAL'));
    else if (filter === 'revenue')  filteredEvts = evts.filter(e => e.trigger && (e.trigger.includes('營收') || e.trigger.includes('YoY')));

    if (!macro && filteredEvts.length === 0) continue;

    const isPast = dt < '{TODAY}';
    const isToday = dt === '{TODAY}';
    const isHot   = macro && (macro.impact === 'HIGH' || macro.impact === 'VERY HIGH');

    html += `<div style="display:flex;gap:0;margin-bottom:16px">
      <!-- Date column -->
      <div style="width:110px;flex-shrink:0;padding-top:14px;text-align:right;padding-right:16px">
        <div style="font-size:13px;font-weight:700;color:${{isPast?'#94a3b8':isToday?'#c2410c':'#1e3a5f'}}">${{dt.slice(5)}}</div>
        <div style="font-size:11px;color:#94a3b8">${{dt.slice(0,4)}}</div>
      </div>
      <!-- Timeline line -->
      <div style="width:24px;flex-shrink:0;display:flex;flex-direction:column;align-items:center">
        <div style="width:12px;height:12px;border-radius:50%;background:${{isHot?'#dc2626':filteredEvts.length>0?'#2563eb':'#cbd5e1'}};margin-top:16px;flex-shrink:0"></div>
        <div style="width:2px;flex:1;background:#e2e8f0;margin-top:2px"></div>
      </div>
      <!-- Content -->
      <div style="flex:1;padding-bottom:4px">`;

    if (macro) {{
      const impactColor = macro.impact==='VERY HIGH'?'#7f1d1d':macro.impact==='HIGH'?'#1e3a5f':macro.impact==='MEDIUM'?'#1e40af':'#374151';
      const impactBg    = macro.impact==='VERY HIGH'?'#fee2e2':macro.impact==='HIGH'?'#eff6ff':'#f1f5f9';
      html += `<div style="background:${{impactBg}};border:1px solid ${{macro.impact==='VERY HIGH'?'#fca5a5':macro.impact==='HIGH'?'#93c5fd':'#e2e8f0'}};
        border-radius:8px;padding:10px 14px;margin-bottom:8px">
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-weight:700;color:${{impactColor}}">${{macro.event}}</span>
          <span style="font-size:11px;background:${{impactColor}};color:#fff;padding:1px 6px;border-radius:4px">${{macro.impact}}</span>
        </div>
        <div style="font-size:12px;color:#64748b;margin-top:4px">${{macro.note}}</div>
      </div>`;
    }}

    if (filteredEvts.length > 0) {{
      html += `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:6px">`;
      for (const e of filteredEvts) {{
        const priColor = (e.priority||'').includes('CRITICAL')?'#7f1d1d':
                         (e.priority||'').includes('HIGH')?'#1e3a5f':'#374151';
        const priBg    = (e.priority||'').includes('CRITICAL')?'#fee2e2':
                         (e.priority||'').includes('HIGH')?'#eff6ff':'#f8fafc';
        html += `<div style="background:${{priBg}};border:1px solid ${{(e.priority||'').includes('CRITICAL')?'#fca5a5':'#e2e8f0'}};
          border-radius:6px;padding:8px 12px">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
            <span style="font-weight:700;font-size:13px">${{e.code}}</span>
            <span style="font-size:12px;color:#64748b">${{e.name}}</span>
            <span style="margin-left:auto;font-size:11px;color:${{e.grand>=70?'#c2410c':e.grand>=60?'#1d4ed8':'#374151'}};font-weight:700">
              Grand ${{e.grand}}</span>
          </div>
          <div style="font-size:12px;color:${{priColor}};font-weight:600;margin-bottom:3px">${{e.trigger}}</div>
          <div style="font-size:11px;color:#64748b">→ ${{e.action}}</div>
        </div>`;
      }}
      html += `</div>`;
    }}

    html += `</div></div>`;
  }}

  if (!html) html = `<div style="text-align:center;color:#94a3b8;padding:32px">無符合條件的事件</div>`;
  document.getElementById('catTimeline').innerHTML = html;
}}

// ════════════════════════════════ STOCK DETAIL ════════════════════════════
function initStockDetail() {{
  const rptMap = {{}};
  STOCKREPORTS.forEach(r => rptMap[r.code] = r);
  const codes  = STOCKREPORTS.map(r => r.code).sort();

  // Populate dropdown
  const sel = document.getElementById('sdSelect');
  codes.forEach(c => {{
    const r = rptMap[c];
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c + ' ' + (r.name||'').split(' ')[0];
    sel.appendChild(opt);
  }});

  // Search box filter
  document.getElementById('sdSearch').addEventListener('input', function() {{
    const q = this.value.toLowerCase();
    Array.from(sel.options).forEach(o => {{
      o.hidden = q && !o.textContent.toLowerCase().includes(q);
    }});
  }});

  // Render on selection
  sel.addEventListener('change', () => renderStockDetail(rptMap[sel.value]));
  if (codes.length) {{ sel.value = codes[0]; renderStockDetail(rptMap[codes[0]]); }}
}}

function renderStockDetail(r) {{
  if (!r) return;
  const fv  = (v,d=1) => v==null?'—':Number(v).toFixed(d);
  const pct = v => v==null?'—':`${{v>=0?'+':''}}${{Number(v).toFixed(1)}}%`;
  const ok  = v => v?'<span style="color:#16a34a;font-weight:700">✅</span>':'<span style="color:#cbd5e1">○</span>';

  const rec = r.recommendation||{{}};
  const mkt = r.market_data||{{}};
  const val = r.valuation||{{}};
  const dna = r.technical_dna||{{}};
  const rs  = r.relative_strength||{{}};
  const fun = r.fundamental||{{}};
  const bt  = r.backtest||{{}};
  const sig = dna.signals||{{}};

  const bg = rec.final&&rec.final.includes('TRIPLE')?'#7f1d1d':
             rec.final&&rec.final.includes('STRONG')?'#14532d':
             rec.final&&rec.final.includes('BUY')  ?'#1e3a5f':'#374151';

  const scoreB = (v,mx=25) => {{
    const w = Math.min(100,Math.round((v||0)/mx*100));
    const c = w>=75?'#16a34a':w>=50?'#2563eb':'#94a3b8';
    return `<div style="display:flex;align-items:center;gap:6px">
      <div style="width:80px;height:8px;background:#f1f5f9;border-radius:4px">
        <div style="width:${{w}}%;height:100%;background:${{c}};border-radius:4px"></div>
      </div><span style="font-size:12px;font-weight:600">${{fv(v)}}</span></div>`;
  }};

  const sb = rec.score_breakdown||{{}};
  document.getElementById('sdPanel').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
      <!-- Header card -->
      <div style="grid-column:1/-1;background:${{bg}};border-radius:10px;padding:18px 24px;color:#fff;display:flex;align-items:center;justify-content:space-between">
        <div>
          <div style="font-size:28px;font-weight:800">${{r.code}} <span style="font-size:18px">${{(r.name||'').split(' ')[0]}}</span></div>
          <div style="opacity:.8;font-size:13px;margin-top:4px">${{r.sector||'—'}} | 資料: ${{r.generated||'—'}}</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:42px;font-weight:900">${{fv(rec.grand_score,0)}}</div>
          <div style="font-size:13px;opacity:.8">Grand Score</div>
          <div style="font-size:14px;font-weight:700;margin-top:4px">${{rec.final||'—'}}</div>
          <button onclick="openVegasChart('${{r.code}}')" style="margin-top:10px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.35);color:#fff;border-radius:7px;padding:6px 16px;font-size:13px;cursor:pointer;font-weight:600;letter-spacing:.3px">📊 K線圖</button>
        </div>
      </div>

      <!-- Score breakdown -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">🏆 評分分解</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div><div style="font-size:11px;color:#64748b;margin-bottom:4px">基本面 (25pts)</div>${{scoreB(sb.fundamental)}}</div>
          <div><div style="font-size:11px;color:#64748b;margin-bottom:4px">技術面 (25pts)</div>${{scoreB(sb.technical)}}</div>
          <div><div style="font-size:11px;color:#64748b;margin-bottom:4px">估值 (25pts)</div>${{scoreB(sb.valuation)}}</div>
          <div><div style="font-size:11px;color:#64748b;margin-bottom:4px">動能 (25pts)</div>${{scoreB(sb.momentum)}}</div>
        </div>
      </div>

      <!-- Market data -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">📈 市場數據</div>
        <table style="width:100%;font-size:13px">
          <tr><td style="color:#64748b;padding:4px 0">收盤價</td><td style="font-weight:700">¥${{fv(mkt.close)}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">月均線</td><td>¥${{fv(mkt.ma30)}} <span style="color:${{(mkt.pct_vs_ma||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{pct(mkt.pct_vs_ma)}}</span></td></tr>
          <tr><td style="color:#64748b;padding:4px 0">vs 基準</td><td style="color:${{(mkt.pct_vs_baseline||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{pct(mkt.pct_vs_baseline)}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">PE</td><td>${{fv(val.pe)}}x</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">PB</td><td>${{fv(val.pb,2)}}x</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">殖利率</td><td style="color:#16a34a;font-weight:600">${{fv(val.div_yield,2)}}%</td></tr>
        </table>
      </div>

      <!-- DNA signals -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">🧬 大飆股DNA <span style="font-size:22px;font-weight:900;color:${{(dna.bull_signs||0)>=4?'#c2410c':'#374151'}}">${{dna.bull_signs||0}}</span><span style="font-size:13px;color:#64748b">/6</span></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
          ${{Object.entries(sig).map(([k,s]) => `
            <div style="display:flex;align-items:center;gap:6px;padding:4px;background:${{s.ok?'#f0fdf4':'#f8fafc'}};border-radius:4px">
              ${{ok(s.ok)}}
              <span style="color:${{s.ok?'#14532d':'#64748b'}}">${{k.replace('_',' ').replace(/s\\d /,'').toUpperCase()}}</span>
              <span style="color:#94a3b8;margin-left:auto">${{s.val!=null?Number(s.val).toFixed(1):''}}</span>
            </div>`).join('')}}
        </div>
        <div style="margin-top:8px;font-size:12px;color:#64748b">研判: ${{dna.verdict||'—'}}</div>
      </div>

      <!-- Relative strength -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">📡 相對強度</div>
        <table style="width:100%;font-size:13px">
          <tr><td style="color:#64748b;padding:4px 0">60日RS</td><td style="font-weight:700;color:${{(rs.rs_60d||0)>=0?'#16a34a':'#dc2626'}}">${{pct(rs.rs_60d)}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">60日報酬</td><td style="color:${{(rs.ret_60d||0)>=0?'#16a34a':'#dc2626'}}">${{pct(rs.ret_60d)}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">距52週高</td><td style="color:${{(rs.pct_from_52w_high||0)>=-5?'#16a34a':'#dc2626'}}">${{pct(rs.pct_from_52w_high)}}</td></tr>
        </table>
      </div>

      <!-- Conviction Score -->
      ${{(()=>{{
        const cv = (CONVICTION.all_results||[]).find(x=>x.code===r.code);
        if (!cv) return '';
        const tc = {{'TIER1-CORE':'#7c3aed','TIER2-HIGH':'#1d4ed8','TIER3-MED':'#15803d','TIER4-LOW':'#64748b','TIER5-WATCH':'#94a3b8'}};
        const c  = tc[cv.tier]||'#64748b';
        const f  = cv.factors||{{}};
        const bars = [
          ['F1 Grand',  f.f1_grand||0, 30],
          ['F2 資金',   f.f2_smc||0,   20],
          ['F3 行動',   f.f3_action||0,20],
          ['F4 MoS',   f.f4_mos||0,   15],
          ['F5 Q2',    f.f5_q2||0,    10],
          ['F6 DNA',   f.f6_dna||0,    5],
        ];
        return `<div class="card card-pad" style="grid-column:1/-1">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div class="section-title">🔥 確信矩陣分數</div>
            <div style="text-align:right">
              <span style="font-size:28px;font-weight:900;color:${{c}}">${{cv.final_score.toFixed(1)}}</span>
              <span style="font-size:12px;color:#64748b"> / 100 &nbsp; ${{cv.label}}</span>
              <div style="font-size:12px;color:${{c}};font-weight:600">${{cv.tier}} — ${{cv.size_guide}}</div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px">
            ${{bars.map(([n,v,mx])=>`
              <div>
                <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">${{n}}</div>
                <div style="height:5px;background:#f1f5f9;border-radius:2px">
                  <div style="height:5px;width:${{Math.min(100,v/mx*100).toFixed(0)}}%;background:${{c}};border-radius:2px"></div>
                </div>
                <div style="font-size:11px;font-weight:600;color:#374151;margin-top:2px">${{v.toFixed(1)}} <span style="color:#94a3b8;font-weight:400">/${{mx}}</span></div>
              </div>`).join('')}}
          </div>
          ${{cv.bonus_reasons&&cv.bonus_reasons.length?`<div style="margin-top:8px;font-size:11px;color:#7c3aed">加成: ${{cv.bonus_reasons.join(' · ')}}</div>`:''}}
        </div>`;
      }})()}}

      <!-- Fundamental -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">📊 基本面</div>
        <table style="width:100%;font-size:13px">
          <tr><td style="color:#64748b;padding:4px 0">4月YoY</td><td style="color:${{(fun.apr_yoy||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{fun.apr_yoy!=null?pct(fun.apr_yoy):'—'}} <span style="color:#94a3b8;font-size:11px">${{fun.apr_accel||''}}</span></td></tr>
          <tr><td style="color:#64748b;padding:4px 0">5月展望</td><td style="font-size:12px">${{fun.may_outlook||'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">Q1 EPS</td><td>${{fun.q1_eps!=null?'¥'+fv(fun.q1_eps):'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">營收YoY</td><td style="color:${{(fun.rev_yoy||0)>=0?'#16a34a':'#dc2626'}}">${{fun.rev_yoy!=null?pct(fun.rev_yoy):'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">營業利益率</td><td>${{fun.op_margin!=null?fv(fun.op_margin,1)+'%':'—'}}</td></tr>
        </table>
      </div>

      <!-- Backtest -->
      <div class="card card-pad">
        <div class="section-title" style="margin-bottom:10px">🔬 DNA回測</div>
        ${{bt.num_signals>0?`
        <table style="width:100%;font-size:13px">
          <tr><td style="color:#64748b;padding:4px 0">訊號次數</td><td style="font-weight:700">${{bt.num_signals}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">20日均報酬</td><td style="color:${{(bt.avg_20d||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{bt.avg_20d!=null?pct(bt.avg_20d):'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">20日勝率</td><td style="font-weight:600">${{bt.win_20d!=null?fv(bt.win_20d,0)+'%':'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">60日均報酬</td><td style="color:${{(bt.avg_60d||0)>=0?'#16a34a':'#dc2626'}};font-weight:600">${{bt.avg_60d!=null?pct(bt.avg_60d):'—'}}</td></tr>
          <tr><td style="color:#64748b;padding:4px 0">60日勝率</td><td style="font-weight:600">${{bt.win_60d!=null?fv(bt.win_60d,0)+'%':'—'}}</td></tr>
        </table>`:'<div style="color:#94a3b8;font-size:13px">無回測資料</div>'}}
      </div>

      <!-- Alerts -->
      ${{r.alerts&&r.alerts.length?`
      <div class="card card-pad" style="grid-column:1/-1;background:#fffbeb;border-color:#fbbf24">
        <div class="section-title" style="margin-bottom:8px">⚠️ 警示訊號</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          ${{r.alerts.map(a=>`<span style="background:#fef3c7;color:#92400e;padding:4px 10px;border-radius:6px;font-size:13px;font-weight:600">${{a}}</span>`).join('')}}
        </div>
      </div>`:''}}
      ${{r.portfolio_weight_pct?`
      <div class="card card-pad" style="background:#eff6ff">
        <div class="section-title" style="margin-bottom:8px">🎯 組合最優權重</div>
        <div style="font-size:28px;font-weight:800;color:#1d4ed8">${{fv(r.portfolio_weight_pct,1)}}%</div>
        <div style="font-size:12px;color:#64748b">Max Sharpe 最優配置</div>
      </div>`:''}}
    </div>`;
}}
// ═══════════════════════ INTERACTIVE K-LINE CHART (EMA10/20/60) ═════════════
const EMA_PERIODS = [10, 20, 60];
const EMA_COLORS  = ['#22d3ee', '#f59e0b', '#a78bfa'];

function closeVegasModal() {{
  document.getElementById('vegasModal').style.display = 'none';
  const c = document.getElementById('vegasCanvas');
  if (c) c.getContext('2d').clearRect(0, 0, c.width, c.height);
  window._vegasBaseImg = null;
}}

function _vegasCalcEMA(arr, period) {{
  const k = 2 / (period + 1);
  const res = new Array(arr.length).fill(null);
  let sum = 0, n = 0, start = -1;
  for (let i = 0; i < arr.length; i++) {{
    if (arr[i] == null) continue;
    sum += arr[i]; n++;
    if (n >= period) {{ res[i] = sum / period; start = i; break; }}
  }}
  if (start < 0) return res;
  for (let i = start + 1; i < arr.length; i++) {{
    if (arr[i] == null) {{ res[i] = res[i-1]; continue; }}
    res[i] = arr[i] * k + (res[i-1] || 0) * (1 - k);
  }}
  return res;
}}

async function openVegasChart(code) {{
  const nameRec = (ACTIONSIG.all_signals||[]).find(r=>r.code===code)
               || (SMARTMONEY.all_results||[]).find(r=>r.code===code) || {{}};
  const name = nameRec.name || '';
  const modal = document.getElementById('vegasModal');
  modal.style.display = 'flex';
  document.getElementById('vegasTitle').textContent = code + ' ' + name + ' — K線圖';
  const statusEl = document.getElementById('vegasStatus');
  statusEl.textContent = '📡 載入中…';
  document.getElementById('vegasCanvas').width = 10;
  document.getElementById('vegasLegend').innerHTML = '';
  window._vegasBaseImg = null;

  try {{
    const fmRec = (_fmData||[]).find(c=>c.code===code);
    const suffix = (fmRec&&fmRec.market==='OTC')?'.TWO':'.TW';
    const url = 'https://query1.finance.yahoo.com/v8/finance/chart/'+code+suffix+'?range=6mo&interval=1d&events=div%2Csplit';
    const res = await fetch(url);
    if (!res.ok) {{ const e = await res.json().catch(()=>({{}})); throw new Error('HTTP ' + res.status + (e.error ? ': '+e.error : '')); }}
    const json = await res.json();
    const result = json.chart.result[0];
    const ts = result.timestamp;
    const q  = result.indicators.quote[0];
    const ohlcv = ts.map((t, i) => ({{
      date:  new Date(t * 1000),
      open:  q.open[i],
      high:  q.high[i],
      low:   q.low[i],
      close: q.close[i],
      vol:   q.volume[i]
    }})).filter(d => d.open != null && d.close != null);
    if (!ohlcv.length) throw new Error('無資料');
    statusEl.textContent = '✅ ' + ohlcv.length + ' 個交易日 · 滑鼠移至圖表查看詳情';
    _renderVegasCanvas(ohlcv);
  }} catch(e) {{
    statusEl.innerHTML = '❌ 載入失敗: ' + e.message;
  }}
}}

function _renderVegasCanvas(ohlcv) {{
  const canvas = document.getElementById('vegasCanvas');
  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.parentElement.clientWidth - 4;
  const cssH = Math.max(300, Math.min(500, window.innerHeight * 0.52));
  canvas.style.width  = cssW + 'px';
  canvas.style.height = cssH + 'px';
  canvas.width  = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);

  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  const W = cssW, H = cssH;
  const P = {{t:28, r:68, b:40, l:8}};
  const cW = W - P.l - P.r, cH = H - P.t - P.b;

  const closes = ohlcv.map(d => d.close);
  const emas = EMA_PERIODS.map(p => _vegasCalcEMA(closes, p));

  const VIEW = Math.min(ohlcv.length, 200);
  const data   = ohlcv.slice(-VIEW);
  const eslice = emas.map(e => e.slice(-VIEW));

  let lo = Infinity, hi = -Infinity;
  data.forEach(d => {{ lo = Math.min(lo, d.low); hi = Math.max(hi, d.high); }});
  eslice.forEach(e => e.forEach(v => {{ if (v) {{ lo = Math.min(lo, v); hi = Math.max(hi, v); }} }}));
  const pad = (hi - lo) * 0.04;
  lo -= pad; hi += pad;
  const rng = hi - lo;

  const xS = i => P.l + (i + 0.5) / VIEW * cW;
  const yS = p => P.t + cH * (1 - (p - lo) / rng);
  const cand = Math.max(1.5, Math.min(9, cW / VIEW * 0.72));

  function drawBase() {{
    ctx.fillStyle = '#0f172a'; ctx.fillRect(0, 0, W, H);
    const TICKS = 6;
    for (let g = 0; g <= TICKS; g++) {{
      const y = P.t + (g / TICKS) * cH;
      ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(P.l, y); ctx.lineTo(W - P.r, y); ctx.stroke();
      const price = hi - (g / TICKS) * rng;
      ctx.fillStyle = '#64748b'; ctx.font = '10px monospace'; ctx.textAlign = 'right';
      ctx.fillText(price.toFixed(1), W - P.r + 60, y + 4);
    }}
    data.forEach((d, i) => {{
      const x = xS(i);
      const col = d.close >= d.open ? '#22c55e' : '#ef4444';
      ctx.strokeStyle = col; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x, yS(d.high)); ctx.lineTo(x, yS(d.low)); ctx.stroke();
      const y1 = yS(Math.max(d.open, d.close));
      const y2 = yS(Math.min(d.open, d.close));
      ctx.fillStyle = col;
      ctx.fillRect(x - cand/2, y1, cand, Math.max(1, y2 - y1));
    }});
    EMA_PERIODS.forEach((period, pi) => {{
      const ema = eslice[pi];
      ctx.strokeStyle = EMA_COLORS[pi]; ctx.lineWidth = 1.8;
      ctx.beginPath(); let begun = false;
      ema.forEach((v, i) => {{
        if (!v) return;
        const x = xS(i), y = yS(v);
        begun ? ctx.lineTo(x, y) : (ctx.moveTo(x, y), begun = true);
      }});
      ctx.stroke();
    }});
    const step = Math.max(1, Math.floor(VIEW / 10));
    ctx.fillStyle = '#475569'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
    data.forEach((d, i) => {{
      if (i % step === 0 || i === VIEW - 1) {{
        const lbl = d.date.getFullYear() + '/' + String(d.date.getMonth()+1).padStart(2,'0');
        ctx.fillText(lbl, xS(i), H - P.b + 16);
      }}
    }});
  }}

  drawBase();
  window._vegasBaseImg = ctx.getImageData(0, 0, Math.round(cssW * dpr), Math.round(cssH * dpr));

  document.getElementById('vegasLegend').innerHTML =
    EMA_PERIODS.map((p, i) =>
      '<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px">' +
      '<span style="display:inline-block;width:22px;height:3px;background:' + EMA_COLORS[i] + ';border-radius:1px;vertical-align:middle"></span>' +
      '<span style="color:#94a3b8;font-size:11px">EMA' + p + '</span></span>'
    ).join('') +
    '<span style="display:inline-flex;align-items:center;gap:4px;margin-right:10px">' +
    '<span style="display:inline-block;width:10px;height:10px;background:#22c55e;vertical-align:middle"></span>' +
    '<span style="color:#94a3b8;font-size:11px">陽線</span></span>' +
    '<span style="display:inline-flex;align-items:center;gap:4px">' +
    '<span style="display:inline-block;width:10px;height:10px;background:#ef4444;vertical-align:middle"></span>' +
    '<span style="color:#94a3b8;font-size:11px">陰線</span></span>';

  function _onPointer(mx, my) {{
    if (!window._vegasBaseImg) return;
    ctx.putImageData(window._vegasBaseImg, 0, 0);
    const idx = Math.round((mx - P.l - cW / VIEW / 2) / (cW / VIEW));
    const ci = Math.max(0, Math.min(VIEW - 1, idx));
    const d = data[ci];
    if (!d) return;
    const cx = xS(ci), cy = yS(d.close);
    ctx.save();
    ctx.strokeStyle = 'rgba(148,163,184,.55)'; ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);
    ctx.beginPath(); ctx.moveTo(cx, P.t); ctx.lineTo(cx, H - P.b); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(P.l, cy); ctx.lineTo(W - P.r, cy); ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
    ctx.fillStyle = '#e2e8f0'; ctx.font = 'bold 10px monospace'; ctx.textAlign = 'right';
    ctx.fillText(d.close.toFixed(1), W - P.r + 65, cy + 4);
    const fmt = v => v != null ? (+v).toFixed(1) : '—';
    const fmtV = v => v == null ? '—' : v >= 1e8 ? (v/1e8).toFixed(1)+'億' : v >= 1e4 ? (v/1e4).toFixed(0)+'萬' : String(v);
    const ds = d.date.getFullYear()+'/'+String(d.date.getMonth()+1).padStart(2,'0')+'/'+String(d.date.getDate()).padStart(2,'0');
    const lines = [ds,
      '開:'+fmt(d.open)+'  高:'+fmt(d.high),
      '低:'+fmt(d.low)+'  收:'+fmt(d.close),
      '量:'+fmtV(d.vol),
      ...EMA_PERIODS.map((p,i) => 'EMA'+p+':'+(eslice[i][ci]?eslice[i][ci].toFixed(1):'—'))
    ];
    const TW=152, LH=17, TP=8, TH=lines.length*LH+TP*2;
    let tx = cx+14; if (tx+TW > W-P.r) tx = cx-TW-10;
    let ty = Math.max(P.t+2, cy-TH/2); if (ty+TH > H-P.b) ty = H-P.b-TH-2;
    ctx.fillStyle='rgba(15,23,42,.92)'; ctx.strokeStyle='rgba(100,116,139,.45)'; ctx.lineWidth=1;
    const rr=6;
    ctx.beginPath();
    ctx.moveTo(tx+rr,ty); ctx.lineTo(tx+TW-rr,ty);
    ctx.arcTo(tx+TW,ty,tx+TW,ty+rr,rr); ctx.lineTo(tx+TW,ty+TH-rr);
    ctx.arcTo(tx+TW,ty+TH,tx+TW-rr,ty+TH,rr); ctx.lineTo(tx+rr,ty+TH);
    ctx.arcTo(tx,ty+TH,tx,ty+TH-rr,rr); ctx.lineTo(tx,ty+rr);
    ctx.arcTo(tx,ty,tx+rr,ty,rr); ctx.closePath();
    ctx.fill(); ctx.stroke();
    ctx.textAlign='left';
    lines.forEach((line,li) => {{
      ctx.fillStyle = li===0?'#f1f5f9':li<=3?'#94a3b8':EMA_COLORS[li-4];
      ctx.font = li===0?'bold 11px sans-serif':'10px monospace';
      ctx.fillText(line, tx+TP, ty+TP+12+li*LH);
    }});
  }}

  canvas.onmousemove  = e => _onPointer(e.offsetX, e.offsetY);
  canvas.onmouseleave = () => {{ if (window._vegasBaseImg) ctx.putImageData(window._vegasBaseImg,0,0); }};
  canvas.ontouchmove  = e => {{
    e.preventDefault();
    const r = canvas.getBoundingClientRect();
    _onPointer(e.touches[0].clientX-r.left, e.touches[0].clientY-r.top);
  }};
  canvas.ontouchend = () => {{ if (window._vegasBaseImg) ctx.putImageData(window._vegasBaseImg,0,0); }};
}}

// ══════════════════════════ FULL MARKET (全市場) ════════════════════════════
let _fmData = [], _fmFiltered = [], _fmSortKey = 'quick_score', _fmSortAsc = false, _fmPageNum = 0;
const FM_PAGE = 50;

function initFullMarket() {{
  _fmData = (FULLMKT.companies || []);

  // KPI strip
  const total   = _fmData.length;
  const tse     = _fmData.filter(c=>c.market==='TSE').length;
  const otc     = _fmData.filter(c=>c.market==='OTC').length;
  const posYoy  = _fmData.filter(c=>(c.rev_yoy||0)>0).length;
  const posRate = total ? (posYoy/total*100).toFixed(1) : '—';
  const validPE   = _fmData.filter(c=>c.pe&&c.pe>0&&c.pe<200);
  const avgPE     = validPE.length ? (validPE.reduce((s,c)=>s+c.pe,0)/validPE.length).toFixed(1) : '—';
  const withEPS   = _fmData.filter(c=>c.eps_q1!=null).length;
  const posEPS    = _fmData.filter(c=>(c.eps_q1||0)>0).length;
  document.getElementById('fmKpis').innerHTML = [
    {{label:'上市+上櫃',   value:total+'支',               sub:'全市場'}},
    {{label:'TWSE上市',    value:tse+'支',                 sub:'TSE'}},
    {{label:'TPEX上櫃',    value:otc+'支',                 sub:'OTC'}},
    {{label:'Q1 EPS涵蓋',  value:withEPS+'支',             sub:`獲利 ${{posEPS}}支`}},
    {{label:'營收正成長',  value:posRate+'%',              sub:`${{posYoy}}支`}},
    {{label:'市場均值PE',  value:avgPE+'x',               sub:'有值股票'}},
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${{k.label}}</div><div class="kpi-val">${{k.value}}</div><div class="kpi-sub">${{k.sub}}</div></div>`).join('');

  // EPS leaderboard
  const topEPS = [..._fmData].filter(c=>c.eps_q1!=null).sort((a,b)=>(b.eps_q1||0)-(a.eps_q1||0)).slice(0,15);
  document.getElementById('fmEpsLeaderboard').innerHTML = topEPS.map((c,i)=>{{
    const mktBadge = c.market==='TSE'?'<span style="color:#2563eb;font-size:10px">TSE</span>':'<span style="color:#16a34a;font-size:10px">OTC</span>';
    return `<tr>
      <td style="color:#94a3b8">${{i+1}}</td>
      <td><b>${{c.code}}</b></td>
      <td style="max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{(c.name||'').split(' ')[0]}}</td>
      <td>${{mktBadge}}</td>
      <td style="font-weight:700;color:#c2410c">${{c.eps_q1!=null?c.eps_q1.toFixed(2):'—'}}</td>
      <td style="color:#16a34a">${{c.gross_margin!=null?c.gross_margin.toFixed(1)+'%':'—'}}</td>
    </tr>`;
  }}).join('');

  // Gross margin leaderboard (revenue > 100M NTD = 100,000 thousand)
  const topGM = [..._fmData].filter(c=>c.gross_margin!=null&&(c.rev_now||0)>100000)
    .sort((a,b)=>(b.gross_margin||0)-(a.gross_margin||0)).slice(0,15);
  document.getElementById('fmGmLeaderboard').innerHTML = topGM.map((c,i)=>{{
    const mktBadge = c.market==='TSE'?'<span style="color:#2563eb;font-size:10px">TSE</span>':'<span style="color:#16a34a;font-size:10px">OTC</span>';
    return `<tr>
      <td style="color:#94a3b8">${{i+1}}</td>
      <td><b>${{c.code}}</b></td>
      <td style="max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{(c.name||'').split(' ')[0]}}</td>
      <td>${{mktBadge}}</td>
      <td style="font-weight:700;color:#16a34a">${{c.gross_margin!=null?c.gross_margin.toFixed(1)+'%':'—'}}</td>
      <td style="color:#c2410c">${{c.eps_q1!=null?c.eps_q1.toFixed(2):'—'}}</td>
    </tr>`;
  }}).join('');

  // Sector dropdown
  const sectors = [...new Set(_fmData.map(c=>c.sector).filter(Boolean))].sort();
  const sel = document.getElementById('fmSector');
  sectors.forEach(s => {{ const o=document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); }});

  // Sector grid
  const secMap = {{}};
  _fmData.forEach(c => {{
    if (!c.sector) return;
    if (!secMap[c.sector]) secMap[c.sector] = {{cnt:0, pos:0, yoys:[]}};
    secMap[c.sector].cnt++;
    if ((c.rev_yoy||0)>0) secMap[c.sector].pos++;
    if (c.rev_yoy!=null) secMap[c.sector].yoys.push(c.rev_yoy);
  }});
  const secArr = Object.entries(secMap).map(([s,v])=>{{
    const med = v.yoys.length ? v.yoys.sort((a,b)=>a-b)[Math.floor(v.yoys.length/2)] : null;
    return {{sector:s, cnt:v.cnt, pos:v.pos, med}};
  }}).sort((a,b)=>(b.med||0)-(a.med||0));
  document.getElementById('fmSectorGrid').innerHTML = secArr.map(s=>{{
    const medStr = s.med!=null ? `${{s.med>=0?'+':''}}${{s.med.toFixed(1)}}%` : '—';
    const clr = s.med==null?'#94a3b8':s.med>10?'#16a34a':s.med>0?'#059669':s.med>-10?'#d97706':'#dc2626';
    return `<div class="card-pad" style="background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0">
      <div style="font-size:12px;font-weight:700;color:#374151;margin-bottom:4px">${{s.sector}}</div>
      <div style="display:flex;justify-content:space-between;align-items:baseline">
        <span style="font-size:11px;color:#64748b">${{s.cnt}}家</span>
        <span style="font-size:14px;font-weight:800;color:${{clr}}">${{medStr}}</span>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:2px">正成長 ${{s.pos}}/${{s.cnt}}</div>
    </div>`;
  }}).join('');

  renderFMTable();
}}

function renderFMTable() {{
  const mkt    = document.getElementById('fmMarket').value;
  const sec    = document.getElementById('fmSector').value;
  const yoyMin = parseFloat(document.getElementById('fmYoyMin').value);
  const peMax  = parseFloat(document.getElementById('fmPeMax').value);
  const epsF   = document.getElementById('fmEpsFilter').value;
  const q      = document.getElementById('fmSearch').value.toLowerCase().trim();
  const epsThresh = {{pos:0, gt1:1, gt3:3, gt5:5}}[epsF];

  _fmFiltered = _fmData.filter(c => {{
    if (mkt!=='ALL' && c.market!==mkt) return false;
    if (sec && c.sector!==sec) return false;
    if (!isNaN(yoyMin) && (c.rev_yoy==null || c.rev_yoy<yoyMin)) return false;
    if (!isNaN(peMax)  && (c.pe==null || c.pe>peMax)) return false;
    if (epsF && (c.eps_q1==null || c.eps_q1<=epsThresh)) return false;
    if (q && !c.code.toLowerCase().includes(q) && !c.name.toLowerCase().includes(q) && !(c.sector||'').toLowerCase().includes(q)) return false;
    return true;
  }});

  _fmFiltered.sort((a,b) => {{
    const va = a[_fmSortKey]; const vb = b[_fmSortKey];
    if (va==null&&vb==null) return 0;
    if (va==null) return 1; if (vb==null) return -1;
    return _fmSortAsc ? va-vb : vb-va;
  }});

  _fmPageNum = 0;
  document.getElementById('fmCount').textContent = `共 ${{_fmFiltered.length}} 支`;
  renderFMPage();
}}

function renderFMPage() {{
  const start = _fmPageNum * FM_PAGE;
  const slice = _fmFiltered.slice(start, start + FM_PAGE);
  const fv = (v,d=1) => v==null?'<span style="color:#cbd5e1">—</span>':v.toFixed(d);
  const fp = (v) => v==null?'<span style="color:#cbd5e1">—</span>':`<span style="color:${{v>=0?'#16a34a':'#dc2626'}}">${{v>=0?'+':''}}${{v.toFixed(1)}}%</span>`;
  document.getElementById('tbodyFullMarket').innerHTML = slice.map(c => `
    <tr>
      <td><b>${{c.code}}</b></td>
      <td style="max-width:90px;overflow:hidden;text-overflow:ellipsis">${{c.name}}</td>
      <td><span style="font-size:10px;padding:2px 5px;border-radius:4px;background:${{c.market==='TSE'?'#eff6ff':'#f0fdf4'}};color:${{c.market==='TSE'?'#2563eb':'#16a34a'}}">${{c.market}}</span></td>
      <td style="font-size:11px;color:#64748b;max-width:80px;overflow:hidden;text-overflow:ellipsis">${{c.sector||'—'}}</td>
      <td>${{fv(c.price)}}</td>
      <td>${{fp(c.change)}}</td>
      <td style="color:${{(c.pe||0)<15?'#16a34a':(c.pe||0)>30?'#dc2626':'#374151'}}">${{fv(c.pe)}}x</td>
      <td>${{fv(c.pb)}}x</td>
      <td>${{fv(c.yield)}}%</td>
      <td>${{fp(c.rev_yoy)}}</td>
      <td style="font-weight:600;color:${{(c.eps_q1||0)>0?'#16a34a':(c.eps_q1!=null&&c.eps_q1<0)?'#dc2626':'#94a3b8'}}">${{c.eps_q1!=null?c.eps_q1.toFixed(2):'—'}}</td>
      <td style="color:${{(c.gross_margin||0)>40?'#16a34a':(c.gross_margin||0)>20?'#d97706':'#64748b'}}">${{c.gross_margin!=null?c.gross_margin.toFixed(1)+'%':'—'}}</td>
      <td style="color:${{(c.net_margin||0)>15?'#16a34a':(c.net_margin||0)>5?'#d97706':(c.net_margin!=null&&c.net_margin<0)?'#dc2626':'#64748b'}}">${{c.net_margin!=null?c.net_margin.toFixed(1)+'%':'—'}}</td>
      <td><span style="font-weight:700;color:${{(c.quick_score||0)>=6?'#16a34a':(c.quick_score||0)>=3?'#d97706':'#94a3b8'}}">${{c.quick_score||0}}</span></td>
    </tr>`).join('');

  const total = _fmFiltered.length;
  const pages = Math.ceil(total/FM_PAGE);
  document.getElementById('fmPageInfo').textContent = `第 ${{_fmPageNum+1}}/${{pages}} 頁 (${{start+1}}–${{Math.min(start+FM_PAGE,total)}})`;
  document.getElementById('fmPrevBtn').disabled = _fmPageNum===0;
  document.getElementById('fmNextBtn').disabled = _fmPageNum>=pages-1;
}}

function fmPage(dir) {{
  const pages = Math.ceil(_fmFiltered.length/FM_PAGE);
  _fmPageNum = Math.max(0, Math.min(pages-1, _fmPageNum+dir));
  renderFMPage();
}}

function fmSort(key) {{
  if (_fmSortKey===key) _fmSortAsc=!_fmSortAsc;
  else {{ _fmSortKey=key; _fmSortAsc=false; }}
  renderFMTable();
}}

function fmResetFilters() {{
  document.getElementById('fmMarket').value='ALL';
  document.getElementById('fmSector').value='';
  document.getElementById('fmYoyMin').value='';
  document.getElementById('fmPeMax').value='';
  document.getElementById('fmEpsFilter').value='';
  document.getElementById('fmSearch').value='';
  renderFMTable();
}}

// ══════════════════════════ STRATEGY SYSTEM ═══════════════════════════════
function showStratTab(btn, id) {{
  const page = document.getElementById('page-strategy');
  page.querySelectorAll('.sub-tab').forEach(b => b.classList.remove('active'));
  page.querySelectorAll('.strat-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

function initStrategySystem() {{
  const T = TAIEX_DATA || {{}};
  // ── Step 1: N2 panel ──────────────────────────────────────────────────
  if (T.current) {{
    const close = T.current.close;
    document.getElementById('stN2Close').textContent = close.toLocaleString('zh-TW', {{maximumFractionDigits:2}});
    document.getElementById('stN2Date').textContent = T.current.date || '';
  }}
  if (T.n2) {{
    document.getElementById('stN2Val').textContent = T.n2.toLocaleString('zh-TW', {{maximumFractionDigits:2}});
    document.getElementById('stN2Standby').textContent = `${{T.standby?.toLocaleString('zh-TW', {{maximumFractionDigits:2}})}} ~ ${{T.n2?.toLocaleString('zh-TW', {{maximumFractionDigits:2}})}}`;
    const trendEl = document.getElementById('stN2Trend');
    trendEl.textContent = T.trend || '—';
    trendEl.style.color = T.trend === '多頭' ? '#22c55e' : '#f87171';
    const zoneEl = document.getElementById('stN2Zone');
    zoneEl.textContent = T.in_standby ? '⚡ 目前在待機區' : (T.trend === '多頭' ? '多頭格局' : '空頭格局');
    zoneEl.style.color = T.in_standby ? '#fbbf24' : '#94a3b8';
    document.getElementById('stN2High').textContent = T.n2_high?.toLocaleString('zh-TW', {{maximumFractionDigits:2}}) || '—';
    document.getElementById('stN2Low').textContent = T.n2_low?.toLocaleString('zh-TW', {{maximumFractionDigits:2}}) || '—';
  }}
  // Draw TAIEX chart
  _drawTaiexChart(T);

  // ── Crisis levels ─────────────────────────────────────────────────────
  if (T.n2) {{
    const n2 = T.n2;
    const close = T.current?.close || n2;
    const aboveEl = document.getElementById('stratCrisisAbove');
    if (aboveEl) {{
      aboveEl.textContent = close > n2 ? '之上 ✅' : '之下 ⚠️';
      aboveEl.style.color = close > n2 ? '#22c55e' : '#f87171';
    }}
    const levels = [
      {{ label:'N2 (警戒)', val:n2, color:'#fbbf24', desc:'跌破→待機' }},
      {{ label:'N2 − 300', val:n2-300, color:'#f97316', desc:'跌破→防禦' }},
      {{ label:'N2 − 600', val:n2-600, color:'#ef4444', desc:'跌破→危機出場' }},
    ];
    const container = document.getElementById('stratCrisisLevels');
    if (container) {{
      container.innerHTML = levels.map(l => `
        <div style="padding:10px;background:#1a0404;border:1px solid ${{l.color}}33;border-radius:8px;text-align:center">
          <div style="color:${{l.color}};font-weight:700">${{l.label}}</div>
          <div style="font-size:18px;font-weight:700;color:#f1f5f9">${{l.val.toLocaleString('zh-TW',{{maximumFractionDigits:0}})}}</div>
          <div style="font-size:11px;color:#94a3b8">${{l.desc}}</div>
          <div style="font-size:11px;color:${{close > l.val ? '#22c55e':'#f87171'}}">${{close > l.val ? '✅ 安全':'⚠️ 已破'}}</div>
        </div>`).join('');
    }}
    const crisisBox = document.getElementById('strat-n2-crisis');
    if (crisisBox) {{
      const status = close > n2 ? '✅ 多頭格局 — 大盤在N2之上，可正常操作' : '⚠️ 空頭格局 — 大盤跌破N2，建議保守操作';
      const bg = close > n2 ? '#0f1a0a' : '#1a0404';
      const bc = close > n2 ? '#166534' : '#991b1b';
      const tc = close > n2 ? '#4ade80' : '#f87171';
      crisisBox.style.background = bg;
      crisisBox.style.border = `1px solid ${{bc}}`;
      crisisBox.innerHTML = `<div style="color:${{tc}};font-size:14px;font-weight:700">${{status}}</div>`;
    }}
  }}

  // ── Step 7: Buy module table ───────────────────────────────────────────
  renderStratBuy();

  // ── Step 8: Sell signal table ─────────────────────────────────────────
  _renderStratSell();

  // ── Step 4: Sector heatmap ────────────────────────────────────────────
  _renderStratSectors();

  // ── Step 5: Rocket candidates ─────────────────────────────────────────
  _renderStratRockets();

  // Strategy page date
  const D = DNA_FULLMKT || {{}};
  const el = document.getElementById('stratDate');
  if (el && D.data_date) el.textContent = `數據日期: ${{D.data_date}}`;

  // ── Step ②: MACD live status ─────────────────────────────────────────
  _renderStratMacd();

  // ── Step ③: Capital allocation W%R ───────────────────────────────────
  _renderStratCapital();

  // ── Step ⑨: 6K/9K ────────────────────────────────────────────────────
  _renderStrat6k9k();
}}

function _drawTaiexChart(T) {{
  const canvas = document.getElementById('stTaiexChart');
  if (!canvas || !T.history || !T.history.length) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.parentElement.offsetWidth - 2;
  const H = 220;
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);

  const hist = T.history;
  const closes = hist.map(r => r.close);
  const allVals = closes.concat([T.n2 || 0, T.standby || 0]);
  const minV = Math.min(...allVals) * 0.998;
  const maxV = Math.max(...allVals) * 1.002;

  const pad = {{l:50, r:16, t:16, b:32}};
  const cW = W - pad.l - pad.r;
  const cH = H - pad.t - pad.b;

  const xScale = i => pad.l + (i / (hist.length - 1)) * cW;
  const yScale = v => pad.t + cH - ((v - minV) / (maxV - minV)) * cH;

  // Background
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);

  // N2 and standby zone bands
  if (T.n2 && T.standby) {{
    const yN2 = yScale(T.n2), yStandby = yScale(T.standby);
    ctx.fillStyle = 'rgba(124,58,237,0.12)';
    ctx.fillRect(pad.l, yN2, cW, yStandby - yN2);
    // N2 line
    ctx.strokeStyle = '#a78bfa'; ctx.lineWidth = 1.5; ctx.setLineDash([6,4]);
    ctx.beginPath(); ctx.moveTo(pad.l, yN2); ctx.lineTo(pad.l + cW, yN2); ctx.stroke();
    // Standby line
    ctx.strokeStyle = '#fbbf24'; ctx.lineWidth = 1; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(pad.l, yStandby); ctx.lineTo(pad.l + cW, yStandby); ctx.stroke();
    ctx.setLineDash([]);
    // Labels
    ctx.fillStyle = '#a78bfa'; ctx.font = '10px sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(`N2 ${{T.n2.toFixed(0)}}`, 2, yN2 + 4);
    ctx.fillStyle = '#fbbf24';
    ctx.fillText(`待機 ${{T.standby.toFixed(0)}}`, 2, yStandby + 4);
  }}

  // Close line
  ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 2; ctx.setLineDash([]);
  ctx.beginPath();
  hist.forEach((r, i) => {{
    const x = xScale(i), y = yScale(r.close);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }});
  ctx.stroke();

  // Date labels (every ~10 bars)
  ctx.fillStyle = '#64748b'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
  const step = Math.max(1, Math.floor(hist.length / 8));
  hist.forEach((r, i) => {{
    if (i % step === 0) ctx.fillText(r.date.slice(5), xScale(i), H - 8);
  }});

  // Y-axis
  ctx.fillStyle = '#64748b'; ctx.textAlign = 'right';
  [minV, (minV + maxV)/2, maxV].forEach(v => {{
    ctx.fillText(v.toFixed(0), pad.l - 4, yScale(v) + 4);
  }});
}}

function renderStratBuy() {{
  const rows = (DNA_FULLMKT?.all_results || []);
  const minCond = parseInt(document.getElementById('stratBuyMin')?.value || 3);
  const search = (document.getElementById('stratBuySearch')?.value || '').toLowerCase();

  const totalSigs = r => r.strategy_signs != null ? r.strategy_signs
    : (r.s1_ok?1:0)+(r.s2_ok?1:0)+(r.s3_ok?1:0)+(r.s4_ok?1:0)+(r.s5_ok?1:0)+(r.s6_ok?1:0);
  const filtered = rows.filter(r => {{
    if (totalSigs(r) < minCond) return false;
    if (search && !r.code?.includes(search) && !(r.name||'').toLowerCase().includes(search)) return false;
    return true;
  }}).sort((a, b) => totalSigs(b) - totalSigs(a) || (b.mo_rsi4||0) - (a.mo_rsi4||0));

  const countEl = document.getElementById('stratBuyCount');
  if (countEl) countEl.textContent = `共 ${{filtered.length}} 支`;

  const ck = v => v ? '<span style="color:#22c55e;font-weight:700">✓</span>' : '<span style="color:#475569">·</span>';
  const tbody = document.getElementById('tbodyStratBuy');
  if (!tbody) return;
  tbody.innerHTML = filtered.slice(0, 200).map((r, i) => {{
    const sigs = (r.s1_ok?1:0)+(r.s2_ok?1:0)+(r.s3_ok?1:0)+(r.s4_ok?1:0)+(r.s5_ok?1:0)+(r.s6_ok?1:0);
    // Entry condition proxy: s3 (日W%R oversold) + s4 (RSI) = entry signal
    const entryOk = r.s3_ok && r.s4_ok;
    const verdColor = sigs>=5?'#22c55e':sigs>=3?'#86efac':'#94a3b8';
    return `<tr onclick="showDnaScreenDetail('${{r.code}}')" style="cursor:pointer" title="點擊查看K線圖">
      <td style="text-align:center;color:#64748b">${{i+1}}</td>
      <td style="font-weight:700;color:#60a5fa">${{r.code||''}}</td>
      <td>${{r.name||''}}</td>
      <td style="text-align:center">${{ck(r.s1_ok)}}</td>
      <td style="text-align:center">${{ck(r.s2_ok)}}</td>
      <td style="text-align:center">${{ck(r.s3_ok)}}</td>
      <td style="text-align:center">${{ck(r.s4_ok)}}</td>
      <td style="text-align:center">${{ck(r.s5_ok)}}</td>
      <td style="text-align:center">${{ck(r.s6_ok)}}</td>
      <td style="text-align:center">${{r.s7_ok != null ? ck(r.s7_ok) : '<span style="color:#475569;font-size:10px">—</span>'}}</td>
      <td style="text-align:center">${{r.s8_ok != null ? ck(r.s8_ok) : '<span style="color:#475569;font-size:10px">—</span>'}}</td>
      <td style="text-align:center">${{ck(entryOk)}}</td>
      <td style="text-align:center;font-weight:700;color:${{verdColor}}">${{r.strategy_signs != null ? r.strategy_signs+'/8' : sigs+'/6'}}</td>
      <td><span style="font-size:11px;color:${{verdColor}}">${{sigs>=5?'🚀 強買':sigs>=3?'📈 買進':'👀 觀察'}}</span></td>
    </tr>`;
  }}).join('');
}}

function _renderStratSell() {{
  const rows = (DNA_FULLMKT?.all_results || [])
    .filter(r => r.mo_rsi4 != null && r.mo_rsi4 >= 70)
    .sort((a, b) => (b.mo_rsi4||0) - (a.mo_rsi4||0))
    .slice(0, 50);
  const el = document.getElementById('stratSellTable');
  if (!el) return;
  if (!rows.length) {{ el.innerHTML = '<div style="color:#64748b;padding:12px">無高位月RSI個股</div>'; return; }}
  el.innerHTML = `<table class="data-table" style="font-size:12px"><thead><tr>
    <th>代號</th><th>名稱</th><th>月RSI(4)</th><th>月W%R(3)</th><th>訊號數</th><th>出場提示</th>
  </tr></thead><tbody>
    ${{rows.map(r => {{
      const sigs = (r.s1_ok?1:0)+(r.s2_ok?1:0)+(r.s3_ok?1:0)+(r.s4_ok?1:0)+(r.s5_ok?1:0)+(r.s6_ok?1:0);
      const sellWarn = r.mo_rsi4 >= 77 ? '⚠️ 月RSI超買' : r.mo_rsi4 >= 70 ? '注意高位' : '';
      return `<tr onclick="showDnaScreenDetail('${{r.code}}')" style="cursor:pointer" title="點擊查看K線圖">
        <td style="font-weight:700;color:#f87171">${{r.code}}</td>
        <td>${{r.name}}</td>
        <td style="text-align:right;color:${{r.mo_rsi4>=77?'#f87171':'#fbbf24'}}">${{(r.mo_rsi4||0).toFixed(1)}}</td>
        <td style="text-align:right;color:#94a3b8">${{r.mo_di1!=null?r.mo_di1.toFixed(1):'—'}}</td>
        <td style="text-align:center">${{sigs}}/6</td>
        <td style="color:#f87171;font-size:11px">${{sellWarn}}</td>
      </tr>`;
    }}).join('')}}
  </tbody></table>`;
}}

function _renderStratSectors() {{
  const rows = DNA_FULLMKT?.all_results || [];
  const secMap = {{}};
  rows.forEach(r => {{
    if (!r.sector) return;
    if (!secMap[r.sector]) secMap[r.sector] = {{count:0, rsiSum:0, sigSum:0}};
    secMap[r.sector].count++;
    secMap[r.sector].rsiSum += r.mo_rsi4 || 0;
    secMap[r.sector].sigSum += r.bull_signs || 0;
  }});
  const sectors = Object.entries(secMap).map(([sec, d]) => ({{
    sec, count: d.count, avgRsi: d.rsiSum / d.count, avgSig: d.sigSum / d.count
  }})).sort((a,b) => b.avgRsi - a.avgRsi).slice(0, 20);
  const el = document.getElementById('stratSectorTable');
  if (!el) return;
  el.innerHTML = `<table class="data-table" style="font-size:12px"><thead><tr>
    <th>產業</th><th>股票數</th><th>平均月RSI(4)</th><th>平均訊號數</th><th>族群強度</th>
  </tr></thead><tbody>
    ${{sectors.map(s => {{
      const strength = s.avgRsi >= 70 ? '🔥 強' : s.avgRsi >= 55 ? '📈 中' : '📉 弱';
      const rsiColor = s.avgRsi >= 70 ? '#f87171' : s.avgRsi >= 55 ? '#fbbf24' : '#94a3b8';
      return `<tr>
        <td style="font-weight:600">${{s.sec}}</td>
        <td style="text-align:center">${{s.count}}</td>
        <td style="text-align:right;color:${{rsiColor}};font-weight:700">${{s.avgRsi.toFixed(1)}}</td>
        <td style="text-align:right">${{s.avgSig.toFixed(1)}}</td>
        <td style="color:${{rsiColor}}">${{strength}}</td>
      </tr>`;
    }}).join('')}}
  </tbody></table>`;
}}

function _renderStratCapital() {{
  const C = TAIEX_CAPITAL || {{}};
  const el = document.getElementById('stratCapitalGauges');
  if (!el || !Object.keys(C).length) return;
  const wrColor = v => v > -20 ? '#f87171' : v > -50 ? '#fbbf24' : v > -80 ? '#22c55e' : '#86efac';
  const wrLabel = v => v > -20 ? '超買 → 減倉' : v > -50 ? '中性 → 持有' : v > -80 ? '偏弱 → 加碼' : '超賣 → 重倉';
  const items = [
    {{ key:'tw50',  label:'權值股 (0050)',    desc:'大型股指標' }},
    {{ key:'tw006', label:'富邦50 (006208)',  desc:'大型股指標' }},
    {{ key:'fin',   label:'金融 (0055)',      desc:'金融股指標' }},
    {{ key:'mid',   label:'中型100 (0051)',   desc:'中小型指標' }},
    {{ key:'taiex', label:'加權指數 (TWII)',  desc:'大盤總覽' }},
  ];
  el.innerHTML = items.filter(i => C[i.key]).map(i => {{
    const d = C[i.key];
    const wr = d.mo_wr3;
    const col = wrColor(wr);
    const lbl = wrLabel(wr);
    // W%R bar: 0 (overbought) to -100 (oversold); display as % fill
    const pct = Math.min(100, Math.max(0, (-wr)));
    return `<div class="kpi-card" style="border-color:${{col}}">
      <div class="kpi-label">${{i.label}}</div>
      <div class="kpi-value" style="color:${{col}};font-size:22px">${{wr.toFixed(1)}}</div>
      <div style="margin:4px 0;background:#1e293b;border-radius:4px;height:6px;overflow:hidden">
        <div style="height:100%;width:${{pct}}%;background:${{col}};border-radius:4px"></div>
      </div>
      <div class="kpi-sub" style="color:${{col}}">${{lbl}}</div>
      <div class="kpi-sub">${{i.desc}} | ${{d.close?.toLocaleString('zh-TW',{{maximumFractionDigits:2}})}}</div>
    </div>`;
  }}).join('');
}}

function _renderStratMacd() {{
  const M = TAIEX_MONTHLY?.macd || {{}};
  if (!M.short_dif) return;
  const arrowLabel = (a) => a===1?'↑①穿越0軸':a===2?'↑②金叉':a===3?'↓③穿零軸':a===4?'↓④死叉':'持續中';
  const arrowColor = (a) => (a===1||a===2)?'#22c55e':(a===3||a===4)?'#f87171':'#94a3b8';
  const el = document.getElementById('stratMacdStatus');
  if (!el) return;
  el.innerHTML = `
    <div class="kpi-card" style="border-color:#a78bfa">
      <div class="kpi-label">短線DIF (9/12/26)</div>
      <div class="kpi-value" style="color:${{M.short_dif_positive?'#22c55e':'#f87171'}}">${{(M.short_dif||0).toFixed(0)}}</div>
      <div class="kpi-sub" style="color:${{arrowColor(M.short_arrow)}}">${{arrowLabel(M.short_arrow)}}</div>
    </div>
    ${{M.long_dif != null ? `
    <div class="kpi-card" style="border-color:#7c3aed">
      <div class="kpi-label">長線DIF (200/209/210)</div>
      <div class="kpi-value" style="color:${{M.long_dif_positive?'#22c55e':'#f87171'}}">${{(M.long_dif||0).toFixed(0)}}</div>
      <div class="kpi-sub" style="color:${{arrowColor(M.long_arrow)}}">${{arrowLabel(M.long_arrow)}}</div>
    </div>
    <div class="kpi-card" style="border-color:${{M.long_spiral?'#22c55e':'#475569'}}">
      <div class="kpi-label">DIF210 螺旋攻擊</div>
      <div class="kpi-value" style="color:${{M.long_spiral?'#22c55e':'#94a3b8'}}">${{M.long_spiral?'✅ 確認':'—'}}</div>
      <div class="kpi-sub">${{M.long_dif_rising?'DIF持續上升':'DIF未上升'}}</div>
    </div>` : ''}}
  `;
}}

function _renderStrat6k9k() {{
  const K = TAIEX_MONTHLY?.sixk_ninekk || {{}};
  const count = K.red_count ?? 0;
  const sig6k = K.signal_6k ?? false;
  const sig9k = K.signal_9k ?? false;

  // Count KPIs
  const countEl = document.getElementById('strat6kCount');
  if (countEl) {{
    countEl.textContent = count;
    countEl.style.color = sig9k?'#f87171':sig6k?'#f97316':count>=3?'#fbbf24':'#22c55e';
  }}
  const sig6El = document.getElementById('strat6kSig');
  if (sig6El) {{
    sig6El.textContent = sig6k ? '⚠️ 觸發' : `差${{6-count}}根`;
    sig6El.style.color = sig6k ? '#f87171' : '#94a3b8';
  }}
  const sig9El = document.getElementById('strat9kSig');
  if (sig9El) {{
    sig9El.textContent = sig9k ? '🚨 觸發' : `差${{9-count}}根`;
    sig9El.style.color = sig9k ? '#f87171' : '#94a3b8';
  }}
  const blkEl = document.getElementById('stratBlack6kCount');
  if (blkEl) {{
    blkEl.textContent = K.black_count ?? 0;
    blkEl.style.color = K.signal_black6k ? '#22c55e' : '#94a3b8';
  }}

  // Banner
  const banner = document.getElementById('strat6k9kBanner');
  if (banner) {{
    if (sig9k) {{
      banner.innerHTML = `<div style="background:#1a0404;border:2px solid #ef4444;border-radius:10px;padding:14px 16px;font-size:14px;color:#f87171">
        🚨 <b>9K 清倉訊號已觸發 (${{count}}根)</b> — 依策略系統應全數出清所有持股。從弱勢/低獲利股開始賣出。
      </div>`;
    }} else if (sig6k) {{
      banner.innerHTML = `<div style="background:#1a0a00;border:2px solid #f97316;border-radius:10px;padding:14px 16px;font-size:14px;color:#fb923c">
        ⚠️ <b>6K 減碼訊號已觸發 (${{count}}根)</b> — 依策略系統應開始往上調節持股，弱勢股優先出清。
      </div>`;
    }} else {{
      banner.innerHTML = `<div style="background:#0f1a0a;border:1px solid #166534;border-radius:10px;padding:12px 16px;font-size:13px;color:#4ade80">
        ✅ 6K/9K 尚未觸發 (目前 ${{count}} 根) — 多頭趨勢延續中，可繼續持有。
      </div>`;
    }}
  }}

  // Monthly K chart
  _draw6kChart(K.monthly_bars || []);
}}

function _draw6kChart(bars) {{
  const canvas = document.getElementById('strat6kChart');
  if (!canvas || !bars.length) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.parentElement.offsetWidth - 2;
  const H = 200;
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);

  const allC = bars.map(b => b.close);
  const minV = Math.min(...allC) * 0.99;
  const maxV = Math.max(...allC) * 1.01;
  const pad = {{l:60, r:12, t:10, b:28}};
  const cW = W - pad.l - pad.r;
  const cH = H - pad.t - pad.b;
  const n = bars.length;
  const barW = Math.max(3, Math.floor(cW / n) - 2);

  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);

  const xOf = i => pad.l + (i / n) * cW + barW / 2;
  const yOf = v => pad.t + cH - ((v - minV) / (maxV - minV)) * cH;

  bars.forEach((b, i) => {{
    const x = pad.l + (i / n) * cW;
    const yo = yOf(b.open); const yc = yOf(b.close);
    const yh = yOf(b.high); const yl = yOf(b.low);
    const color = b.in_chain ? '#f97316' : b.is_red ? '#22c55e' : '#f87171';
    // Wick
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x + barW/2, yh); ctx.lineTo(x + barW/2, yl); ctx.stroke();
    // Body
    ctx.fillStyle = color;
    const top = Math.min(yo, yc); const bodyH = Math.max(2, Math.abs(yc - yo));
    ctx.fillRect(x + 1, top, barW - 2, bodyH);
    // Chain highlight
    if (b.in_chain) {{
      ctx.strokeStyle = '#fbbf24'; ctx.lineWidth = 1.5;
      ctx.strokeRect(x, top - 2, barW, bodyH + 4);
    }}
  }});

  // Date labels
  ctx.fillStyle = '#64748b'; ctx.font = '9px sans-serif'; ctx.textAlign = 'center';
  const step = Math.max(1, Math.floor(n / 10));
  bars.forEach((b, i) => {{
    if (i % step === 0) ctx.fillText(b.date.slice(2), xOf(i), H - 6);
  }});

  // Y labels
  ctx.textAlign = 'right'; ctx.fillStyle = '#64748b';
  [minV, (minV+maxV)/2, maxV].forEach(v => {{
    ctx.fillText((v/1000).toFixed(0)+'K', pad.l - 2, yOf(v) + 4);
  }});

  // Legend
  ctx.fillStyle = '#f97316'; ctx.font = '10px sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('■ 有效鏈紅K', pad.l + 4, H - 6);
}}

function _renderStratRockets() {{
  const rows = (DNA_FULLMKT?.all_results || [])
    .filter(r => r.bull_signs >= 5 || (r.bull_signs >= 4 && r.mo_rsi4 >= 70) || r.s7_ok || r.s8_ok)
    .sort((a,b) => {{
      const sa = (a.s7_ok?1:0)+(a.s8_ok?1:0)+(a.bull_signs||0);
      const sb = (b.s7_ok?1:0)+(b.s8_ok?1:0)+(b.bull_signs||0);
      return sb - sa;
    }})
    .slice(0, 30);
  const el = document.getElementById('stratRocketTable');
  if (!el) return;
  if (!rows.length) {{ el.innerHTML = '<div style="color:#64748b;padding:12px">無飆股候選</div>'; return; }}
  const hasSpiral = rows.some(r => r.s7_ok != null);
  el.innerHTML = `<table class="data-table" style="font-size:12px"><thead><tr>
    <th>代號</th><th>名稱</th><th>產業</th><th>訊號數</th><th>月RSI(4)</th>
    ${{hasSpiral ? '<th>⑦DIF210螺旋</th><th>⑧ADX300螺旋</th>' : ''}}
    <th>評級</th>
  </tr></thead><tbody>
    ${{rows.map(r => {{
      const color = (r.s7_ok && r.s8_ok) ? '#a78bfa' : r.bull_signs >= 5 ? '#22c55e' : '#fbbf24';
      const spiral = r.s7_ok && r.s8_ok ? '🌀 雙螺旋' : r.s7_ok ? '🌀 DIF螺旋' : r.s8_ok ? '📐 ADX螺旋' : r.bull_signs>=5 ? '🚀 強候選' : '📈 候選';
      return `<tr onclick="showDnaScreenDetail('${{r.code}}')" style="cursor:pointer" title="點擊查看K線圖">
        <td style="font-weight:700;color:#a78bfa">${{r.code}}</td>
        <td>${{r.name}}</td>
        <td style="font-size:11px;color:#94a3b8">${{r.sector||'—'}}</td>
        <td style="text-align:center;font-weight:700;color:${{color}}">${{r.bull_signs}}/6</td>
        <td style="text-align:right;color:${{(r.mo_rsi4||0)>=77?'#f87171':'#fbbf24'}}">${{(r.mo_rsi4||0).toFixed(1)}}</td>
        ${{hasSpiral ? `<td style="text-align:center">${{r.s7_ok != null ? (r.s7_ok?'<span style="color:#22c55e">✓</span>':'·') : '—'}}</td><td style="text-align:center">${{r.s8_ok != null ? (r.s8_ok?'<span style="color:#22c55e">✓</span>':'·') : '—'}}</td>` : ''}}
        <td style="color:${{color}};font-size:11px">${{spiral}}</td>
      </tr>`;
    }}).join('')}}
  </tbody></table>`;
}}
</script>

<!-- ══════════════════════════════ VEGAS CHANNEL MODAL ═════════════════ -->
<div id="vegasModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(2,6,23,.88);z-index:9999;align-items:center;justify-content:center;padding:16px;box-sizing:border-box" onclick="if(event.target===this)closeVegasModal()">
  <div style="background:#0f172a;border-radius:14px;padding:20px 24px;width:100%;max-width:1180px;position:relative;box-shadow:0 24px 64px rgba(0,0,0,.7)">
    <button onclick="closeVegasModal()" title="關閉" style="position:absolute;top:12px;right:14px;background:rgba(255,255,255,.08);border:none;color:#94a3b8;font-size:18px;cursor:pointer;border-radius:6px;width:30px;height:30px;display:flex;align-items:center;justify-content:center">✕</button>
    <div id="vegasTitle" style="color:#f1f5f9;font-size:16px;font-weight:700;margin-bottom:4px;padding-right:36px"></div>
    <div id="vegasStatus" style="color:#94a3b8;font-size:11px;margin-bottom:8px"></div>
    <canvas id="vegasCanvas" style="display:block;border-radius:8px;background:#0f172a;width:100%;touch-action:none;cursor:crosshair"></canvas>
    <div id="vegasLegend" style="margin-top:10px;display:flex;flex-wrap:wrap;gap:4px;align-items:center"></div>
  </div>
</div>

</body>
</html>"""

html = html.replace("</body>", '<div id="vc-sm" style="text-align:center;font-size:11px;color:#94a3b8;margin:14px 0;opacity:.85"></div><script>fetch("https://abacus.jasoncameron.dev/hit/sm413-etf/views").then(function(r){return r.json()}).then(function(d){var e=document.getElementById("vc-sm");if(e)e.textContent="👁 "+Number(d.value).toLocaleString()+" 次瀏覽 · views";}).catch(function(){});</script>' + "</body>")
out = Path("dashboard.html")
out.write_text(html, encoding="utf-8")
print(f"✓ Dashboard built: {out.resolve()}")
print(f"  Stocks: {len(stocks)} | Buys: {len(buys)} | Avg score: {avg_score:.1f}")
