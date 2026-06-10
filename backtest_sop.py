#!/usr/bin/env python3
"""
SOP Backtest Engine — DNA 大飆股 完整進出場回測
Entry:  TAIEX N2 standby zone + daily W%R(50)<20 + RSI(60)>57 + MACD bullish
Exit:   Monthly W%R(3)>50 → 100% exit | Monthly RSI(4)<77 → 50% exit (×2)
Period: ~3 years  Capital: 1M TWD + 2M TWD
Output: backtest_sop_results.json
"""

import json, math, warnings
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
warnings.filterwarnings('ignore')

# ── Config ───────────────────────────────────────────────────────────────────
START_DATE   = "2023-01-01"
END_DATE     = datetime.now().strftime("%Y-%m-%d")
INIT_CAP_1M  = 1_000_000
INIT_CAP_2M  = 2_000_000
ALLOC_PCT    = 0.20     # 20% per position
MAX_POSITIONS= 5        # max simultaneous holdings
HOLD_MIN     = 15       # min holding days before exit check
N2_PERIOD    = 42       # 2-month rolling window (approx. 42 trading days)
OTC_CODES    = {"6488"}

TODAY = sorted([d.name for d in Path("reports").iterdir()
                if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

comp = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
ALL_CODES = sorted(name_map.keys())
TICKERS   = [f"{c}.TWO" if c in OTC_CODES else f"{c}.TW" for c in ALL_CODES]

print(f"[SOP Backtest] {START_DATE} → {END_DATE}")
print(f"[SOP Backtest] {len(ALL_CODES)} stocks | Alloc:{ALLOC_PCT*100:.0f}% | Max:{MAX_POSITIONS} positions")

import yfinance as yf

# ── Indicator functions ───────────────────────────────────────────────────────
def _wr(h, lo, c, n):
    hh = h.rolling(n).max(); ll = lo.rolling(n).min()
    return (hh - c) / (hh - ll + 1e-10) * 100   # 0=top(overbought), 100=bottom(oversold)

def _rsi(c, n):
    d  = c.diff()
    ag = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    al = (-d).clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100 / (1 + ag / al.replace(0, np.nan))

def _macd(c, fast=12, slow=26, sig=9):
    dif = c.ewm(span=fast, adjust=False).mean() - c.ewm(span=slow, adjust=False).mean()
    return dif, dif.ewm(span=sig, adjust=False).mean()

def _monthly_rsi(close, n=4):
    return _rsi(close.resample('ME').last(), n)

def _monthly_wr(hi, lo, cl, n=3):
    return _wr(hi.resample('ME').max(), lo.resample('ME').min(), cl.resample('ME').last(), n)

# ── Download TAIEX ────────────────────────────────────────────────────────────
print("Downloading TAIEX ^TWII…")
tw_raw   = yf.download("^TWII", start="2022-06-01", end=END_DATE,
                        auto_adjust=True, progress=False)
tw_close = tw_raw["Close"].squeeze().dropna()
tw_high  = tw_raw["High"].squeeze().dropna()
tw_low   = tw_raw["Low"].squeeze().dropna()

# N2: 2-month rolling midpoint; standby zone = close <= N2
tw_n2       = (tw_high.rolling(N2_PERIOD).max() + tw_low.rolling(N2_PERIOD).min()) / 2
tw_in_n2    = tw_close <= tw_n2            # True = market in standby zone
tw_wr50     = _wr(tw_high, tw_low, tw_close, 50)
tw_oversold = tw_wr50 > 70                 # TAIEX oversold (W%R>70 on our 0-100 scale)
# Market OK: either in N2 standby or TAIEX itself oversold (crash-buy context)
tw_mkt_ok   = tw_in_n2 | tw_oversold

# ── Download stocks ───────────────────────────────────────────────────────────
print(f"Downloading {len(TICKERS)} stocks (period 3y+)…")
raw = yf.download(TICKERS, start="2022-06-01", end=END_DATE,
                  auto_adjust=True, progress=False, group_by="ticker")

# ── Compute per-stock signals ─────────────────────────────────────────────────
print("Computing indicators…")
sdata = {}   # code → DataFrame

for code, ticker in zip(ALL_CODES, TICKERS):
    try:
        df = raw.xs(ticker, level=0, axis=1).dropna(how="all")
    except Exception:
        continue
    if len(df) < 80:
        continue
    cm = {c.lower(): c for c in df.columns}
    try:
        c  = df[cm.get("close","Close")]
        h  = df[cm.get("high","High")]
        lo = df[cm.get("low","Low")]
    except Exception:
        continue

    wr50    = _wr(h, lo, c, 50)
    rsi60   = _rsi(c, 60)
    dif, sg = _macd(c)

    # Monthly signals (forward-filled onto daily index)
    mo_rsi4 = _monthly_rsi(c).reindex(c.index, method='ffill')
    mo_wr3  = _monthly_wr(h, lo, c).reindex(c.index, method='ffill')

    # Entry conditions
    s3_entry   = wr50 < 20                           # daily W%R oversold top
    s4_entry   = rsi60 > 57                           # daily RSI momentum
    macd_bull  = dif > sg                             # MACD golden cross

    # Exit signals
    # Full exit: price in lower half of 3-month range (weakening)
    exit_full  = mo_wr3 > 50
    # Partial exit: monthly RSI4 turned bearish (crossed below 77)
    # We track this as the current monthly RSI < 77 (was above on entry)
    exit_half  = mo_rsi4 < 77

    sdata[code] = pd.DataFrame({
        'c': c, 'h': h, 'lo': lo,
        'wr50': wr50, 'rsi60': rsi60,
        'dif': dif,   'macd_sg': sg,
        'mo_rsi4': mo_rsi4, 'mo_wr3': mo_wr3,
        's3': s3_entry, 's4': s4_entry, 'mb': macd_bull,
        'xf': exit_full, 'xh': exit_half,
    })

print(f"  Signals ready for {len(sdata)} stocks")

# ── Backtest ──────────────────────────────────────────────────────────────────
def _safe(v):
    try:
        f = float(v)
        return None if math.isnan(f) or math.isinf(f) else f
    except Exception:
        return None

def run(init_cap):
    cash   = float(init_cap)
    pos    = {}   # code → {shares, entry_price, entry_date, partial_done, entry_mo_rsi4}
    equity = []
    trades = []

    trade_dates = tw_close.loc[START_DATE:].index

    for dt in trade_dates:
        # ── Daily portfolio value ─────────────────────────────────────────────
        pv = 0.0
        for code, p in pos.items():
            if code in sdata and dt in sdata[code].index:
                px = _safe(sdata[code].at[dt, 'c'])
                pv += p['shares'] * (px if px else p['entry_price'])
            else:
                pv += p['shares'] * p['entry_price']
        equity.append({'date': str(dt.date()), 'value': round(cash + pv)})

        # ── Exit logic ────────────────────────────────────────────────────────
        for code in list(pos.keys()):
            p = pos[code]
            if code not in sdata or dt not in sdata[code].index:
                continue
            px = _safe(sdata[code].at[dt, 'c'])
            if not px:
                continue
            days_held = (dt - p['entry_date']).days
            if days_held < HOLD_MIN:
                continue

            xf = bool(sdata[code].at[dt, 'xf'])   # monthly W%R > 50
            xh = bool(sdata[code].at[dt, 'xh'])    # monthly RSI4 < 77

            mo_rsi = _safe(sdata[code].at[dt, 'mo_rsi4'])

            # Full exit: monthly W%R(3) > 50 (price in lower half of 3-month range)
            if xf:
                pnl     = (px - p['entry_price']) * p['shares']
                pnl_pct = (px / p['entry_price'] - 1) * 100
                trades.append({
                    'code': code, 'name': name_map.get(code, code)[:6],
                    'entry_date': str(p['entry_date'].date()),
                    'entry_price': round(p['entry_price'], 2),
                    'exit_date': str(dt.date()),
                    'exit_price': round(px, 2),
                    'shares': p['shares'],
                    'pnl': round(pnl),
                    'pnl_pct': round(pnl_pct, 2),
                    'exit_reason': '月W%R(3)>50 全出',
                })
                cash += px * p['shares']
                del pos[code]

            # Partial exit (first): monthly RSI4 drops below 77 (was high at entry)
            elif xh and not p.get('partial_done') and mo_rsi is not None:
                # Only trigger if RSI was elevated at entry (proxy: entry_mo_rsi4 > 60)
                # and has now fallen below 77
                entry_rsi = p.get('entry_mo_rsi4', 0) or 0
                if entry_rsi >= 60 or days_held > 60:
                    sell_sh = p['shares'] // 2
                    if sell_sh > 0:
                        pnl     = (px - p['entry_price']) * sell_sh
                        pnl_pct = (px / p['entry_price'] - 1) * 100
                        trades.append({
                            'code': code, 'name': name_map.get(code, code)[:6],
                            'entry_date': str(p['entry_date'].date()),
                            'entry_price': round(p['entry_price'], 2),
                            'exit_date': str(dt.date()),
                            'exit_price': round(px, 2),
                            'shares': sell_sh,
                            'pnl': round(pnl),
                            'pnl_pct': round(pnl_pct, 2),
                            'exit_reason': '月RSI(4)<77 減倉50%',
                        })
                        cash += px * sell_sh
                        pos[code]['shares'] -= sell_sh
                        pos[code]['partial_done'] = True

        # ── Entry logic ───────────────────────────────────────────────────────
        if len(pos) >= MAX_POSITIONS:
            continue

        if dt not in tw_mkt_ok.index:
            continue
        if not bool(tw_mkt_ok.loc[dt]):
            continue

        # Score candidates: all signals must pass
        candidates = []
        for code, df in sdata.items():
            if code in pos:
                continue
            if dt not in df.index:
                continue
            s3 = bool(df.at[dt, 's3'])
            s4 = bool(df.at[dt, 's4'])
            mb = bool(df.at[dt, 'mb'])
            if not (s3 and s4 and mb):
                continue
            rsi_v = _safe(df.at[dt, 'rsi60']) or 0
            mo_rsi = _safe(df.at[dt, 'mo_rsi4']) or 0
            score = rsi_v + mo_rsi * 0.5
            candidates.append((code, df.at[dt, 'c'], df.at[dt, 'mo_rsi4'], score))

        candidates.sort(key=lambda x: -x[3])

        for code, raw_px, raw_mo_rsi, _ in candidates[:2]:  # max 2 new entries/day
            if len(pos) >= MAX_POSITIONS:
                break
            px = _safe(raw_px)
            if not px or px <= 0:
                continue

            alloc  = init_cap * ALLOC_PCT
            budget = min(alloc, cash * 0.95)
            if budget < px:
                continue

            # Use fractional shares for backtest realism
            shares = int(budget / px)
            if shares == 0:
                continue

            cost = shares * px
            cash -= cost
            mo_rsi_now = _safe(raw_mo_rsi) or 0
            pos[code] = {
                'shares': shares,
                'entry_price': px,
                'entry_date': dt,
                'partial_done': False,
                'entry_mo_rsi4': mo_rsi_now,
            }

    # ── Close remaining positions at last available price ─────────────────────
    last_dt = trade_dates[-1]
    for code, p in list(pos.items()):
        px = None
        if code in sdata and last_dt in sdata[code].index:
            px = _safe(sdata[code].at[last_dt, 'c'])
        if not px:
            px = p['entry_price']
        pnl     = (px - p['entry_price']) * p['shares']
        pnl_pct = (px / p['entry_price'] - 1) * 100
        trades.append({
            'code': code, 'name': name_map.get(code, code)[:6],
            'entry_date': str(p['entry_date'].date()),
            'entry_price': round(p['entry_price'], 2),
            'exit_date': str(last_dt.date()) + '(持倉中)',
            'exit_price': round(px, 2),
            'shares': p['shares'],
            'pnl': round(pnl),
            'pnl_pct': round(pnl_pct, 2),
            'exit_reason': '期末持倉',
        })
        cash += px * p['shares']

    # ── Statistics ────────────────────────────────────────────────────────────
    final_val   = cash
    total_ret   = (final_val / init_cap - 1) * 100
    years       = (pd.Timestamp(END_DATE) - pd.Timestamp(START_DATE)).days / 365.25
    ann_ret     = ((final_val / init_cap) ** (1 / years) - 1) * 100 if years > 0 else 0

    vals = [e['value'] for e in equity]
    peak = init_cap; max_dd = 0.0
    for v in vals:
        peak = max(peak, v)
        dd   = (peak - v) / peak * 100
        max_dd = max(max_dd, dd)

    closed = [t for t in trades if '持倉' not in t['exit_reason']]
    wins   = [t for t in closed if t['pnl_pct'] > 0]
    losses = [t for t in closed if t['pnl_pct'] <= 0]
    win_rt = len(wins) / len(closed) * 100 if closed else 0
    avg_w  = sum(t['pnl_pct'] for t in wins)   / len(wins)   if wins   else 0
    avg_l  = sum(t['pnl_pct'] for t in losses) / len(losses) if losses else 0
    pf     = round(-avg_w / avg_l, 2) if avg_l < 0 else None

    # Monthly returns
    eq_df  = pd.DataFrame(equity).set_index(pd.to_datetime([e['date'] for e in equity]))['value']
    mo_eq  = eq_df.resample('ME').last()
    mo_ret_pct = mo_eq.pct_change() * 100
    monthly_rets = [
        {'month': str(d)[:7], 'return': round(float(r), 2)}
        for d, r in mo_ret_pct.items() if not math.isnan(float(r))
    ]

    # Downsample equity curve to weekly for JSON size
    eq_weekly = eq_df.resample('W').last()
    equity_sampled = [
        {'date': str(d.date()), 'value': round(float(v))}
        for d, v in eq_weekly.items() if not math.isnan(float(v))
    ]

    return {
        'initial_capital': init_cap,
        'final_value': round(final_val),
        'total_return_pct': round(total_ret, 2),
        'annualized_return_pct': round(ann_ret, 2),
        'max_drawdown_pct': round(max_dd, 2),
        'total_trades': len(trades),
        'closed_trades': len(closed),
        'win_rate': round(win_rt, 1),
        'avg_win_pct': round(avg_w, 2),
        'avg_loss_pct': round(avg_l, 2),
        'profit_factor': pf,
        'equity_curve': equity_sampled,
        'trades': sorted(trades, key=lambda x: x['entry_date'], reverse=True)[:100],
        'monthly_returns': monthly_rets,
    }

print("Running 1M TWD backtest…")
r1 = run(INIT_CAP_1M)
print(f"  1M → {r1['total_return_pct']:+.1f}% | Ann {r1['annualized_return_pct']:+.1f}% | "
      f"MaxDD {r1['max_drawdown_pct']:.1f}% | Trades {r1['total_trades']} | Win {r1['win_rate']:.0f}%")

print("Running 2M TWD backtest…")
r2 = run(INIT_CAP_2M)
print(f"  2M → {r2['total_return_pct']:+.1f}% | Ann {r2['annualized_return_pct']:+.1f}% | "
      f"MaxDD {r2['max_drawdown_pct']:.1f}% | Trades {r2['total_trades']} | Win {r2['win_rate']:.0f}%")

# ── Gap analysis (static comparison) ─────────────────────────────────────────
gap_analysis = {
    "current_dna": {
        "signals": [
            {"id":"S1","name":"月DMI(+DI)>50","status":"✅ 已計算","note":"月線多頭排列確認"},
            {"id":"S2","name":"月RSI(4)>77","status":"✅ 已計算","note":"月線超買動能"},
            {"id":"S3","name":"日W%R(50)<20","status":"✅ 已計算","note":"日線短期回調後突破 (SOP成形條件)"},
            {"id":"S4","name":"日RSI(60)>57","status":"✅ 已計算","note":"日線動能確認"},
            {"id":"S5","name":"週VR(2)≥150","status":"✅ 已計算","note":"週線成交量放大"},
            {"id":"S6","name":"月VR(2)≥150","status":"✅ 已計算","note":"月線成交量放大"},
            {"id":"S7","name":"DIF210四箭頭向上","status":"❌ 未計算","note":"MACD(200/209/210)螺旋攻擊 — SOP核心進場信號"},
            {"id":"S8","name":"ADX300向上","status":"❌ 未計算","note":"趨勢加速確認"},
        ],
        "entry": "bull_signs≥2 + core_met≥1 (無大盤位階過濾)",
        "exit": "未定義明確出場條件",
    },
    "sop": {
        "step1_market": "大盤位階: DIF210底部 / 月黑6K / N2-100候補區 / 60分RSI60<34",
        "step2_stock":  "MACD DIF210四箭頭 + ADX300↑ + W%R50<20 + ≥3個DNA確認",
        "exit_individual": "月W%R(3)>50 → 100%出場；月RSI(4)<77 → 50%減倉×2",
        "exit_market":     "DIF210頂部 / 月6K-9K / 鐘擺效應(≥6000pt漲+極端背離) → 全出",
    },
    "gaps": [
        {"id":"G1","sev":"🔴 高","title":"缺大盤位階過濾",
         "desc":"現行系統無TAIEX N2候補區判斷，牛熊不分，可能在空頭中進場。本回測已補入N2過濾。"},
        {"id":"G2","sev":"🔴 高","title":"S7 DIF210未實作",
         "desc":"MACD(200/209/210)螺旋攻擊是SOP最核心的進場觸發，現系統顯示'計算中'但實際未產生信號。"},
        {"id":"G3","sev":"🔴 高","title":"S8 ADX300未實作",
         "desc":"ADX(300)向上是確認趨勢加速的必要條件，缺少時可能在盤整市場誤判進場。"},
        {"id":"G4","sev":"🔴 高","title":"缺出場機制",
         "desc":"現行儀表板無月W%R(3)>50全出或月RSI(4)<77減倉的自動提醒。持股無明確停利SOP。"},
        {"id":"G5","sev":"🟡 中","title":"S2月RSI(4)方向混淆",
         "desc":"S2=月RSI>77是進場動能確認；月RSI<77下穿才是出場信號。兩者方向相反，需拆分追蹤。"},
        {"id":"G6","sev":"🟡 中","title":"缺資金配置顯示",
         "desc":"SOP要求單倉不超過20%、最多5個倉位。現行系統無倉位管理規則提示。"},
    ],
    "matches": [
        {"signal":"S3: 日W%R(50)<20","compat":"完全符合","note":"SOP成形條件完全一致"},
        {"signal":"S4: 日RSI(60)>57","compat":"部分符合","note":"SOP用於確認，現系統同"},
        {"signal":"S1+S2+S5+S6 DNA確認","compat":"完全符合","note":"≥3個DNA確認的要求吻合"},
        {"signal":"月RSI高位監控","compat":"部分符合","note":"賣出面板已顯示月RSI>70個股，但缺下穿提醒"},
    ],
}

# ── Assemble output ───────────────────────────────────────────────────────────
output = {
    "generated":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "period":         f"{START_DATE} → {END_DATE}",
    "universe_size":  len(sdata),
    "entry_note":     "回測進場條件: TAIEX N2候補區(近2月低位) + 日W%R(50)<20 + 日RSI(60)>57 + MACD多頭",
    "exit_note":      "回測出場條件: 月W%R(3)>50全出 | 月RSI(4)<77(高位回落)減50%×2",
    "disclaimer":     "DIF210/ADX300以標準MACD(12,26,9)+RSI趨勢代替; 月線以交易日月末計算; 回測不含交易成本及滑點",
    "result_1m":      r1,
    "result_2m":      r2,
    "gap_analysis":   gap_analysis,
}

out_path = REPORT_DIR / "backtest_sop_results.json"
out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ backtest_sop_results.json saved → {out_path}")
