"""Checks briefs for unflagged facts and facts that contradict the profile.

Put 5-6 real profiles as .txt files in evals/profiles/ (gitignored), then:
    python evals/run_evals.py
Exits with code 1 if any profile fails.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.brief import make_brief  # noqa: E402
from agent.llm import extract  # noqa: E402
from agent.profile import parse_profile  # noqa: E402
from agent.prompts import EVAL_JUDGE  # noqa: E402

PROFILES = ROOT / "evals" / "profiles"
RESULTS = ROOT / "evals" / "results"


def main():
    files = sorted(PROFILES.glob("*.txt"))
    if not files:
        sys.exit(f"No profiles found. Add .txt files to {PROFILES}")
    RESULTS.mkdir(exist_ok=True)

    rows, failed = [], 0
    for f in files:
        text = f.read_text()
        brief = make_brief(parse_profile(text))
        wrong = extract(EVAL_JUDGE.format(profile=text, brief=brief["markdown"]))["contradictions"]
        ok = not brief["unflagged"] and not wrong
        failed += not ok
        rows.append((f.stem, len(brief["unflagged"]), len(wrong), "PASS" if ok else "FAIL"))

        report = [f"# {f.stem}", "", brief["markdown"], "", "## Unflagged facts"]
        report += [f"- {u}" for u in brief["unflagged"]] or ["- none"]
        report += ["", "## Contradictions"]
        report += [f"- {w['claim']} ({w['why']})" for w in wrong] or ["- none"]
        (RESULTS / f"{f.stem}.md").write_text("\n".join(report))

    print(f"\n{'profile':<28}{'unflagged':>10}{'wrong':>8}  result")
    for name, u, w, r in rows:
        print(f"{name:<28}{u:>10}{w:>8}  {r}")
    print(f"\n{len(rows) - failed}/{len(rows)} passed. Details in {RESULTS}/")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
