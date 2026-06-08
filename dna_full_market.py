#!/usr/bin/env python3
"""
Full-market DNA screen — 6 pure-technical signals (massor5755 spec):
  S1: 月 +DI(1) > 50        Monthly DMI positive directional
  S2: 月 RSI(4) > 77         Monthly RSI(4) super-strong
  S3: 日 W%R(50) < 20        Daily Williams %R oversold/extension
  S4: 日 RSI(60) > 57        Daily RSI medium-term bullish
  S5: 週 VR(2) >= 150        Weekly Volume Ratio bullish
  S6: 月 VR(2) >= 150        Monthly Volume Ratio bullish

Downloads 3 timeframes via yfinance (no TWSE rate limit).
Output: dna_full_market.json
"""
import json, time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

print(f"[{datetime.now():%H:%M:%S}] === Full-Market DNA Screen (6-signal technical) ===")
print(f"  Report dir: {REPORT_DIR}")

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
print(f"  Companies loaded: {len(companies)}")

# ── Indicator helpers ─────────────────────────────────────────────────────────

def rsi_s(s, n):
    d  = s.diff(); g = d.clip(lower=0); l = (-d).clip(lower=0)
    ag = g.ewm(alpha=1/n, adjust=False).mean()
    al = l.ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100 / (1 + ag / al.replace(0, float("nan")))

def williams_r_s(h, l, c, n):
    hh = h.rolling(n).max(); ll = l.rolling(n).min()
    return (hh - c) / (hh - ll + 1e-10) * 100

def vr_s(close, volume, n):
    """Volume Ratio = (A + 0.5C) / (B + 0.5C) * 100
       A=up-day vol, B=down-day vol, C=flat-day vol, over n periods"""
    d = close.diff()
    A = volume.where(d > 0, 0).rolling(n).sum()
    B = volume.where(d < 0, 0).rolling(n).sum()
    C = volume.where(d == 0, 0).rolling(n).sum()
    denom = (B + C / 2).replace(0, float("nan"))
    return (A + C / 2) / denom * 100

def plus_di_s(high, low, close, n=1):
    """+DI(n): positive directional indicator (Wilder smoothing)"""
    prev_h = high.shift(1); prev_l = low.shift(1); prev_c = close.shift(1)
    up   = high - prev_h
    down = prev_l - low
    pdm = up.where((up > 0) & (up > down), 0.0)
    tr  = pd.concat([high - low,
                     (high - prev_c).abs(),
                     (low  - prev_c).abs()], axis=1).max(axis=1)
    if n == 1:
        return 100 * pdm / tr.replace(0, float("nan"))
    smoothed_pdm = pdm.ewm(alpha=1/n, adjust=False).mean()
    smoothed_tr  = tr.ewm(alpha=1/n, adjust=False).mean()
    return 100 * smoothed_pdm / smoothed_tr.replace(0, float("nan"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Build ticker lists ────────────────────────────────────────────────────────
tse_codes = [(c["code"], f"{c['code']}.TW")  for c in companies if c.get("market") != "OTC"]
otc_codes = [(c["code"], f"{c['code']}.TWO") for c in companies if c.get("market") == "OTC"]
all_pairs  = tse_codes + otc_codes
ticker_to_code = {p[1]: p[0] for p in all_pairs}
all_tickers    = [p[1] for p in all_pairs]

print(f"  TSE: {len(tse_codes)} | OTC: {len(otc_codes)}")

import yfinance as yf

BATCH = 200
batches = [all_tickers[i:i+BATCH] for i in range(0, len(all_tickers), BATCH)]

def download_tf(period, interval, label):
    """Download one timeframe for all tickers; return dict code→df."""
    out = {}
    print(f"\n  [{label}] Downloading {len(batches)} batches (period={period} interval={interval})...")
    for i, batch in enumerate(batches):
        try:
            raw = yf.download(batch, period=period, interval=interval,
                              auto_adjust=True, progress=False, group_by="ticker")
            if len(raw) == 0:
                continue
            for ticker in batch:
                code = ticker_to_code.get(ticker, "")
                if not code: continue
                try:
                    df = raw.xs(ticker, level=0, axis=1).dropna(how="all") if len(batch) > 1 else raw.dropna(how="all")
                    if len(df) >= 5:
                        out[code] = df
                except Exception:
                    continue
            print(f"    Batch {i+1}/{len(batches)}: {sum(1 for t in batch if ticker_to_code.get(t,'') in out)} with data", end="\r")
        except Exception as e:
            print(f"    Batch {i+1}/{len(batches)} error: {e}")
    print(f"  [{label}] Done: {len(out)} stocks with data          ")
    return out

# Download all three timeframes (daily 2y needed for MACD200/ADX300)
daily_data   = download_tf("2y",   "1d",  "Daily")
weekly_data  = download_tf("2y",   "1wk", "Weekly")
monthly_data = download_tf("2y",   "1mo", "Monthly")

# Latest date from daily
latest_date = "?"
for df in daily_data.values():
    if len(df) > 0:
        latest_date = str(df.index[-1].date())
        break

print(f"\n  Latest daily date: {latest_date}")

# ── Compute signals per stock ──────────────────────────────────────────────────
def col(df, name):
    cm = {c.lower(): c for c in df.columns}
    k  = cm.get(name.lower())
    return df[k] if k else None

results = []
for c in companies:
    code   = c["code"]
    name   = c.get("name","")
    market = c.get("market","TSE")
    sector = c.get("sector","")

    # Fundamentals (still stored for reference in detail panel)
    rev_yoy     = sf(c.get("rev_yoy"))
    eps_q1      = sf(c.get("eps_q1"))
    gm          = sf(c.get("gross_margin"))
    om          = sf(c.get("op_margin"))
    pe          = sf(c.get("pe"))
    pb          = sf(c.get("pb"))
    dy          = sf(c.get("yield"))
    quick_score = c.get("quick_score", 0)

    # ── Daily data ──────────────────────────────────────────────────────────
    dd = daily_data.get(code)
    wr50_v = rsi60_v = close_v = None
    dif210_v = dif210_spiral = adx300_v = adx300_spiral = None
    if dd is not None and len(dd) >= 50:
        dc = col(dd, "close"); dh = col(dd, "high"); dl = col(dd, "low")
        if dc is not None and dh is not None and dl is not None:
            wr  = williams_r_s(dh, dl, dc, 50)
            rs  = rsi_s(dc, 60)
            wr50_v  = float(wr.iloc[-1])  if not pd.isna(wr.iloc[-1])  else None
            rsi60_v = float(rs.iloc[-1])  if not pd.isna(rs.iloc[-1])  else None
            close_v = float(dc.iloc[-1])  if len(dc) > 0              else None

            # DIF210 = EMA(200) - EMA(209); requires ≥210 bars
            if len(dc) >= 210:
                e200 = dc.ewm(span=200, adjust=False).mean()
                e209 = dc.ewm(span=209, adjust=False).mean()
                dif  = e200 - e209
                dif210_v = float(dif.iloc[-1])
                # Spiral: DIF positive AND rising slope AND recent lows higher than older lows
                recent = dif.dropna().iloc[-20:]
                if len(recent) >= 10:
                    slope = (recent.iloc[-1] - recent.iloc[0]) / max(len(recent), 1)
                    dif_rising = slope > 0
                    above_zero = dif210_v > 0
                    # Check if recent local troughs are rising (convergence)
                    lows = [float(recent.iloc[i]) for i in range(len(recent)) if i > 0 and i < len(recent)-1
                            and recent.iloc[i] < recent.iloc[i-1] and recent.iloc[i] < recent.iloc[i+1]]
                    trough_rising = len(lows) >= 2 and lows[-1] > lows[0]
                    dif210_spiral = bool(dif_rising and above_zero and trough_rising)
                else:
                    dif210_spiral = False

            # ADX300: uses period=min(300, bars//2) with EWM proxy
            if len(dc) >= 30:
                n_adx = min(300, max(14, len(dc) // 2))
                tr1 = dh - dl
                tr2 = (dh - dc.shift()).abs()
                tr3 = (dl - dc.shift()).abs()
                tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                up  = dh - dh.shift(); dn = dl.shift() - dl
                dmp = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=dc.index)
                dmm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=dc.index)
                tr_s  = tr.ewm(span=n_adx, adjust=False).mean()
                dmp_s = dmp.ewm(span=n_adx, adjust=False).mean()
                dmm_s = dmm.ewm(span=n_adx, adjust=False).mean()
                dip   = 100 * dmp_s / tr_s.replace(0, float("nan"))
                dim   = 100 * dmm_s / tr_s.replace(0, float("nan"))
                dx    = 100 * (dip - dim).abs() / (dip + dim).replace(0, float("nan"))
                adx_s = dx.ewm(span=n_adx, adjust=False).mean()
                adx300_v = float(adx_s.iloc[-1]) if not pd.isna(adx_s.iloc[-1]) else None
                if adx300_v is not None and len(adx_s.dropna()) >= 10:
                    adx_recent = adx_s.dropna().iloc[-10:]
                    adx300_spiral = bool(adx_recent.iloc[-1] > adx_recent.iloc[0] and adx300_v > 20)

    # ── Weekly data ─────────────────────────────────────────────────────────
    wd = weekly_data.get(code)
    wk_vr2_v = None
    if wd is not None and len(wd) >= 3:
        wc = col(wd, "close"); wv = col(wd, "volume")
        if wc is not None and wv is not None:
            wvr = vr_s(wc, wv, 2)
            wk_vr2_v = float(wvr.iloc[-1]) if not pd.isna(wvr.iloc[-1]) else None

    # ── Monthly data ─────────────────────────────────────────────────────────
    md = monthly_data.get(code)
    mo_di1_v = mo_rsi4_v = mo_vr2_v = None
    if md is not None and len(md) >= 5:
        mc = col(md, "close"); mh = col(md, "high")
        ml = col(md, "low");   mv = col(md, "volume")
        if mc is not None and mh is not None and ml is not None:
            di  = plus_di_s(mh, ml, mc, 1)
            rs4 = rsi_s(mc, 4)
            mo_di1_v  = float(di.iloc[-1])  if not pd.isna(di.iloc[-1])  else None
            mo_rsi4_v = float(rs4.iloc[-1]) if not pd.isna(rs4.iloc[-1]) else None
        if mc is not None and mv is not None:
            mvr = vr_s(mc, mv, 2)
            mo_vr2_v  = float(mvr.iloc[-1]) if not pd.isna(mvr.iloc[-1]) else None

    # ── Signal evaluation ────────────────────────────────────────────────────
    s1_ok = mo_di1_v  is not None and mo_di1_v  > 50
    s2_ok = mo_rsi4_v is not None and mo_rsi4_v > 77
    s3_ok = wr50_v    is not None and wr50_v    < 20
    s4_ok = rsi60_v   is not None and rsi60_v   > 57
    s5_ok = wk_vr2_v  is not None and wk_vr2_v  >= 150
    s6_ok = mo_vr2_v  is not None and mo_vr2_v  >= 150
    s7_ok = bool(dif210_spiral)   # DIF210螺旋攻擊
    s8_ok = bool(adx300_spiral)   # ADX300螺旋

    bull_signs = sum([s1_ok, s2_ok, s3_ok, s4_ok, s5_ok, s6_ok])
    strategy_signs = sum([s1_ok, s2_ok, s3_ok, s4_ok, s5_ok, s6_ok, s7_ok, s8_ok])
    has_price  = wr50_v is not None

    if   bull_signs >= 5 and s3_ok and s4_ok: verdict = "🚀 強力買進"
    elif bull_signs >= 4 and (s3_ok or s4_ok): verdict = "📈 買進"
    elif bull_signs >= 5:                       verdict = "📈 強勢技術面"
    elif bull_signs >= 3:                       verdict = "📊 留意"
    elif (wr50_v or 100) > 80 or (rsi60_v or 50) < 35: verdict = "📉 弱勢"
    else:                                       verdict = "⬛ 中性"

    results.append({
        "code": code, "name": name, "market": market, "sector": sector,
        "close":     round(close_v, 2)  if close_v  is not None else None,
        # Technical signals
        "mo_di1":    round(mo_di1_v, 1)  if mo_di1_v  is not None else None,
        "mo_rsi4":   round(mo_rsi4_v, 1) if mo_rsi4_v is not None else None,
        "wr50":      round(wr50_v, 1)    if wr50_v    is not None else None,
        "rsi60":     round(rsi60_v, 1)   if rsi60_v   is not None else None,
        "wk_vr2":    round(wk_vr2_v, 0)  if wk_vr2_v  is not None else None,
        "mo_vr2":    round(mo_vr2_v, 0)  if mo_vr2_v  is not None else None,
        # DIF210 / ADX300 strategy signals
        "dif210":    round(dif210_v, 4)  if dif210_v  is not None else None,
        "adx300":    round(adx300_v, 1)  if adx300_v  is not None else None,
        # Signal flags (S1-S6 original, S7=DIF210螺旋, S8=ADX300螺旋)
        "s1_ok": s1_ok, "s2_ok": s2_ok, "s3_ok": s3_ok,
        "s4_ok": s4_ok, "s5_ok": s5_ok, "s6_ok": s6_ok,
        "s7_ok": s7_ok, "s8_ok": s8_ok,
        "bull_signs": bull_signs, "strategy_signs": strategy_signs, "has_price": has_price,
        "verdict": verdict,
        # Fundamentals (for detail panel reference)
        "rev_yoy":    round(rev_yoy, 1) if rev_yoy is not None else None,
        "eps_q1":     round(eps_q1, 2)  if eps_q1  is not None else None,
        "gross_margin": round(gm, 1)    if gm      is not None else None,
        "op_margin":  round(om, 1)      if om      is not None else None,
        "pe":  round(pe, 1) if pe else None,
        "pb":  round(pb, 2) if pb else None,
        "yield": round(dy, 1) if dy else None,
        "quick_score": quick_score,
    })

results.sort(key=lambda x: -(x["bull_signs"] * 10 + (1 if x["has_price"] else 0)))

bull_all   = [r for r in results if r["bull_signs"] >= 3]
weak       = [r for r in results if "📉" in r["verdict"]]
with_price = [r for r in results if r["has_price"]]

# Sector summary
from collections import defaultdict
sec_dna = defaultdict(list)
for r in results:
    sec_dna[r.get("sector") or "其他"].append(r)
sector_summary = []
for sec, stocks in sec_dna.items():
    avg_bs   = sum(s["bull_signs"] for s in stocks) / len(stocks)
    bull_pct = sum(1 for s in stocks if s["bull_signs"] >= 3) / len(stocks) * 100
    sector_summary.append({"sector": sec, "count": len(stocks),
                            "avg_bull_signs": round(avg_bs, 2),
                            "bull_pct": round(bull_pct, 1)})
sector_summary.sort(key=lambda x: -x["avg_bull_signs"])

print(f"\n  === DNA Results (6-signal technical) ===")
print(f"  Total: {len(results)} | With price: {len(with_price)}")
print(f"  Bull (3+ signals): {len(bull_all)} | Weak: {len(weak)}")
print(f"\n  Top 10:")
for r in results[:10]:
    print(f"    {r['code']} [{r['market']}] {r['name'][:8]:<10} "
          f"bull={r['bull_signs']} di1={r['mo_di1']} rsi4={r['mo_rsi4']} "
          f"wr={r['wr50']} rsi60={r['rsi60']} wkvr={r['wk_vr2']} movr={r['mo_vr2']} "
          f"{r['verdict']}")

# ── Build series_map for stocks with bull_signs >= 3 (for chart rendering) ────
print(f"\n  Building series_map for {len(bull_all)} bull stocks...")
series_map = {}
bull_codes = {r["code"] for r in bull_all}

for c in companies:
    code = c["code"]
    if code not in bull_codes:
        continue

    dd = daily_data.get(code)
    md = monthly_data.get(code)

    if dd is None or len(dd) < 20:
        continue

    cm_d = {cx.lower(): cx for cx in dd.columns}
    dc_c = cm_d.get("close"); dh_c = cm_d.get("high")
    dl_c = cm_d.get("low");   do_c = cm_d.get("open")
    if not all([dc_c, dh_c, dl_c, do_c]):
        continue

    # Compute indicators on full series, then take tail for chart
    wr_full  = williams_r_s(dd[dh_c], dd[dl_c], dd[dc_c], 50)
    rsi_full = rsi_s(dd[dc_c], 60)

    dd_tail = dd.tail(60)
    wr_tail  = wr_full.tail(60)
    rsi_tail = rsi_full.tail(60)

    candles = []
    for i, idx in enumerate(dd_tail.index):
        try:
            o = float(dd_tail[do_c].iloc[i])
            h = float(dd_tail[dh_c].iloc[i])
            l = float(dd_tail[dl_c].iloc[i])
            c_ = float(dd_tail[dc_c].iloc[i])
            if any(pd.isna(x) for x in [o, h, l, c_]): continue
            candles.append([str(idx.date()), round(o,2), round(c_,2), round(l,2), round(h,2)])
        except: pass

    wr_pts  = [[str(idx.date()), round(float(v),1)] for idx, v in wr_tail.items() if not pd.isna(v)]
    rsi_pts = [[str(idx.date()), round(float(v),1)] for idx, v in rsi_tail.items() if not pd.isna(v)]

    entry = {"d": candles, "wr": wr_pts, "rsi60": rsi_pts}

    # Monthly: +DI(1) and RSI(4)
    if md is not None and len(md) >= 5:
        cm_m = {cx.lower(): cx for cx in md.columns}
        mc_c = cm_m.get("close"); mh_c = cm_m.get("high"); ml_c = cm_m.get("low")
        if mc_c and mh_c and ml_c:
            di_full   = plus_di_s(md[mh_c], md[ml_c], md[mc_c], 1)
            rsi4_full = rsi_s(md[mc_c], 4)
            md_tail   = md.tail(18)
            di_tail   = di_full.tail(18)
            rs4_tail  = rsi4_full.tail(18)

            m_close = [[str(idx.date())[:7], round(float(v),2)] for idx, v in md_tail[mc_c].items() if not pd.isna(v)]
            m_di    = [[str(idx.date())[:7], round(float(v),1)] for idx, v in di_tail.items() if not pd.isna(v)]
            m_rsi4  = [[str(idx.date())[:7], round(float(v),1)] for idx, v in rs4_tail.items() if not pd.isna(v)]
            entry["m_c"]    = m_close
            entry["m_di"]   = m_di
            entry["m_rsi4"] = m_rsi4

    series_map[code] = entry

print(f"  series_map: {len(series_map)} stocks")

out = {
    "generated":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    "data_date":   latest_date,
    "signals":     ["月+DI(1)>50", "月RSI(4)>77", "日W%R(50)<20", "日RSI(60)>57", "週VR(2)≥150", "月VR(2)≥150"],
    "total":       len(results),
    "with_price":  len(with_price),
    "bull_count":  len(bull_all),
    "weak_count":  len(weak),
    "sector_summary": sector_summary,
    "strong_bull": [r for r in results if r["bull_signs"] >= 5][:50],
    "bull":        [r for r in results if r["bull_signs"] == 3 or r["bull_signs"] == 4][:150],
    "weak":        weak[:50],
    "all_results": results,
    "series_map":  series_map,
}
(REPORT_DIR / "dna_full_market.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
sz = (REPORT_DIR / "dna_full_market.json").stat().st_size // 1024
print(f"\n  Saved dna_full_market.json ({sz} KB)")
print(f"[{datetime.now():%H:%M:%S}] Done")
