"""
Code Reviewer Agent
Model: claude-opus-4-8 with adaptive thinking — needs deep reasoning for professional review
"""

import anthropic
from pathlib import Path

MODEL = "claude-opus-4-8"
_client = anthropic.Anthropic()

_SYSTEM = """You are a senior software engineer performing a professional code review.
Structure your response exactly as follows:

## Executive Summary
One concise paragraph covering overall code quality and the most critical finding.

## Issues Found
Rate each issue: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low
For each: state the issue, reference the line/function if possible, and give a fix recommendation.

## Security Analysis
Identify any security vulnerabilities (injection, auth issues, secrets in code, insecure deps, etc.).
State "None found" if clean.

## Performance Notes
Identify inefficiencies, n+1 queries, blocking calls, memory leaks, etc.
State "None found" if clean.

## Positive Observations
What the code does well (at least two points).

## Suggested Fix
Show a corrected code snippet for the single most critical issue only. Omit if no critical issues."""


def review(
    code: str = None,
    file_path: str = None,
    language: str = "auto",
) -> dict:
    """
    Perform a professional code review with executive summary and severity ratings.

    Args:
        code:      Code string to review (use this OR file_path).
        file_path: Path to a code file (extension auto-detects language).
        language:  Language hint e.g. 'python', 'typescript'. 'auto' infers from file ext.

    Returns:
        dict with keys: model, language, review, input_tokens, output_tokens
    """
    if file_path:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        code = path.read_text(encoding="utf-8")
        if language == "auto":
            language = path.suffix.lstrip(".") or "unknown"
    elif not code:
        return {"error": "Provide either 'code' string or 'file_path'"}

    if language == "auto":
        language = "unknown"

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Language: {language}\n\n```{language}\n{code}\n```",
            }
        ],
    )

    review_text = next(
        block.text for block in msg.content if hasattr(block, "text") and block.type == "text"
    )

    return {
        "model": MODEL,
        "language": language,
        "review": review_text,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }
