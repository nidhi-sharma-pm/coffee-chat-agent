import os

from agent.llm import draft, extract
from agent.prompts import REPLY_DRAFT, REPLY_TRIAGE, TONE

# intent -> (tracker status, next step)
INTENTS = {
    "yes": ("Replied", "Book meeting"),
    "no": ("Not interested", "None"),
    "later": ("Replied", "Follow up in a few weeks"),
    "question": ("Replied", "Answer their question"),
}


def triage_reply(text):
    data = extract(REPLY_TRIAGE.format(reply=text))
    intent = str(data.get("intent", "")).lower()
    return {"intent": intent if intent in INTENTS else "question",
            "summary": data.get("summary") or ""}


def draft_reply_response(name, my_message, their_reply, triage, slots=()):
    times = "\n".join(s.strftime("%a %d %b, %I:%M %p %Z") for s in slots) or "none"
    text, _ = draft(REPLY_DRAFT.format(
        name=name,
        me=os.getenv("YOUR_BLURB", ""),
        my_message=my_message or "(not provided)",
        reply=their_reply,
        intent=triage["intent"],
        times=times,
        tone=TONE,
    ), max_tokens=1500)
    return text
