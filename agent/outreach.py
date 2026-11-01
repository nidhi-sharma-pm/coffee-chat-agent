import os

from agent.llm import draft
from agent.profile import profile_for_prompt
from agent.prompts import HOOK, OUTREACH, TONE


def split_email(text):
    """Split 'Subject: ...' first line from the body."""
    text = text.replace("[Your name]", os.getenv("YOUR_NAME", "[Your name]"))
    first, _, rest = text.partition("\n")
    if first.lower().startswith("subject:"):
        return first.split(":", 1)[1].strip(), rest.strip()
    return "", text.strip()


def draft_outreach(profile, brief_md, goal, common=""):
    text, _ = draft(OUTREACH.format(
        name=profile.get("name") or "them",
        me=os.getenv("YOUR_BLURB", ""),
        goal=goal,
        profile=profile_for_prompt(profile),
        brief=brief_md,
        common=common or "(none found)",
        tone=TONE,
        hook=HOOK,
    ), max_tokens=2000)
    subject, body = split_email(text)
    return {"subject": subject, "body": body}
