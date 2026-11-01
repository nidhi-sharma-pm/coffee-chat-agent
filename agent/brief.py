import re

from agent.llm import draft
from agent.profile import profile_for_prompt
from agent.prompts import BRIEF

FACT_SECTIONS = ("who they are", "recent work and news")


def find_unflagged(markdown):
    """Bullets in fact sections with neither a source link nor [UNVERIFIED]."""
    bad, in_facts = [], False
    for line in markdown.splitlines():
        if line.startswith("#"):
            in_facts = line.lstrip("# ").strip().lower() in FACT_SECTIONS
            continue
        if in_facts and re.match(r"\s*[-*] ", line):
            has_link = re.search(r"\]\((https?://[^)]+|profile)\)", line)
            if not has_link and "[UNVERIFIED]" not in line:
                bad.append(line.strip())
    return bad


def make_brief(profile):
    text, sources = draft(BRIEF.format(profile=profile_for_prompt(profile)), web_search=True)
    return {"markdown": text, "sources": sources, "unflagged": find_unflagged(text)}
