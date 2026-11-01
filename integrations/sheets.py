import os

import gspread

from integrations import get_creds

HEADERS = ["name", "company", "status", "last_contact", "next_step", "notes"]


def _sheet():
    ws = gspread.authorize(get_creds()).open_by_key(os.environ["SHEET_ID"]).sheet1
    if ws.row_values(1) != HEADERS:
        ws.update([HEADERS], "A1")
    return ws


def read_tracker():
    return _sheet().get_all_records()


def upsert_row(person):
    """Update the row matching name + company, or add a new one.
    Only non-empty fields overwrite, so a status change keeps existing notes."""
    ws = _sheet()
    name, company = str(person.get("name") or ""), str(person.get("company") or "")
    for i, rec in enumerate(ws.get_all_records(), start=2):
        if str(rec["name"]) == name and str(rec["company"]) == company:
            merged = {**rec, **{k: v for k, v in person.items() if v}}
            ws.update([[str(merged.get(h) or "") for h in HEADERS]], f"A{i}")
            return
    ws.append_row([str(person.get(h) or "") for h in HEADERS])
