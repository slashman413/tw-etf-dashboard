#!/usr/bin/env python3
"""
Rebuild dashboard.html and push to GitHub Pages.
Usage: python auto_push.py [--dry-run]
"""
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).parent
DASHBOARD = HERE / "dashboard.html"
CONFIG_PATH = HERE / "config.json"

def load_cfg():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}

def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"  ❌ {' '.join(cmd)}\n  {result.stderr.strip()}")
        return False
    return True

def main():
    dry_run = "--dry-run" in sys.argv
    cfg = load_cfg()
    repo = cfg.get("github_repo", "")
    branch = cfg.get("github_branch", "main")

    # Step 1: Rebuild dashboard
    print(f"[{datetime.now():%H:%M:%S}] Rebuilding dashboard.html...")
    result = subprocess.run(
        [sys.executable, str(HERE / "build_dashboard.py")],
        capture_output=True, text=True, cwd=str(HERE)
    )
    if result.returncode != 0:
        print(f"  ❌ build_dashboard.py failed:\n{result.stderr[-800:]}")
        return 1
    print(f"  ✅ dashboard.html rebuilt ({DASHBOARD.stat().st_size // 1024} KB)")

    if dry_run:
        print("  [dry-run] skipping git push")
        return 0

    # Step 2: Push to GitHub
    # The dashboard.html lives in the root of the repo, alongside the Python scripts.
    # We commit only dashboard.html (+ full_market.json if it changed).
    repo_dir = HERE  # scripts are in the same dir as the repo
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    cmds = [
        (["git", "add", "dashboard.html"], "stage dashboard.html"),
        (["git", "diff", "--cached", "--quiet"], "check diff"),  # exits 1 if changes
        (["git", "commit", "-m", f"auto: rebuild dashboard {ts}"], "commit"),
        (["git", "push", "origin", branch], "push"),
    ]

    print(f"[{datetime.now():%H:%M:%S}] Pushing to {repo} ({branch})...")
    for cmd, label in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_dir))
        if label == "check diff" and result.returncode == 0:
            print("  ℹ️  No changes to push (dashboard unchanged)")
            return 0
        if result.returncode != 0 and label != "check diff":
            print(f"  ❌ {label}: {result.stderr.strip()[-300:]}")
            return 1
        if label not in ("check diff",):
            print(f"  ✅ {label}")

    url = f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[-1]}/dashboard.html"
    print(f"\n  🌐 Live at: {url}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
