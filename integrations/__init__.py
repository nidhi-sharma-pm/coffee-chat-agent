"""Shared Google login. First run opens a browser; after that token.json is reused."""
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
    "https://www.googleapis.com/auth/gmail.compose",
]
ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / "token.json"


def get_creds():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        secrets = ROOT / os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        if not secrets.exists():
            raise FileNotFoundError(
                "Google isn't connected yet. Download your OAuth client file as "
                f"credentials.json into {ROOT} (see README, Setup step 3).")
        creds = InstalledAppFlow.from_client_secrets_file(secrets, SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    return creds
