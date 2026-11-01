from agent.llm import extract
from agent.prompts import PROFILE_EXTRACT

FIELDS = ["name", "current_role", "company", "past_roles", "education",
          "location", "topics", "linkedin_url"]


def parse_profile(text):
    """Turn a pasted profile into clean fields. Missing fields stay None."""
    data = extract(PROFILE_EXTRACT.format(profile=text))
    profile = {f: data.get(f) or None for f in FIELDS}
    profile["raw"] = text
    return profile


def profile_for_prompt(profile):
    """Readable profile text for other prompts (without the raw paste)."""
    lines = []
    for f in FIELDS:
        v = profile.get(f)
        if v:
            lines.append(f"{f}: {', '.join(v) if isinstance(v, list) else v}")
    return "\n".join(lines)
