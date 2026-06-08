#!/usr/bin/env python3
import json
from pathlib import Path
for code in ['6669','2330','2357','1590','2882']:
    p = Path('reports/2026-06-06/stocks') / (code+'_report.json')
    d = json.loads(p.read_text(encoding='utf-8'))
    f = d.get('fundamental', {})
    name = d.get('name','?')[:8]
    print(f'{code} {name}: q1_eps={f.get("q1_eps")} trail_eps={f.get("trail_eps")} src={f.get("trail_eps_source")}')
