from agent.llm import draft
from agent.prompts import CHAT_PREP


def make_chat_prep(profile, brief_md, common, my_profile_text, goal):
    """One-page markdown prep sheet to read right before the chat."""
    text, _ = draft(CHAT_PREP.format(
        name=profile.get("name") or "them",
        goal=goal,
        me=my_profile_text or "(not saved)",
        them=profile["raw"],
        brief=brief_md,
        common=common or "(not generated)",
    ), max_tokens=4000)
    return text
