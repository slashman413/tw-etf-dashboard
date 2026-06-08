#!/usr/bin/env python3
"""
Iteration 24: AI/HPC Value Chain Analysis
No API calls — synthesizes composite_data.json + risk_data.json +
               price_targets.json + april_revenue.json

Maps Taiwan stocks across the AI infrastructure value chain:
  Layer 1 — Foundry:           TSMC (2330)
  Layer 2 — Packaging/Test:    ASE (3711), PSMC-adjacent
  Layer 3 — Memory:            Nanya Tech (2408), Winbond (2344), Macronix (2337)
  Layer 4 — IC Design:         MediaTek (2454), Realtek (2379), Novatek (3034),
                               Silergy (6415), Yageo passive (2327)
  Layer 5 — PCB/CCL:           Unimicron (3037), Elite PCB (2383)
  Layer 6 — Server/Systems:    Quanta (2382), Wiwynn (6669), Wistron (3231),
                               Gigabyte (2376), ASUS (2357), Pegatron (4938)
  Layer 7 — Network/Storage:   Realtek (2379), ASUS NW
  Layer 8 — Industrial/Edge:   Advantech (2395)
  Non-AI:  Traditional sectors — Financials, Cement, Shipping, Petrochemicals

Generates: AI_VALUE_CHAIN.md + ai_chain.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
riskdata  = json.loads((REPORT_DIR / "risk_data.json").read_text(encoding="utf-8"))
ptargets  = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
apr_data  = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# ── Value chain layer definitions ─────────────────────────────────────────────
CHAIN = {
    "L1_Foundry": {
        "label": "Layer 1 — 晶圓代工 (Foundry)",
        "desc": "最核心AI晶片製造層，台積電幾乎壟斷先進製程",
        "codes": ["2330"],
        "theme": "#1e40af",
    },
    "L2_Package": {
        "label": "Layer 2 — 封裝測試 (Packaging/Test)",
        "desc": "CoWoS先進封裝需求隨AI GPU爆增；ASE為最大封測廠",
        "codes": ["3711"],
        "theme": "#1d4ed8",
    },
    "L3_Memory": {
        "label": "Layer 3 — 記憶體 (Memory)",
        "desc": "HBM/DDR5 AI訓練需求驅動DRAM週期復甦",
        "codes": ["2408", "2344", "2337"],
        "theme": "#0891b2",
    },
    "L4_ICDesign": {
        "label": "Layer 4 — IC設計 (IC Design)",
        "desc": "AI加速晶片、網路IC、電源管理IC受益",
        "codes": ["2454", "2379", "3034", "6415", "2327"],
        "theme": "#0284c7",
    },
    "L5_PCB": {
        "label": "Layer 5 — PCB/基板 (PCB/Substrate)",
        "desc": "AI伺服器高密度基板需求強勁",
        "codes": ["3037", "2383"],
        "theme": "#0369a1",
    },
    "L6_Systems": {
        "label": "Layer 6 — 伺服器/系統 (Servers/Systems)",
        "desc": "雲端廠商AI基礎建設資本支出直接受益者",
        "codes": ["2382", "6669", "3231", "2376", "2357", "4938"],
        "theme": "#7c3aed",
    },
    "L7_Components": {
        "label": "Layer 7 — 關鍵零組件 (Components)",
        "desc": "散熱、光學、連接器等AI伺服器必需組件",
        "codes": ["3008", "2308", "2395"],
        "theme": "#6d28d9",
    },
    "L8_Telecom": {
        "label": "Layer 8 — 電信/網路基礎 (Telecom/Network)",
        "desc": "AI數據中心網路頻寬需求擴增受益",
        "codes": ["2412", "3045"],
        "theme": "#4338ca",
    },
    "Non_Financial": {
        "label": "金融股 (Financials)",
        "desc": "AI主題間接受益 — 企業放款增加；IFRS 17利多",
        "codes": ["2882", "2881", "2886", "2891", "2884", "2892", "2887", "2890",
                  "2883", "5880", "2801", "5876", "5871"],
        "theme": "#16a34a",
    },
    "Non_Cyclical": {
        "label": "傳統週期股 (Cyclicals/Non-AI)",
        "desc": "石化、鋼鐵、航運、水泥 — 與AI主題關聯性低",
        "codes": ["1301", "1303", "2002", "2603", "2609", "2615", "1101", "1102",
                  "1216", "2207"],
        "theme": "#64748b",
    },
}

# Build master lookups
comp_map   = {s["code"]: s for s in composite}
risk_map   = {s["code"]: s for s in riskdata["all_stocks"]}
target_map = {t["code"]: t for t in ptargets["targets"]}
apr_map    = {r["code"]: r for r in apr_data["all_results"]}
name_map   = {**{s["code"]: s["name"] for s in composite},
              **{s["code"]: s["name"] for s in expansion}}

def get_stock(code):
    s  = comp_map.get(code, {})
    r  = risk_map.get(code, {})
    t  = target_map.get(code, {})
    a  = apr_map.get(code, {})
    return {
        "code":     code,
        "name":     name_map.get(code, code),
        "score":    s.get("score"),
        "verdict":  s.get("verdict", "—"),
        "fwd_pe":   sf(s.get("fwd_pe")),
        "pb":       sf(s.get("pb")),
        "div":      sf(s.get("div_yield")),
        "rev_yoy":  sf(s.get("rev_yoy")),
        "op_margin":sf(s.get("op_margin")),
        "price":    sf(s.get("price")),
        "risk":     r.get("risk", 30),
        "ra_score": r.get("ra_score"),
        "peg":      r.get("peg"),
        "upside":   sf(t.get("upside")),
        "target":   sf(t.get("target")),
        "cum_yoy":  a.get("cum_yoy"),
        "accel":    a.get("accel"),
    }

# Build chain data
chain_data = {}
for layer_id, layer_info in CHAIN.items():
    stocks = [get_stock(c) for c in layer_info["codes"]]
    stocks = [s for s in stocks if s["score"] is not None or s["code"] in
              [x["code"] for x in expansion]]

    # Layer aggregates (only scored stocks)
    scored = [s for s in stocks if s["score"] is not None]
    avg_score  = sum(s["score"] for s in scored) / len(scored) if scored else None
    avg_pe     = None
    pe_vals    = [s["fwd_pe"] for s in scored if s["fwd_pe"]]
    if pe_vals: avg_pe = sum(pe_vals) / len(pe_vals)
    avg_upside = None
    up_vals    = [s["upside"] for s in stocks if s["upside"]]
    if up_vals: avg_upside = sum(up_vals) / len(up_vals)
    avg_risk   = sum(s["risk"] for s in scored) / len(scored) if scored else None
    buy_count  = sum(1 for s in scored if s["verdict"] in ("STRONG BUY","BUY"))

    chain_data[layer_id] = {
        "label":     layer_info["label"],
        "desc":      layer_info["desc"],
        "theme":     layer_info["theme"],
        "stocks":    stocks,
        "avg_score": round(avg_score, 1) if avg_score else None,
        "avg_pe":    round(avg_pe, 1) if avg_pe else None,
        "avg_upside":round(avg_upside, 1) if avg_upside else None,
        "avg_risk":  round(avg_risk, 1) if avg_risk else None,
        "buy_count": buy_count,
        "n":         len(stocks),
    }

# ── Generate AI_VALUE_CHAIN.md ────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Taiwan AI/HPC Value Chain Analysis — {TODAY}",
    "*Mapping Taiwan ETF stocks across the global AI infrastructure supply chain*",
    "",
    "## Chain Overview",
    "",
    "```",
    "  Global AI Demand (NVIDIA/Meta/Google/Microsoft/AWS)",
    "       ↓",
    "  ┌─────────────────────────────────────────────────┐",
    "  │ L1: TSMC (2330) — Advanced Foundry              │ ← Most critical node",
    "  │ L2: ASE (3711) — CoWoS Packaging                │",
    "  │ L3: Nanya/Winbond/Macronix — Memory (DRAM/NOR)  │",
    "  │ L4: MediaTek/Realtek/Novatek — IC Design        │",
    "  │ L5: Unimicron/Elite PCB — Advanced Substrates   │",
    "  │ L6: Quanta/Wiwynn/Gigabyte/ASUS — AI Servers    │ ← Biggest revenue",
    "  │ L7: LARGAN/Delta/Advantech — Components/Edge    │",
    "  │ L8: Chunghwa/TWM — Network Infrastructure       │",
    "  └─────────────────────────────────────────────────┘",
    "       ↓",
    "  Enterprise/Cloud AI Deployment",
    "```",
    "",
    "---",
    "",
    "## Layer-by-Layer Comparison",
    "",
    "| Layer | Stocks | Avg Score | Avg Fwd P/E | Avg Upside | Avg Risk | BUY Count |",
    "|-------|--------|-----------|------------|-----------|---------|-----------|",
]

ai_layers = [k for k in CHAIN if k.startswith("L")]
for lid in ai_layers:
    d = chain_data[lid]
    lines.append(
        f"| {d['label'].split('—')[0].strip()} | {d['n']} | "
        f"**{fmt(d['avg_score'],1)}** | {fmt(d['avg_pe'],1,'','x')} | "
        f"{fmt(d['avg_upside'],1,'+' if (d['avg_upside'] or 0)>0 else '','')}% | "
        f"{fmt(d['avg_risk'],0)} | {d['buy_count']}/{d['n']} |"
    )

lines += ["", "---", ""]

# Detailed per-layer section
for lid in CHAIN:
    d = chain_data[lid]
    if not d["stocks"]: continue

    lines += [
        f"## {d['label']}",
        f"*{d['desc']}*",
        "",
        "| Code | Name | Score | Fwd P/E | Upside | Risk | Cum YoY | Verdict |",
        "|------|------|-------|---------|--------|------|---------|---------|",
    ]
    for s in d["stocks"]:
        score_str = str(s["score"]) if s["score"] else "—"
        lines.append(
            f"| **{s['code']}** | {s['name'].split()[0]} | {score_str} | "
            f"{fmt(s['fwd_pe'],1,'','x')} | "
            f"{fmt(s['upside'],1,'+' if (s['upside'] or 0)>0 else '','')}{'%' if s['upside'] else '—'} | "
            f"{s['risk']} | "
            f"{fmt(s['cum_yoy'],1,'+' if (s['cum_yoy'] or 0)>0 else '','')}{'%' if s['cum_yoy'] else '—'} | "
            f"{s['verdict']} |"
        )
    if d["avg_score"]:
        lines.append(
            f"| **平均** | — | **{fmt(d['avg_score'],1)}** | {fmt(d['avg_pe'],1,'','x')} | "
            f"{fmt(d['avg_upside'],1,'+' if (d['avg_upside'] or 0)>0 else '','')}% | "
            f"{fmt(d['avg_risk'],0)} | — | — |"
        )
    lines.append("")

# Best value by layer
lines += [
    "---",
    "",
    "## 投資策略: 哪層最具吸引力?",
    "",
    "| 評估維度 | 最佳層級 | 說明 |",
    "|---------|---------|------|",
]

# Find best layer by different metrics
ai_chain_data = {k: v for k,v in chain_data.items() if k.startswith("L")}

best_score  = max(ai_chain_data.items(), key=lambda x: x[1]["avg_score"] or 0)
best_upside = max(ai_chain_data.items(), key=lambda x: x[1]["avg_upside"] or -999)
best_risk   = min(ai_chain_data.items(), key=lambda x: x[1]["avg_risk"] or 999)
best_pe_val = min((x for x in ai_chain_data.items() if x[1]["avg_pe"]),
                  key=lambda x: x[1]["avg_pe"] or 999, default=None)

lines.append(f"| 最高平均綜合分 | {best_score[1]['label'].split('—')[0].strip()} | 分={best_score[1]['avg_score']:.1f} |")
lines.append(f"| 最大目標上漲空間 | {best_upside[1]['label'].split('—')[0].strip()} | 平均+{best_upside[1]['avg_upside']:.1f}% |")
lines.append(f"| 最低風險評分 | {best_risk[1]['label'].split('—')[0].strip()} | 風險={best_risk[1]['avg_risk']:.0f} |")
if best_pe_val:
    lines.append(f"| 最低估值(P/E) | {best_pe_val[1]['label'].split('—')[0].strip()} | P/E={best_pe_val[1]['avg_pe']:.1f}x |")

lines += [
    "",
    "## 鏈條投資觀點",
    "",
    "**高確定性選擇 (L1 Foundry):**",
    "台積電是AI算力的絕對瓶頸。任何AI需求增加必然流經台積電。",
    "估值偏高但護城河無與倫比。適合長期核心持倉。",
    "",
    "**最高彈性 (L3 Memory):**",
    "南亞科(2408)累計YoY +624% — DRAM週期復甦力道最強。",
    "目標價+156%，PEG極低，但週期性高。適合積極型投資人。",
    "",
    "**最大收入規模 (L6 Systems):**",
    "廣達、緯穎等AI伺服器廠直接吃到雲端資本支出。",
    "毛利率薄，但收入成長可見度高。",
    "",
    "**被低估的層級 (L7 Components):**",
    "大立光(3008)光學+Delta台達電 — AI伺服器散熱需求被市場忽視。",
    "",
    "**避開 (L4 IC Design — MediaTek):**",
    "聯發科(2454)累計YoY為負，手機市場疲弱抵銷AI受益。",
    "Novatek面板IC需求弱。本層分化明顯，需個股篩選。",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 24*",
]

(REPORT_DIR / "AI_VALUE_CHAIN.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save JSON ──────────────────────────────────────────────────────────────────
chain_json = {
    "date": TODAY,
    "layers": [
        {
            "id": lid,
            "label": d["label"],
            "desc": d["desc"],
            "theme": d["theme"],
            "avg_score": d["avg_score"],
            "avg_pe": d["avg_pe"],
            "avg_upside": d["avg_upside"],
            "avg_risk": d["avg_risk"],
            "buy_count": d["buy_count"],
            "n": d["n"],
            "stocks": [{"code":s["code"],"name":s["name"].split()[0],
                        "score":s["score"],"fwd_pe":s["fwd_pe"],
                        "upside":s["upside"],"risk":s["risk"],
                        "cum_yoy":s["cum_yoy"],"verdict":s["verdict"]}
                       for s in d["stocks"]],
        }
        for lid, d in chain_data.items()
    ],
}
(REPORT_DIR / "ai_chain.json").write_text(
    json.dumps(chain_json, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ AI_VALUE_CHAIN.md + ai_chain.json")
print(f"\n  AI Value Chain Layer Summary:")
for lid in ai_layers:
    d = chain_data[lid]
    short = d["label"].split("—")[0].strip()
    print(f"  {short:20s} n={d['n']}  score={fmt(d['avg_score'],1):5s}  "
          f"pe={fmt(d['avg_pe'],1,'','x'):7s}  upside={fmt(d['avg_upside'],1,'+','%'):8s}  "
          f"risk={fmt(d['avg_risk'],0):4s}  buys={d['buy_count']}/{d['n']}")

print(f"\n  Best layer by metric:")
print(f"    Highest score:  {best_score[1]['label'].split('—')[0].strip()} ({best_score[1]['avg_score']:.1f})")
print(f"    Best upside:    {best_upside[1]['label'].split('—')[0].strip()} (+{best_upside[1]['avg_upside']:.1f}%)")
print(f"    Lowest risk:    {best_risk[1]['label'].split('—')[0].strip()} ({best_risk[1]['avg_risk']:.0f})")
