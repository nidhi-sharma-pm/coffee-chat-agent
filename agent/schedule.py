import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agent.llm import quick
from agent.prompts import INVITE
from integrations import gcal


def open_slots(days=7, length=30, work_start=9, work_end=17, limit=5):
    """Free weekday slots in working hours, starting tomorrow."""
    tz = ZoneInfo(os.getenv("USER_TIMEZONE", "UTC"))
    start = (datetime.now(tz) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=days)
    busy = gcal.busy_times(start, end)
    step, dur = timedelta(minutes=30), timedelta(minutes=length)

    slots, day = [], start
    while day < end and len(slots) < limit:
        if day.weekday() < 5:
            t = day.replace(hour=work_start)
            day_end = day.replace(hour=work_end)
            while t + dur <= day_end and len(slots) < limit:
                if all(t + dur <= b0 or t >= b1 for b0, b1 in busy):
                    slots.append(t)
                    t += dur  # don't offer overlapping slots
                else:
                    t += step
        day += timedelta(days=1)
    return slots


def draft_invite(profile, slot, length, attendee_email, goal):
    description = quick(INVITE.format(
        me_name=os.getenv("YOUR_NAME", "me"),
        name=profile.get("name") or "guest",
        role=profile.get("current_role") or "",
        company=profile.get("company") or "",
        goal=goal,
    ))
    summary = f"Coffee chat: {os.getenv('YOUR_NAME', 'me')} / {profile.get('name') or 'guest'}"
    return gcal.create_invite_draft(summary, description, slot,
                                    slot + timedelta(minutes=length), attendee_email)
