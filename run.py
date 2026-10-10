#!/usr/bin/env python3
"""Launcher for every script in src/twetf/.

    python run.py <name> [args...]     e.g.  python run.py fetch_taiex --months=1
    python run.py --list               show every runnable module, grouped by layer

<name> is the module's file name without .py; it is resolved across fetchers/,
analyzers/, renderers/, pipeline/ and oneoff/. Works from any working directory.
"""
import runpy
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
LAYERS = ("fetchers", "analyzers", "renderers", "pipeline", "oneoff")


def modules():
    for layer in LAYERS:
        for p in sorted((SRC / "twetf" / layer).glob("*.py")):
            if p.stem != "__init__":
                yield layer, p.stem


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if sys.argv[1] == "--list":
        for layer, name in modules():
            print(f"{layer:10s} {name}")
        return 0
    name = Path(sys.argv[1]).stem
    hits = [f"twetf.{layer}.{n}" for layer, n in modules() if n == name]
    if not hits:
        print(f"run.py: unknown script '{name}' (see: python run.py --list)", file=sys.stderr)
        return 2
    sys.path.insert(0, str(SRC))
    sys.argv = [sys.argv[1], *sys.argv[2:]]
    runpy.run_module(hits[0], run_name="__main__", alter_sys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
