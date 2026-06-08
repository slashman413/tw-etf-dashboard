"""
Creativity Manager Agent
Model: claude-sonnet-4-6 — strong creative reasoning at a fraction of Opus cost
"""

import random
import anthropic

MODEL = "claude-sonnet-4-6"
_client = anthropic.Anthropic()

MODES = {
    "startup":     "Think like a bold startup founder with $10M and 12 months to ship.",
    "future":      "Think like a scientist 50 years in the future looking back at today's primitives.",
    "crossover":   "Combine two completely unrelated industries in an unexpected way.",
    "contrarian":  "What would the most contrarian, counter-intuitive approach look like?",
    "first_principles": "Strip the problem down to first principles. Ignore all existing solutions.",
    "random":      None,  # picks a random mode each call
}


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

    if mode == "random" or mode not in MODES:
        actual_mode = random.choice([m for m in MODES if m != "random"])
    else:
        actual_mode = mode

    persona = MODES[actual_mode]

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=f"""You are a world-class creative strategist. {persona}

Generate exactly {count} ideas. Format each as:

**Idea N: [Catchy Name]**
**Concept:** One sentence describing the idea.
**Why it works:** One sentence on the insight or opportunity it exploits.
**First step:** One concrete action someone can take today to start.
""",
        messages=[{"role": "user", "content": f"Generate {count} creative ideas about: {topic}"}],
    )

    ideas_text = msg.content[0].text

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
