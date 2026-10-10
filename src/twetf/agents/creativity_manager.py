"""
Creativity Manager Agent
Prompt + model: config/llm.toml [tasks.creative_ideas]; lenses: [creative_modes]
"""

import random

from twetf import llm


def generate(
    topic: str,
    count: int = 5,
    mode: str = "random",
    save_to: str = None,
) -> dict:
    """
    Generate bold, specific, actionable creative ideas on any topic.

    Args:
        topic:   The subject to ideate on (e.g. 'AI-powered tutoring apps').
        count:   Number of ideas to generate (1–20).
        mode:    Creative lens — one of: startup, future, crossover, contrarian,
                 first_principles, random. Default: random.
        save_to: Optional file path to save ideas as Markdown (e.g. 'ideas.md').

    Returns:
        dict with keys: topic, mode_used, ideas (str), count
    """
    count = max(1, min(count, 20))

    modes = llm.config()["creative_modes"]
    actual_mode = mode if mode in modes else random.choice(list(modes))
    persona = modes[actual_mode]

    msg = llm.run("creative_ideas", persona=persona, count=count, topic=topic)

    ideas_text = llm.text(msg)

    if save_to:
        from pathlib import Path
        path = Path(save_to)
        path.write_text(f"# Creative Ideas: {topic}\n\nMode: {actual_mode}\n\n{ideas_text}", encoding="utf-8")

    return {
        "topic": topic,
        "mode_used": actual_mode,
        "ideas": ideas_text,
        "count": count,
        "saved_to": save_to,
    }
