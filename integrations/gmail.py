import base64
from email.message import EmailMessage

from googleapiclient.discovery import build

from integrations import get_creds

# This module only creates drafts. There is deliberately no send function:
# you review every draft in Gmail and hit send yourself.


def create_draft(to, subject, body):
    msg = EmailMessage()
    msg["To"], msg["Subject"] = to, subject
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service = build("gmail", "v1", credentials=get_creds(), cache_discovery=False)
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft["id"]
