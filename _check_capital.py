import yfinance as yf
import json
from pathlib import Path

def williams_r(h, l, c, n):
    hh = h.rolling(n).max(); ll = l.rolling(n).min()
    return (hh - c) / (hh - ll + 1e-10) * -100  # 0=overbought, -100=oversold

# Capital allocation indices per strategy
targets = {
    "tw50":   {"name": "台灣50 (0050)",        "ticker": "0050.TW"},
    "tw006":  {"name": "富邦台灣50 (006208)",   "ticker": "006208.TW"},
    "fin":    {"name": "元大金融(0055)",         "ticker": "0055.TW"},
    "mid":    {"name": "中型100 ETF (0051)",    "ticker": "0051.TW"},
    "taiex":  {"name": "加權指數 (^TWII)",       "ticker": "^TWII"},
}

results = {}
for key, info in targets.items():
    tk = yf.Ticker(info["ticker"])
    df = tk.history(period="2y", interval="1mo", auto_adjust=True)
    if df.empty or len(df) < 4:
        print(f"  {info['name']}: no monthly data")
        continue
    wr = williams_r(df["High"], df["Low"], df["Close"], 3)
    val = float(wr.iloc[-1])
    close = float(df["Close"].iloc[-1])
    trend = "強勢" if val > -20 else "中性" if val > -50 else "弱勢/超賣"
    results[key] = {
        "name": info["name"],
        "ticker": info["ticker"],
        "mo_wr3": round(val, 1),
        "close": round(close, 2),
        "trend": trend,
        "date": str(df.index[-1].date())
    }
    print(f"  {info['name']}: 月W%R3={val:.1f} ({trend}) close={close:.2f}")

Path("taiex_capital.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Saved taiex_capital.json")
