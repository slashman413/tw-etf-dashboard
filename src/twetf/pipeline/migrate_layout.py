"""Move a pre-src/ working copy's generated data into the new layout (one-time, local).

    python run.py migrate_layout            # dry run: show what would move
    python run.py migrate_layout --apply

reports/<date>/          -> data/reports/<date>/
taiex_*.json, expansion_ohlcv.json (untracked fresh copies at the root) -> data/raw/
Never overwrites: an existing destination is reported and skipped.
"""
import shutil
import sys

from twetf.paths import RAW_DIR, REPORTS_DIR, ROOT, SEED_DIR

apply = "--apply" in sys.argv
moves = []
legacy = ROOT / "reports"
if legacy.is_dir():
    moves += [(d, REPORTS_DIR / d.name) for d in sorted(legacy.iterdir()) if d.is_dir()]
for pat in ("taiex_*.json", "expansion_ohlcv.json"):
    moves += [(f, RAW_DIR / f.name) for f in sorted(ROOT.glob(pat))]

if not moves:
    print("Nothing to migrate — layout is already current.")
for src, dst in moves:
    if dst.exists() and (SEED_DIR / f"reports-{dst.name}").exists():
        # Auto-seeded copy of the tracked snapshot: the user's real one wins.
        if apply:
            shutil.rmtree(dst)
    elif dst.exists():
        print(f"  skip   {src.relative_to(ROOT)}  ({dst.relative_to(ROOT)} exists)")
        continue
    print(f"  {'move' if apply else 'would move'}  {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
if apply and legacy.is_dir() and not any(legacy.iterdir()):
    legacy.rmdir()
if not apply and moves:
    print("\nRe-run with --apply to perform the moves.")
