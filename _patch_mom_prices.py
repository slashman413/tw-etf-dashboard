"""Patch price_momentum.json with fresh yfinance prices for OTC/missing stocks."""
import json, time
import yfinance as yf
from pathlib import Path

rd = Path("reports") / sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
mom_path = rd / "price_momentum.json"
mom = json.loads(mom_path.read_text(encoding="utf-8"))
mom_map = {m["code"]: m for m in mom.get("all_momentum", [])}

missing_codes = [code for code, m in mom_map.items()
                 if m.get("pct_vs_prior") is None and m.get("close") is None]
print(f"Patching {len(missing_codes)} missing stocks via yfinance: {missing_codes}")

comp = json.loads((rd / "composite_data.json").read_text(encoding="utf-8"))
exp  = json.loads((rd / "expansion_stocks.json").read_text(encoding="utf-8"))
prior_map = {}
for s in comp + exp:
    try:
        v = float(str(s.get("price", "0")).replace(",", ""))
        if v > 0:
            prior_map[s["code"]] = v
    except:
        pass

updated = 0
for code in missing_codes:
    for suffix in [".TW", ".TWO"]:
        try:
            df = yf.Ticker(f"{code}{suffix}").history(period="5d", interval="1d", auto_adjust=True)
            if not df.empty:
                close = float(df["Close"].iloc[-1])
                prior = prior_map.get(code)
                pct = round((close / prior - 1) * 100, 1) if prior and prior > 0 else None
                if code in mom_map:
                    mom_map[code]["close"] = close
                    mom_map[code]["pct_vs_prior"] = pct
                    if pct is not None:
                        if pct > 10:
                            mom_map[code]["signal"] = "UP"
                        elif pct < -8:
                            mom_map[code]["signal"] = "DOWN"
                updated += 1
                print(f"  {code}{suffix}: close={close:.1f} pct={pct}")
                break
        except Exception as e:
            pass
    time.sleep(0.2)

print(f"Updated {updated}/{len(missing_codes)} stocks")
mom["all_momentum"] = list(mom_map.values())
mom_path.write_text(json.dumps(mom, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved {mom_path}")
