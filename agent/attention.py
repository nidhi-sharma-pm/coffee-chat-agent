"""Works out who needs attention today, from tracker dates alone (no LinkedIn access)."""
from datetime import date

STATUSES = ["Sent on LinkedIn", "Sent email", "Accepted", "Replied", "Meeting booked",
            "Chatted", "Checked in", "Not interested"]
WAITING = {"Sent on LinkedIn", "Sent email", "Accepted"}
STAY_IN_TOUCH = {"Chatted", "Checked in"}
NUDGE_AFTER_DAYS = 7
CHECK_IN_AFTER_DAYS = 28


def due_today(rows, today=None):
    """Returns (nudges, check_ins): tracker rows plus a 'days' field, oldest first."""
    today = today or date.today()
    nudges, check_ins = [], []
    for r in rows:
        try:
            days = (today - date.fromisoformat(str(r.get("last_contact", "")))).days
        except ValueError:
            continue
        if r.get("status") in WAITING and days >= NUDGE_AFTER_DAYS:
            nudges.append({**r, "days": days})
        elif r.get("status") in STAY_IN_TOUCH and days >= CHECK_IN_AFTER_DAYS:
            check_ins.append({**r, "days": days})
    by_age = lambda r: -r["days"]  # noqa: E731
    return sorted(nudges, key=by_age), sorted(check_ins, key=by_age)
