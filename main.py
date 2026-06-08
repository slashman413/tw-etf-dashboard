#!/usr/bin/env python3
"""
Multi-Agent Parallel Runner
Runs Web Crawler, Data Extractor, Code Reviewer, and Creativity Manager simultaneously.
"""

import asyncio
import argparse
from concurrent.futures import ThreadPoolExecutor

from agents import crawl, extract, review, generate


def _run(name: str, fn, *args, **kwargs) -> dict:
    try:
        result = fn(*args, **kwargs)
        return {"agent": name, "status": "ok", "result": result}
    except Exception as e:
        return {"agent": name, "status": "error", "error": str(e)}


def _print_result(r: dict) -> None:
    bar = "=" * 60
    print(f"\n{bar}")
    icon = "✓" if r["status"] == "ok" else "✗"
    print(f"  {icon}  {r['agent'].replace('_', ' ').upper()}")
    print(bar)

    if r["status"] == "error":
        print(f"Error: {r['error']}")
        return

    res = r["result"]
    if not isinstance(res, dict):
        print(res)
        return

    skip = {"raw_text", "data", "ideas"}
    for k, v in res.items():
        if k in skip:
            continue
        print(f"{k}: {v}")

    if "ideas" in res:
        print(res["ideas"])
    if "summary" in res:
        print("\n--- Summary ---")
        print(res["summary"])


async def run_all(args: argparse.Namespace) -> list:
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)
    tasks = []

    if args.url:
        tasks.append(loop.run_in_executor(executor, _run, "web_crawler", crawl, args.url))

    if args.content:
        tasks.append(
            loop.run_in_executor(
                executor, _run, "data_extractor", extract, args.content, args.format, args.output
            )
        )

    if args.code or args.code_file:
        tasks.append(
            loop.run_in_executor(
                executor, _run, "code_reviewer", review, args.code, args.code_file, args.language
            )
        )

    if args.topic:
        tasks.append(
            loop.run_in_executor(
                executor,
                _run,
                "creativity_manager",
                generate,
                args.topic,
                args.ideas,
                args.mode,
                args.save_ideas,
            )
        )

    if not tasks:
        print("No agents configured. Pass at least one: --url, --content, --code/--code-file, --topic")
        return []

    print(f"\nLaunching {len(tasks)} agent(s) in parallel...\n")
    results = await asyncio.gather(*tasks)

    for r in results:
        _print_result(r)

    return list(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Parallel Runner — Web Crawler · Data Extractor · Code Reviewer · Creativity Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all 4 agents at once
  python main.py --url https://news.ycombinator.com --content "Name,Age\\nAlice,30\\nBob,25" --code-file app.py --topic "AI productivity tools"

  # Web crawler only
  python main.py --url https://example.com

  # Code review a file
  python main.py --code-file myapp.py

  # Extract data to SQLite
  python main.py --content "Product: Widget, Price: 9.99, Stock: 42" --format sqlite --output products

  # 10 startup-mode ideas saved to file
  python main.py --topic "remote work tools" --ideas 10 --mode startup --save-ideas ideas.md
        """,
    )

    # Web Crawler
    crawler = parser.add_argument_group("Web Crawler")
    crawler.add_argument("--url", metavar="URL", help="URL to crawl and summarize")

    # Data Extractor
    extractor = parser.add_argument_group("Data Extractor")
    extractor.add_argument("--content", metavar="TEXT", help="Raw text content to extract data from")
    extractor.add_argument(
        "--format", default="json", choices=["json", "csv", "markdown", "sqlite"],
        help="Output format (default: json)"
    )
    extractor.add_argument("--output", default="output", metavar="PATH", help="Output file path without extension (default: output)")

    # Code Reviewer
    reviewer = parser.add_argument_group("Code Reviewer")
    reviewer.add_argument("--code", metavar="CODE", help="Code string to review")
    reviewer.add_argument("--code-file", metavar="FILE", dest="code_file", help="Path to a code file to review")
    reviewer.add_argument("--language", default="auto", metavar="LANG", help="Language hint e.g. python, typescript (default: auto)")

    # Creativity Manager
    creative = parser.add_argument_group("Creativity Manager")
    creative.add_argument("--topic", metavar="TOPIC", help="Topic to generate creative ideas about")
    creative.add_argument("--ideas", type=int, default=5, metavar="N", help="Number of ideas to generate (default: 5)")
    creative.add_argument(
        "--mode", default="random",
        choices=["startup", "future", "crossover", "contrarian", "first_principles", "random"],
        help="Creative lens (default: random)"
    )
    creative.add_argument("--save-ideas", metavar="FILE", dest="save_ideas", help="Save ideas to a Markdown file")

    asyncio.run(run_all(parser.parse_args()))


if __name__ == "__main__":
    main()
