"""All Claude calls go through this file. Nothing else imports anthropic."""
import json
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

DRAFT_MODEL = "claude-sonnet-5-5"  # drafts and briefs
SMALL_MODEL = "claude-haiku-5-5"   # small extraction jobs
WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
# If a request is declined, the API retries it on a fallback model automatically.
FALLBACK_BETA = "server-side-fallback-2026-07-01"

_client = anthropic.Anthropic(max_retries=3, timeout=180.0)


class LLMError(RuntimeError):
    pass


def _check(response):
    if response.stop_reason == "refusal":
        raise LLMError("Claude declined this request. Try rewording it.")
    if response.stop_reason == "max_tokens":
        raise LLMError("Response was cut off. Raise max_tokens.")


def _text(blocks):
    return "".join(b.text for b in blocks if b.type == "text").strip()


def _sources(blocks):
    """Collect (title, url) pairs from web search results, deduplicated."""
    seen, out = set(), []
    for b in blocks:
        if b.type == "web_search_tool_result" and isinstance(b.content, list):
            for r in b.content:
                if r.url not in seen:
                    seen.add(r.url)
                    out.append({"title": r.title, "url": r.url})
    return out


def draft(prompt, system=None, web_search=False, max_tokens=8000):
    """Sonnet call. Returns (text, sources). Sources is empty without web search."""
    messages = [{"role": "user", "content": prompt}]
    kwargs = dict(
        model=DRAFT_MODEL,
        max_tokens=max_tokens,
        messages=messages,
        betas=[FALLBACK_BETA],
        fallbacks="default",
    )
    if system:
        kwargs["system"] = system
    if web_search:
        kwargs["tools"] = [WEB_SEARCH]

    blocks = []
    for _ in range(5):  # long searches can pause; resume up to 5 times
        response = _client.beta.messages.create(**kwargs)
        _check(response)
        blocks.extend(response.content)
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})
    return _text(blocks), _sources(blocks)


def quick(prompt, max_tokens=1000):
    """Haiku call for short plain-text output."""
    response = _client.messages.create(
        model=SMALL_MODEL,
        max_tokens=max_tokens,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )
    _check(response)
    return _text(response.content)


def parse_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)


def extract(prompt, max_tokens=2000):
    """Haiku call that must return JSON. Retries once if the JSON is broken."""
    text = quick(prompt, max_tokens)
    try:
        return parse_json(text)
    except json.JSONDecodeError:
        text = quick(prompt + "\n\nReturn ONLY valid JSON. No prose, no code fences.", max_tokens)
        return parse_json(text)
