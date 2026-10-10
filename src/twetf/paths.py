"""Single source of truth for every on-disk location the scripts use.

Layout (repo root):
  dashboard.html, series_map.json   published by GitHub Pages — tracked, written by CI
  config.json                       local settings
  assets/                           images embedded into dashboard.html
  data/seed/                        tracked bootstrap snapshots (a fresh clone works offline)
  data/raw/                         fetched market data              — gitignored
  data/reports/<YYYY-MM-DD>/        analyzer outputs                 — gitignored
  cache/                            disposable HTTP/intermediate cache — gitignored
  docs/                             generated long-form reports

Paths are absolute (anchored at the repo root), so scripts no longer depend on the
current working directory.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_PY = ROOT / "run.py"

DASHBOARD = ROOT / "dashboard.html"
SERIES_MAP = ROOT / "series_map.json"
CONFIG_PATH = ROOT / "config.json"
ASSETS_DIR = ROOT / "assets"
DOCS_DIR = ROOT / "docs"

DATA_DIR = ROOT / "data"
SEED_DIR = DATA_DIR / "seed"
RAW_DIR = DATA_DIR / "raw"
REPORTS_DIR = DATA_DIR / "reports"
CACHE_DIR = ROOT / "cache"


def raw_path(name):
    """Where a fetcher should write `name` (creates data/raw/)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    return RAW_DIR / name


def raw_or_seed(name):
    """Freshest copy of `name`: data/raw/ if a fetcher produced it, else the tracked seed."""
    p = RAW_DIR / name
    return p if p.exists() else SEED_DIR / name


def script_cmd(name, *args):
    """argv that runs another module of this repo, e.g. script_cmd("fetch_taiex", "--months=1")."""
    return [sys.executable, str(RUN_PY), Path(name).stem, *map(str, args)]


def _bootstrap():
    """Seed data/reports/ on a fresh clone so analyzers have a dated dir to read."""
    for d in (RAW_DIR, REPORTS_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
    if not any(p.is_dir() and p.name[:4].isdigit() for p in REPORTS_DIR.iterdir()):
        for seed in sorted(SEED_DIR.glob("reports-*")):
            dst = REPORTS_DIR / seed.name.removeprefix("reports-")
            if not dst.exists():
                shutil.copytree(seed, dst)


_bootstrap()
