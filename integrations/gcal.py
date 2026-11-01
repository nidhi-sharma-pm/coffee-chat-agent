from datetime import datetime

from googleapiclient.discovery import build

from integrations import get_creds


def _service():
    return build("calendar", "v3", credentials=get_creds(), cache_discovery=False)


def _dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def busy_times(start, end):
    body = {"timeMin": start.isoformat(), "timeMax": end.isoformat(), "items": [{"id": "primary"}]}
    busy = _service().freebusy().query(body=body).execute()["calendars"]["primary"]["busy"]
    return [(_dt(b["start"]), _dt(b["end"])) for b in busy]


def create_invite_draft(summary, description, start, end, attendee_email=None):
    """Create the event WITHOUT emailing anyone (sendUpdates='none').
    Open it in Google Calendar and send the invite yourself."""
    body = {
        "summary": "[DRAFT] " + summary,
        "description": description,
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }
    if attendee_email:
        body["attendees"] = [{"email": attendee_email}]
    event = _service().events().insert(calendarId="primary", body=body, sendUpdates="none").execute()
    return event["htmlLink"]
