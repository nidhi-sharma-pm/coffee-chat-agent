from pathlib import Path

from pypdf import PdfReader

from agent.llm import extract
from agent.prompts import PROFILE_EXTRACT

MY_PROFILE = Path(__file__).resolve().parent.parent / "my_profile.txt"  # gitignored

FIELDS = ["name", "current_role", "company", "past_roles", "education",
          "location", "topics", "linkedin_url"]


def pdf_to_text(file):
    """Read text from a PDF on this Mac (LinkedIn 'Save to PDF' is plain text).
    Returns "" for scanned or image-only PDFs."""
    pages = PdfReader(file).pages
    text = "\n".join(page.extract_text() or "" for page in pages)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


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


def load_my_profile():
    return MY_PROFILE.read_text() if MY_PROFILE.exists() else ""


def save_my_profile(text):
    MY_PROFILE.write_text(text.strip())
