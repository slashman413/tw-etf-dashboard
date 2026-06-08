"""
Data Extractor Agent
Model: claude-haiku-4-5 — structured extraction is well within Haiku's capability
Supports output formats: json, csv, markdown, sqlite
"""

import csv
import json
import sqlite3
import anthropic
from io import StringIO
from pathlib import Path

MODEL = "claude-haiku-4-5"
_client = anthropic.Anthropic()

_FORMAT_PROMPTS = {
    "json": (
        "Return a valid JSON object (or array) containing all extracted data. "
        "Use descriptive key names. Return ONLY raw JSON, no markdown fences."
    ),
    "csv": (
        "Return data as CSV with a header row. Each subsequent row is one record. "
        "Return ONLY the raw CSV text, no markdown fences."
    ),
    "markdown": (
        "Return a well-formatted Markdown document. Use headers, bullet lists, and tables "
        "where appropriate. Return ONLY the Markdown, no extra commentary."
    ),
    "sqlite": (
        "Return a JSON object with exactly these keys: "
        "'table_name' (string), 'columns' (list of {name, type} objects), "
        "'rows' (list of lists matching column order). "
        "Use SQLite-compatible types (TEXT, INTEGER, REAL, BLOB). "
        "Return ONLY raw JSON, no markdown fences."
    ),
}


def _strip_fences(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def extract(
    content: str,
    output_format: str = "json",
    output_path: str = "output",
) -> dict:
    """
    Extract structured data from free-form content and save to a file.

    Args:
        content:       The raw text/data to extract from.
        output_format: One of 'json', 'csv', 'markdown', 'sqlite'.
        output_path:   File path without extension (extension is added automatically).

    Returns:
        dict with keys: format, path, and format-specific metadata.
    """
    fmt = output_format.lower()
    if fmt not in _FORMAT_PROMPTS:
        return {"error": f"Unknown format '{fmt}'. Choose: json, csv, markdown, sqlite"}

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=f"You are a data extraction specialist. {_FORMAT_PROMPTS[fmt]}",
        messages=[{"role": "user", "content": f"Extract all meaningful data from:\n\n{content}"}],
    )

    raw = _strip_fences(msg.content[0].text)
    base = Path(output_path)

    if fmt == "json":
        data = json.loads(raw)
        path = base.with_suffix(".json")
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"format": "json", "path": str(path), "data": data}

    elif fmt == "csv":
        path = base.with_suffix(".csv")
        path.write_text(raw, encoding="utf-8")
        reader = csv.reader(StringIO(raw))
        rows = list(reader)
        return {"format": "csv", "path": str(path), "rows": len(rows) - 1, "columns": rows[0] if rows else []}

    elif fmt == "markdown":
        path = base.with_suffix(".md")
        path.write_text(raw, encoding="utf-8")
        return {"format": "markdown", "path": str(path), "preview": raw[:300]}

    elif fmt == "sqlite":
        schema = json.loads(raw)
        path = base.with_suffix(".db")
        conn = sqlite3.connect(str(path))
        cols_def = ", ".join(f"{c['name']} {c['type']}" for c in schema["columns"])
        conn.execute(f"CREATE TABLE IF NOT EXISTS {schema['table_name']} ({cols_def})")
        placeholders = ", ".join("?" * len(schema["columns"]))
        conn.executemany(
            f"INSERT INTO {schema['table_name']} VALUES ({placeholders})", schema["rows"]
        )
        conn.commit()
        conn.close()
        return {
            "format": "sqlite",
            "path": str(path),
            "table": schema["table_name"],
            "columns": [c["name"] for c in schema["columns"]],
            "rows_inserted": len(schema["rows"]),
        }
