import json
import os

from agent.llm import draft, parse_json, quick
from agent.profile import profile_for_prompt
from agent.prompts import LINKEDIN, NUDGE, SHORTEN, TONE

NOTE_LIMIT = 300  # LinkedIn's connection note limit


def draft_linkedin(profile, brief_md, goal, common=""):
    """Returns {"note": connection note, "dm": first message after they accept}."""
    text, _ = draft(LINKEDIN.format(
        name=profile.get("name") or "them",
        me=os.getenv("YOUR_BLURB", ""),
        goal=goal,
        profile=profile_for_prompt(profile),
        brief=brief_md,
        common=common or "(none found)",
        tone=TONE,
    ), max_tokens=2000)
    try:
        data = parse_json(text)
    except json.JSONDecodeError:
        return {"note": "", "dm": text}
    note = (data.get("note") or "").strip()
    if len(note) > NOTE_LIMIT:
        note = quick(SHORTEN.format(limit=280, text=note))
    return {"note": note, "dm": (data.get("dm") or "").strip()}


def draft_nudge(name, days, notes=None):
    return quick(NUDGE.format(name=name, days=days, context=notes or "none", tone=TONE))
