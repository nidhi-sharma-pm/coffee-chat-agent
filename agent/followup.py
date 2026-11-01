import os

from agent.llm import draft
from agent.outreach import split_email
from agent.prompts import CHECK_IN, THANK_YOU, TONE


def _run(template, profile, notes, **extra):
    text, _ = draft(template.format(
        name=profile.get("name") or "them",
        me=os.getenv("YOUR_BLURB", ""),
        notes=notes,
        tone=TONE,
        **extra,
    ), max_tokens=2000)
    subject, body = split_email(text)
    return {"subject": subject, "body": body}


def draft_thank_you(profile, notes):
    return _run(THANK_YOU, profile, notes)


def draft_check_in(profile, notes, weeks_since):
    return _run(CHECK_IN, profile, notes, weeks=weeks_since)
