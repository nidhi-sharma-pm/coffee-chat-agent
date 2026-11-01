from agent.llm import draft
from agent.prompts import COMMON_GROUND


def find_common_ground(their_profile, my_profile_text):
    """Markdown: overlaps, where paths differ, and how to use it in the chat."""
    text, _ = draft(COMMON_GROUND.format(me=my_profile_text, them=their_profile["raw"]),
                    max_tokens=3000)
    return text
