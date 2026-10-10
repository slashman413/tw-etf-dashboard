"""Read/patch the `const NAME = {...}` JSON blocks embedded in dashboard.html.

Pure string-in/string-out: callers pass fetched prices/valuations, today's date and a
timestamp, so this runs identically in CI, locally, or in a test.
"""
import json
import re

from twetf.analyzers import indicators as ind


def extract_const(html, name):
    m = f"const {name}"
    idx = html.find(m)
    if idx < 0: return None
    eq = html.find("=", idx + len(m)) + 1
    while html[eq] == " ": eq += 1
    obj, _ = json.JSONDecoder().raw_decode(html, eq)
    return obj

def patch_const(html, name, obj):
    m = f"const {name}"
    idx = html.find(m)
    if idx < 0:
        print(f"  WARNING: const {name} not found"); return html
    eq = html.find("=", idx + len(m)) + 1
    while html[eq] == " ": eq += 1
    try:
        _, length = json.JSONDecoder().raw_decode(html, eq)
    except Exception as e:
        print(f"  WARNING: parse {name}: {e}"); return html
    # raw_decode returns absolute end position, not relative length
    return html[:eq] + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + html[length:]


def patch_momentum(html, prices, data_date, today, stamp):
    mom = extract_const(html, "MOMENTUM")
    all_mom = mom.get("all_momentum", [])
    updated = 0
    for e in all_mom:
        p = prices.get(e.get("code", ""))
        if not p: continue
        e["close"] = p["close"]; e["high"] = p["high"]
        e["low"]   = p["low"];   e["volume"] = p["volume"]
        prior = e.get("prior_price") or p["close"]
        if prior and prior > 0:
            e["pct_vs_prior"] = round((p["close"]/prior - 1)*100, 1)
        ma30 = e.get("ma30")
        if ma30 and ma30 > 0:
            e["pct_vs_ma"] = round((p["close"]/ma30 - 1)*100, 1)
        if p["high"] > p["low"]:
            e["intraday_pct"] = round((p["close"]-p["low"])/(p["high"]-p["low"])*100, 1)
        pct = e.get("pct_vs_prior", 0) or 0
        pma = e.get("pct_vs_ma", 0) or 0
        if pct > 20 and pma > 5:    e["signal"] = "STRONG_UP"
        elif pct > 10:              e["signal"] = "UP"
        elif pct < -15 and pma < -5: e["signal"] = "STRONG_DOWN"
        elif pct < -8:              e["signal"] = "DOWN"
        else:                       e["signal"] = "NEUTRAL"
        updated += 1
    mom["date"] = today; mom["data_date"] = data_date; mom["fetch_ts"] = stamp
    valid = [m for m in all_mom if m.get("pct_vs_prior") is not None]
    sc = {s: 0 for s in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}
    for m in valid: sc[m.get("signal","NEUTRAL")] += 1
    mom["signal_counts"] = sc
    mom["top_gainers"] = sorted(valid, key=lambda x: -(x.get("pct_vs_prior",0) or 0))[:10]
    mom["top_losers"]  = sorted(valid, key=lambda x:  (x.get("pct_vs_prior",0) or 0))[:10]
    print(f"  MOMENTUM: {updated} stocks | {sc}")
    return patch_const(html, "MOMENTUM", mom)

def patch_movers(html):
    """Re-derive from already-patched MOMENTUM."""
    mom = extract_const(html, "MOMENTUM")
    valid = [m for m in mom.get("all_momentum", []) if m.get("pct_vs_prior") is not None]
    top6  = sorted(valid, key=lambda x: abs(x.get("pct_vs_prior",0) or 0), reverse=True)[:6]
    movers = [{"code": m["code"], "name": m.get("name",""), "chg": m.get("pct_vs_prior",0), "score": m.get("score",0)} for m in top6]
    print(f"  MOVERS: {len(movers)} entries")
    return patch_const(html, "MOVERS", movers)

def patch_marefresh(html, series_map, prices, data_date, today, stamp):
    ma = extract_const(html, "MAREFRESH")
    all_results = ma.get("all_results", [])
    above, below, s_above, s_below = [], [], [], []
    for e in all_results:
        code = e.get("code", "")
        p = prices.get(code)
        closes = ind.closes(series_map, code, 35)
        if p: e["close"] = p["close"]
        close = e.get("close", 0) or 0
        if not close: continue
        if len(closes) >= 10:
            ma30 = ind.ma(closes, 30)
            e["ma30"] = round(ma30, 2)
        ma30_v = e.get("ma30", 0) or 0
        if ma30_v > 0:
            pct = round((close / ma30_v - 1) * 100, 2)
            e["pct_vs_ma"] = pct
            if pct >= 0:
                above.append(e)
                if pct >= 5: s_above.append(e)
            else:
                below.append(e)
                if pct <= -5: s_below.append(e)
    ma["date"] = today; ma["data_date"] = data_date; ma["fetch_ts"] = stamp
    ma["above_ma"]     = len(above);   ma["below_ma"]     = len(below)
    ma["strong_above"] = len(s_above); ma["strong_below"] = len(s_below)
    ma["above_list"]   = sorted(above, key=lambda x: -(x.get("pct_vs_ma",0) or 0))
    ma["below_list"]   = sorted(below, key=lambda x:  (x.get("pct_vs_ma",0) or 0))
    ma["all_results"]  = all_results
    print(f"  MAREFRESH: above={len(above)} below={len(below)} | s_above={len(s_above)} s_below={len(s_below)}")
    return patch_const(html, "MAREFRESH", ma)

def patch_dnasignals(html, series_map, prices, data_date, today, stamp):
    dna = extract_const(html, "DNASIGNALS")
    for s in dna.get("all_signals", []):
        code = s.get("code", "")
        p = prices.get(code)
        if p:
            s["close_now"] = p["close"]
            s["close"]     = p["close"]
            s["data_date"] = data_date
        ser = ind.series(series_map, code)
        if len(ser) >= 15:
            wr = ind.williams_r(ser, min(50, len(ser)))
            s["s3_wr50"] = wr
            s["s3_ok"]   = wr <= -15   # not in overbought zone
        if len(ser) >= 20:
            closes = [r[2] for r in ser]
            rsi = ind.rsi(closes, 14)
            s["s4_rsi60"] = rsi
            s["s4_ok"]    = 40 <= rsi <= 82   # trending but not extreme overbought
        ok_keys = [k for k in s if k.endswith("_ok")]
        s["bull_signs"] = sum(1 for k in ok_keys if s.get(k))
        core = sum(1 for k in ["s1_ok","s2_ok","s3_ok","s4_ok"] if s.get(k))
        s["core_met"] = core
        total = s["bull_signs"]
        if total >= 7:   s["verdict"] = "STRONG_BULL"
        elif total >= 5: s["verdict"] = "BULL"
        elif total >= 3: s["verdict"] = "WATCH"
        else:            s["verdict"] = "NEUTRAL"
    sigs = dna.get("all_signals", [])
    dna["date"]        = today
    dna["data_date"]   = data_date
    dna["fetch_ts"]    = stamp
    dna["strong_bull"] = sum(1 for s in sigs if s.get("verdict") == "STRONG_BULL")
    dna["bull"]        = sum(1 for s in sigs if s.get("verdict") == "BULL")
    dna["bear"]        = sum(1 for s in sigs if s.get("verdict") in ("WATCH","NEUTRAL"))
    print(f"  DNASIGNALS: strong_bull={dna['strong_bull']} bull={dna['bull']} bear={dna['bear']}")
    return patch_const(html, "DNASIGNALS", dna)

def patch_granddata(html, series_map, prices, data_date, today, stamp):
    gd = extract_const(html, "GRANDDATA")
    for e in gd.get("all_ranked", []):
        code = e.get("code", "")
        p = prices.get(code)
        if not p: continue
        closes = ind.closes(series_map, code, 25)
        if len(closes) >= 10:
            ma20 = ind.ma(closes, 20)
            if ma20 > 0:
                pct = (p["close"] / ma20 - 1) * 100
                # mom_pts: 0-25 scale; 0% deviation → 12.5 pts; ±20% → 0 or 25
                mom = max(0.0, min(25.0, 12.5 + pct * 0.625))
                e["mom_pts"] = round(mom, 1)
                e["grand"] = round(
                    (e.get("fund_pts", 0) or 0) +
                    (e.get("tech_pts", 0) or 0) +
                    (e.get("val_pts",  0) or 0) +
                    mom, 1
                )
    ranked = gd.get("all_ranked", [])
    gd["date"]      = today
    gd["data_date"] = data_date
    gd["fetch_ts"]  = stamp
    gd["all_ranked"]       = sorted(ranked, key=lambda x: -(x.get("grand", 0) or 0))
    gd["strong_buy"]       = sum(1 for r in ranked if (r.get("grand",     0) or 0) >= 80)
    gd["triple_confirmed"] = sum(1 for r in ranked if (r.get("bull_signs",0) or 0) >= 3
                                                   and (r.get("core_met",  0) or 0) >= 2)
    print(f"  GRANDDATA: strong_buy={gd['strong_buy']} triple={gd['triple_confirmed']}")
    return patch_const(html, "GRANDDATA", gd)

def _v_pts(pe, pb, div, is_fin):
    """Re-score the value dimension from fresh valuation (mirrors bwibbu_refresh)."""
    p = 0
    if is_fin:
        if pb and pb < 1.2:   p += 15
        elif pb and pb < 1.5: p += 8
        if div and div >= 5:   p += 15
        elif div and div >= 4: p += 10
        elif div and div >= 3: p += 5
    else:
        if pe and pe < 15:    p += 15
        elif pe and pe < 25:  p += 8
        if pb and pb < 1.5:   p += 8
        elif pb and pb < 2.5: p += 4
        if div and div >= 4:   p += 7
        elif div and div >= 2: p += 3
    return p

def patch_valuation(html, data_date, live, stamp):
    """Refresh the BWIBBU2 valuation const in-place from a live BWIBBU_ALL pull.

    Self-contained: reuses the frozen analysis-start baseline (pe_old/div_old/pb_old,
    name, is_fin) already embedded in BWIBBU2 — no dependency on reports/ files
    (which are gitignored). Only the current values + derived rankings + banner
    date are refreshed. Leaves the curated '重大估值信號' editorial table untouched.
    """
    B = extract_const(html, "BWIBBU2")
    if not B or not B.get("all_refreshed"):
        print("  VALUATION: BWIBBU2 not found or empty — skipping"); return html

    if not live:
        print("  VALUATION: no live data — keeping existing"); return html

    matched = 0
    for r in B["all_refreshed"]:
        q = live.get(r.get("code"))
        if not q: continue
        matched += 1
        is_fin = bool(r.get("is_fin"))
        pe_old, div_old, pb_old = r.get("pe_old"), r.get("div_old"), r.get("pb_old")
        pe_new, div_new, pb_new = q["pe"], q["div"], q["pb"]
        r["pe_new"], r["div_new"], r["pb_new"] = pe_new, div_new, pb_new
        r["delta_pe"]  = round(pe_new  - pe_old,  2) if pe_new  is not None and pe_old  is not None else None
        r["delta_div"] = round(div_new - div_old, 2) if div_new is not None and div_old is not None else None
        r["delta_pb"]  = round(pb_new  - pb_old,  2) if pb_new  is not None and pb_old  is not None else None
        r["v_pts_new"] = _v_pts(pe_new, pb_new, div_new, is_fin)

    ar = B["all_refreshed"]
    pe_changed = [r for r in ar if r.get("delta_pe") is not None]
    high_div   = sorted([r for r in ar if (r.get("div_new") or 0) >= 4.5],
                        key=lambda x: x.get("div_new") or 0, reverse=True)
    cheap_pe   = sorted([r for r in ar if r.get("pe_new") and r["pe_new"] < 15 and not r.get("is_fin")],
                        key=lambda x: x.get("pe_new") or 999)[:8]
    pe_expanded   = sorted(pe_changed, key=lambda x: x.get("delta_pe") or 0, reverse=True)[:5]
    pe_contracted = sorted(pe_changed, key=lambda x: x.get("delta_pe") or 0)[:5]

    def _nm(r): return (r.get("name") or r.get("code")).split()[0]
    B["data_date"]    = data_date or B.get("data_date")
    B["refresh_ts"]   = stamp
    B["total_matched"] = matched
    B["high_div_ge45"] = [{"code": r["code"], "name": _nm(r), "div_new": r["div_new"], "div_old": r["div_old"]} for r in high_div]
    B["cheap_pe_lt15"] = [{"code": r["code"], "name": _nm(r), "pe_new": r["pe_new"], "pe_old": r["pe_old"]} for r in cheap_pe]
    B["pe_expanded"]   = [{"code": r["code"], "name": _nm(r), "pe_old": r["pe_old"], "pe_new": r["pe_new"], "delta": r["delta_pe"]} for r in pe_expanded]
    B["pe_contracted"] = [{"code": r["code"], "name": _nm(r), "pe_old": r["pe_old"], "pe_new": r["pe_new"], "delta": r["delta_pe"]} for r in pe_contracted]

    html = patch_const(html, "BWIBBU2", B)

    # Refresh the banner date literal ("估值更新 — YYYY-MM-DD 收盤數據")
    greg = None
    dd = str(data_date or "")
    if len(dd) == 7 and dd[:3].isdigit():
        greg = f"{int(dd[:3])+1911}-{dd[3:5]}-{dd[5:7]}"
    if greg:
        html = re.sub(r"估值更新 — \d{4}-\d{2}-\d{2} 收盤數據",
                      f"估值更新 — {greg} 收盤數據", html)
    print(f"  VALUATION: matched={matched} high_div={len(high_div)} cheap_pe={len(cheap_pe)} data_date={data_date}")
    return html
