#!/usr/bin/env python3
import json
from pathlib import Path
grand = json.loads(Path('reports/2026-06-06/grand_unified.json').read_text(encoding='utf-8'))
fin_codes = {'2883','2887','2882','2881','2357','2615','2376','2330','6669'}
print(f"{'代號':<6} {'名稱':<10} {'Grand':>7} {'Fund':>6} {'Tech':>6} {'Val':>6} {'Mom':>6} {'Bull':>5} {'Final'}")
print("-"*75)
for r in grand.get('all_ranked',[]):
    if r['code'] in fin_codes:
        print(f"{r['code']:<6} {r.get('name','?')[:8]:<10} {r.get('grand',0):>7.1f} "
              f"{r.get('fund_pts',0):>6.1f} {r.get('tech_pts',0):>6.1f} "
              f"{r.get('val_pts',0):>6.1f} {r.get('mom_pts',0):>6.1f} "
              f"{r.get('bull_signs',0):>5} {r.get('final','?')}")
