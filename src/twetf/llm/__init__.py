"""The only place this repo talks to an LLM API.

    from twetf import llm
    msg = llm.run("web_summary", url=url, raw_text=text)   # task defined in config/llm.toml
    llm.text(msg)                                          # first text block

Prompts and model choices live in config/llm.toml; call sites only pass variables.
The Anthropic client is created lazily, so importing an agent no longer requires
ANTHROPIC_API_KEY (the old module-level `anthropic.Anthropic()` did).
"""
import tomllib
from functools import lru_cache

from twetf.paths import ROOT

CONFIG_PATH = ROOT / "config" / "llm.toml"


@lru_cache(maxsize=1)
def config():
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def task(name):
    return config()["tasks"][name]


@lru_cache(maxsize=1)
def _client():
    import anthropic
    return anthropic.Anthropic()


def build_request(name, **vars):
    """The kwargs for messages.create — split out so it can be inspected/tested offline."""
    t = task(name)
    req = {
        "model": t["model"],
        "max_tokens": t["max_tokens"],
        "system": t["system"].format_map(vars),
        "messages": [{"role": "user", "content": t["user"].format_map(vars)}],
    }
    if t.get("thinking"):
        req["thinking"] = {"type": t["thinking"]}
    return req


def run(name, **vars):
    """Render task `name` with `vars` and send it. Returns the raw Message."""
    return _client().messages.create(**build_request(name, **vars))


def text(msg):
    """First text block of a Message (skips thinking blocks)."""
    return next(b.text for b in msg.content if getattr(b, "type", None) == "text")
