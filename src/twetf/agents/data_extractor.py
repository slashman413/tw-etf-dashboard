"""
Data Extractor Agent
Prompt + model: config/llm.toml [tasks.data_extract]; formats: [extract_formats]
Supports output formats: json, csv, markdown, sqlite
"""

import csv
import json
import sqlite3
from io import StringIO
from pathlib import Path

from twetf import llm


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
    formats = llm.config()["extract_formats"]
    if fmt not in formats:
        return {"error": f"Unknown format '{fmt}'. Choose: json, csv, markdown, sqlite"}

    msg = llm.run("data_extract", format_instructions=formats[fmt], content=content)
    raw = _strip_fences(llm.text(msg))
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
