#!/usr/bin/env python3
"""
Chained Pipelines — output of one agent feeds into the next.

Available pipelines:
  crawl-extract   Crawl URL(s) in parallel → Data Extractor → save file
  code-insights   Code Reviewer → Creativity Manager (targeted improvement ideas)
  full            Crawl → Extract → Review code found → Generate ideas (all chained)
"""

import asyncio
import argparse
from concurrent.futures import ThreadPoolExecutor

from agents import crawl, extract, review, generate


# ── Pipeline 1: Crawl → Extract ──────────────────────────────────────────────

def _crawl_single(url: str, output_format: str, output_path: str) -> dict:
    """Crawl one URL then extract its data into a file."""
    print(f"  [crawl]   {url}")
    cr = crawl(url)
    if cr.get("error"):
        return {"error": cr["error"], "url": url}

    print(f"  [extract] → {output_format} ({output_path})")
    er = extract(cr["raw_text"], output_format=output_format, output_path=output_path)

    return {
        "url": url,
        "summary": cr["summary"],
        "links_found": len(cr["links"]),
        "output": er,
    }


async def crawl_extract(
    urls: list,
    output_format: str = "sqlite",
    output_path: str = "research",
) -> dict:
    """
    Crawl one or more URLs in parallel, combine their content,
    then extract structured data into a single output file.

    Args:
        urls:          List of URLs to crawl.
        output_format: json | csv | markdown | sqlite
        output_path:   Output file path without extension.

    Returns:
        dict with crawl summaries, extract result, and any errors.
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=min(len(urls), 8))

    print(f"\n[Pipeline: crawl-extract] {len(urls)} URL(s) → {output_format}\n")
    print("Step 1/2 — Crawling in parallel...")

    crawl_results = await asyncio.gather(
        *[loop.run_in_executor(executor, crawl, url) for url in urls]
    )

    successes = [r for r in crawl_results if not r.get("error")]
    failures = [r for r in crawl_results if r.get("error")]

    if not successes:
        return {"error": "All URLs failed to crawl", "failures": failures}

    combined_text = "\n\n---\n\n".join(
        f"Source: {r['url']}\n\n{r['raw_text']}" for r in successes
    )

    print(f"\nStep 2/2 — Extracting {len(successes)} page(s) of content → {output_format}...")
    er = extract(combined_text, output_format=output_format, output_path=output_path)

    return {
        "urls_crawled": len(successes),
        "urls_failed": len(failures),
        "failed_urls": [r["url"] for r in failures],
        "summaries": {r["url"]: r["summary"] for r in successes},
        "output": er,
    }


# ── Pipeline 2: Code Review → Improvement Ideas ───────────────────────────────

def code_insights(
    file_path: str = None,
    code: str = None,
    idea_count: int = 5,
    mode: str = "first_principles",
) -> dict:
    """
    Review code, then use the review findings to generate targeted improvement ideas.

    Args:
        file_path:  Path to a code file (use this OR code).
        code:       Inline code string.
        idea_count: Number of improvement ideas to generate.
        mode:       Creative mode for the idea generator.

    Returns:
        dict with review and improvement_ideas.
    """
    print("\n[Pipeline: code-insights]\n")
    print("Step 1/2 — Reviewing code...")
    rev = review(code=code, file_path=file_path)

    if "error" in rev:
        return rev

    # Feed the review's executive summary and top issues into the idea generator
    review_excerpt = rev["review"][:1500]
    topic = (
        f"Code improvement ideas based on this review of {file_path or 'code snippet'} "
        f"({rev['language']}):\n\n{review_excerpt}"
    )

    print(f"\nStep 2/2 — Generating {idea_count} improvement idea(s) (mode: {mode})...")
    ideas = generate(topic=topic, count=idea_count, mode=mode)

    return {
        "file": file_path,
        "language": rev["language"],
        "review": rev["review"],
        "improvement_ideas": ideas["ideas"],
        "mode_used": ideas["mode_used"],
    }


# ── Pipeline 3: Full (Crawl → Extract → Review → Ideas) ──────────────────────

async def full_pipeline(
    url: str,
    code_file: str = None,
    topic: str = None,
    output_format: str = "sqlite",
    output_path: str = "research",
    idea_count: int = 5,
) -> dict:
    """
    Full chained pipeline — runs all agents, feeding outputs between stages.

    Stage 1: Crawl the URL
    Stage 2: Extract crawled data → save file  (parallel with stage 3 if code_file given)
    Stage 3: Review code file (if provided)
    Stage 4: Generate ideas from the review + crawl summary (or a custom topic)

    Args:
        url:           URL to crawl.
        code_file:     Optional code file to review.
        topic:         Custom idea topic (defaults to auto-generated from crawl + review).
        output_format: Format for the data extractor output.
        output_path:   Output file path without extension.
        idea_count:    Number of ideas to generate.

    Returns:
        dict with all stage results.
    """
    print("\n[Pipeline: full]\n")

    # Stage 1 — Crawl
    print("Stage 1/4 — Crawling URL...")
    crawl_result = crawl(url)
    if crawl_result.get("error"):
        return {"error": f"Crawl failed: {crawl_result['error']}"}

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=2)

    # Stage 2+3 — Extract and (optionally) Code Review in parallel
    print("Stage 2/4 — Extracting crawled data + reviewing code (parallel)...")

    stage2_tasks = [
        loop.run_in_executor(
            executor, extract, crawl_result["raw_text"], output_format, output_path
        )
    ]

    review_future = None
    if code_file:
        review_future = loop.run_in_executor(executor, review, None, code_file)
        stage2_tasks.append(review_future)

    stage2_results = await asyncio.gather(*stage2_tasks)
    extract_result = stage2_results[0]
    review_result = stage2_results[1] if code_file else None

    # Stage 4 — Generate ideas
    print("Stage 4/4 — Generating ideas...")
    if not topic:
        parts = [f"URL crawled: {url}", f"Summary: {crawl_result['summary'][:600]}"]
        if review_result and "review" in review_result:
            parts.append(f"Code review findings: {review_result['review'][:600]}")
        topic = "\n\n".join(parts)

    ideas = generate(topic=topic, count=idea_count, mode="crossover")

    return {
        "crawl": {
            "url": url,
            "summary": crawl_result["summary"],
            "links_found": len(crawl_result["links"]),
        },
        "extract": extract_result,
        "review": review_result,
        "ideas": ideas["ideas"],
        "ideas_mode": ideas["mode_used"],
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_section(title: str, content: str) -> None:
    bar = "─" * 60
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)
    print(content)


async def _main(args: argparse.Namespace) -> None:
    if args.pipeline == "crawl-extract":
        result = await crawl_extract(
            urls=args.urls,
            output_format=args.format,
            output_path=args.output,
        )
        print("\n✓ Done")
        for url, summary in result.get("summaries", {}).items():
            _print_section(f"Summary: {url}", summary)
        out = result.get("output", {})
        print(f"\nOutput saved: {out.get('path', '?')}")
        if result.get("urls_failed"):
            print(f"Failed URLs: {result['failed_urls']}")

    elif args.pipeline == "code-insights":
        result = code_insights(
            file_path=args.code_file,
            code=args.code,
            idea_count=args.ideas,
            mode=args.mode,
        )
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        _print_section("Code Review", result["review"])
        _print_section("Improvement Ideas", result["improvement_ideas"])

    elif args.pipeline == "full":
        result = await full_pipeline(
            url=args.url,
            code_file=args.code_file,
            topic=args.topic,
            output_format=args.format,
            output_path=args.output,
            idea_count=args.ideas,
        )
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        _print_section("Crawl Summary", result["crawl"]["summary"])
        print(f"\nData saved: {result['extract'].get('path', '?')}")
        if result["review"]:
            _print_section("Code Review", result["review"]["review"])
        _print_section("Generated Ideas", result["ideas"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chained Pipelines — agents feeding into each other",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipelines:

  crawl-extract   Crawl URL(s) → extract structured data → save file
    python pipeline.py crawl-extract --urls https://site1.com https://site2.com --format sqlite --output research

  code-insights   Review code → generate improvement ideas from the findings
    python pipeline.py code-insights --code-file myapp.py --ideas 5 --mode first_principles

  full            Crawl → Extract → Review code → Generate ideas (all chained)
    python pipeline.py full --url https://example.com --code-file app.py --format json --output output
        """,
    )

    sub = parser.add_subparsers(dest="pipeline", required=True)

    # crawl-extract
    ce = sub.add_parser("crawl-extract", help="Crawl URL(s) then extract data")
    ce.add_argument("--urls", nargs="+", required=True, metavar="URL", help="One or more URLs to crawl")
    ce.add_argument("--format", default="sqlite", choices=["json", "csv", "markdown", "sqlite"])
    ce.add_argument("--output", default="research", metavar="PATH", help="Output path without extension")

    # code-insights
    ci = sub.add_parser("code-insights", help="Review code then generate improvement ideas")
    ci_src = ci.add_mutually_exclusive_group(required=True)
    ci_src.add_argument("--code-file", dest="code_file", metavar="FILE", help="Code file to review")
    ci_src.add_argument("--code", metavar="CODE", help="Inline code string")
    ci.add_argument("--ideas", type=int, default=5, metavar="N", help="Number of ideas (default: 5)")
    ci.add_argument("--mode", default="first_principles",
                    choices=["startup", "future", "crossover", "contrarian", "first_principles", "random"])

    # full
    fl = sub.add_parser("full", help="Crawl → Extract → Review → Ideas")
    fl.add_argument("--url", required=True, metavar="URL", help="URL to crawl")
    fl.add_argument("--code-file", dest="code_file", metavar="FILE", help="Optional code file to review")
    fl.add_argument("--topic", metavar="TEXT", help="Custom idea topic (auto-generated if omitted)")
    fl.add_argument("--format", default="sqlite", choices=["json", "csv", "markdown", "sqlite"])
    fl.add_argument("--output", default="research", metavar="PATH")
    fl.add_argument("--ideas", type=int, default=5, metavar="N")

    asyncio.run(_main(parser.parse_args()))


if __name__ == "__main__":
    main()
