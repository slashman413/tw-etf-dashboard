"""
Code Reviewer Agent
Prompt + model: config/llm.toml [tasks.code_review] (adaptive thinking)
"""

from pathlib import Path

from twetf import llm

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

    msg = llm.run("code_review", language=language, code=code)
    review_text = llm.text(msg)

    return {
        "model": llm.task("code_review")["model"],
        "language": language,
        "review": review_text,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }
