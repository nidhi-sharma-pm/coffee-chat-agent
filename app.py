"""Coffee chat agent. Run with: streamlit run app.py"""
from datetime import date

import streamlit as st

from agent.attention import STATUSES, due_today
from agent.brief import make_brief
from agent.common import find_common_ground
from agent.followup import draft_check_in, draft_thank_you
from agent.linkedin import NOTE_LIMIT, draft_linkedin, draft_nudge
from agent.outreach import draft_outreach
from agent.prep import make_chat_prep
from agent.profile import load_my_profile, parse_profile, pdf_to_text, save_my_profile
from agent.replies import INTENTS, draft_reply_response, triage_reply

st.set_page_config(page_title="Coffee Chat Agent", layout="wide")
st.title("Coffee Chat Agent")
st.caption("Drafts only. Nothing is ever sent. You review and hit send yourself.")
ss = st.session_state
DEFAULT_GOAL = "Learn how they moved into their current role"


# ---------- helpers ----------

def need(key, msg):
    if key not in ss:
        st.info(msg)
        return False
    return True


def load_tracker():
    from integrations.sheets import read_tracker
    try:
        ss.tracker = read_tracker()
    except Exception as e:
        st.error(f"Could not load tracker: {e}")


def update_tracker(name, company, **fields):
    from integrations.sheets import upsert_row
    try:
        upsert_row({"name": name, "company": company,
                    "last_contact": date.today().isoformat(), **fields})
        ss.pop("tracker", None)  # reload next time so lists stay fresh
        st.success("Tracker updated.")
    except Exception as e:
        st.error(f"Sheets error: {e}")


def copy_box(label, text):
    """Read-only box with a copy button (top right) for pasting into LinkedIn."""
    st.caption(label)
    st.code(text, language=None, wrap_lines=True)


def email_editor(key, result):
    subject = st.text_input("Subject", result["subject"], key=f"{key}_subj")
    body = st.text_area("Body", result["body"], height=260, key=f"{key}_body")
    return subject, body


def gmail_button(key, subject, body):
    to = st.text_input("Their email", key=f"{key}_to")
    if st.button("Save to Gmail drafts", key=f"{key}_gmail", disabled=not to):
        from integrations.gmail import create_draft
        try:
            create_draft(to, subject, body)
            st.success("Saved to Gmail drafts.")
        except Exception as e:
            st.error(f"Gmail error: {e}")


def person_label(p):
    return f"{p['name']} · {p['company']}" if p.get("company") else p["name"]


# ---------- tabs ----------

def tab_today():
    if st.button("Check who needs attention"):
        load_tracker()
    if "tracker" not in ss:
        st.info("Click the button to read your tracker.")
        return
    rows = ss.tracker
    if not rows:
        st.info("Your tracker is empty. Rows appear as you mark messages sent.")
        return
    nudges, check_ins = due_today(rows)

    st.subheader(f"No reply yet ({len(nudges)})")
    if not nudges:
        st.caption("Nobody waiting more than 7 days.")
    for i, r in enumerate(nudges):
        with st.expander(f"{person_label(r)} · {r['status']} · {r['days']} days ago"):
            if st.button("Draft nudge", key=f"nudge_btn_{i}"):
                ss[f"nudge_{i}"] = draft_nudge(r["name"], r["days"], r.get("notes"))
            if f"nudge_{i}" in ss:
                copy_box("Copy into LinkedIn", ss[f"nudge_{i}"])
                if st.button("I sent the nudge", key=f"nudged_{i}"):
                    update_tracker(r["name"], r["company"], next_step="Nudged, wait for reply")

    st.subheader(f"Due for a check-in ({len(check_ins)})")
    if not check_ins:
        st.caption("Nobody due. Check-ins come up 4 weeks after a chat.")
    for i, r in enumerate(check_ins):
        with st.expander(f"{person_label(r)} · last contact {r['days']} days ago"):
            if st.button("Draft check-in", key=f"ci_btn_{i}"):
                ss[f"ci_{i}"] = draft_check_in({"name": r["name"]},
                                               r.get("notes") or "No notes saved.",
                                               max(1, r["days"] // 7))["body"]
            if f"ci_{i}" in ss:
                copy_box("Copy into LinkedIn", ss[f"ci_{i}"])
                if st.button("I sent the check-in", key=f"ci_sent_{i}"):
                    update_tracker(r["name"], r["company"], status="Checked in",
                                   next_step="Check in again later")

    st.subheader("Update a status")
    pick = st.selectbox("Person", range(len(rows)), format_func=lambda i: person_label(rows[i]))
    status = st.selectbox("New status", STATUSES)
    if st.button("Update status"):
        update_tracker(rows[pick]["name"], rows[pick]["company"], status=status)


def load_pdf():
    """Fill the paste box from the uploaded PDF so it can be checked before parsing."""
    f = ss.get("profile_pdf")
    if f is None:
        return
    text = pdf_to_text(f)
    ss.pdf_unreadable = not text
    if text:
        ss.profile_text = text


def load_my_pdf():
    f = ss.get("my_pdf")
    if f is not None and (text := pdf_to_text(f)):
        ss.my_text = text


def my_profile_section():
    saved = load_my_profile()
    with st.expander("Your own profile " + ("(saved)" if saved else "(add once to find common ground)"),
                     expanded=not saved):
        st.file_uploader("Upload your LinkedIn PDF", type="pdf", key="my_pdf", on_change=load_my_pdf)
        if "my_text" not in ss:
            ss.my_text = saved
        st.text_area("Or paste your profile", height=200, key="my_text")
        if st.button("Save my profile", disabled=not ss.my_text.strip()):
            save_my_profile(ss.my_text)
            st.success("Saved on this Mac (my_profile.txt, never uploaded to GitHub).")


def tab_profile():
    my_profile_section()
    st.divider()
    st.file_uploader("Upload their LinkedIn PDF (on their profile: More → Save to PDF)",
                     type="pdf", key="profile_pdf", on_change=load_pdf)
    if ss.get("pdf_unreadable"):
        st.warning("Couldn't read text from that PDF (it may be a scan). Paste the profile instead.")
    text = st.text_area("Or paste their profile (LinkedIn About + Experience, bio, etc.). "
                        "An uploaded PDF fills this box so you can check it first.",
                        height=300, key="profile_text")
    if st.button("Parse profile", disabled=not text.strip()):
        with st.spinner("Reading profile..."):
            ss.profile = parse_profile(text)
            for k in ("brief", "common", "prep", "linkedin", "outreach", "followup", "slots", "reply"):
                ss.pop(k, None)
    if "profile" in ss:
        st.json({k: v for k, v in ss.profile.items() if k != "raw"})


def tab_brief():
    if not need("profile", "Parse a profile first."):
        return
    if st.button("Generate brief (uses web search)"):
        with st.spinner("Researching... this can take a minute."):
            ss.brief = make_brief(ss.profile)
    if "brief" in ss:
        b = ss.brief
        if b["unflagged"]:
            st.warning("These facts have no source and no [UNVERIFIED] tag. Check them:\n\n"
                       + "\n".join(f"- {u}" for u in b["unflagged"]))
        st.markdown(b["markdown"])
        with st.expander(f"Sources searched ({len(b['sources'])})"):
            for s in b["sources"]:
                st.markdown(f"- [{s['title']}]({s['url']})")

    st.divider()
    st.subheader("Common ground")
    me = load_my_profile()
    if not me:
        st.info("Save your own profile in the Profile tab to see what you have in common.")
        return
    if st.button("Find what we have in common"):
        with st.spinner("Comparing profiles..."):
            ss.common = find_common_ground(ss.profile, me)
    if "common" in ss:
        st.markdown(ss.common)
        st.caption("Outreach drafts will use the strongest overlap as the hook.")


def tab_outreach():
    if not need("brief", "Generate a brief first."):
        return
    p = ss.profile
    goal = st.text_input("Your goal for this chat", DEFAULT_GOAL, key="goal")
    channel = st.radio("Channel", ["LinkedIn", "Email"], horizontal=True)

    if channel == "LinkedIn":
        if st.button("Draft LinkedIn note + DM"):
            with st.spinner("Drafting..."):
                ss.linkedin = draft_linkedin(p, ss.brief["markdown"], goal, ss.get("common", ""))
        if "linkedin" in ss:
            note = ss.linkedin["note"]
            copy_box(f"Connection note ({len(note)}/{NOTE_LIMIT} characters)", note)
            if len(note) > NOTE_LIMIT:
                st.warning("Too long for LinkedIn. Trim it before sending.")
            copy_box("First DM (send after they accept)", ss.linkedin["dm"])
            if st.button("I sent it on LinkedIn"):
                update_tracker(p.get("name"), p.get("company"), status="Sent on LinkedIn",
                               next_step="Wait for accept")
    else:
        if st.button("Draft email"):
            with st.spinner("Drafting..."):
                ss.outreach = draft_outreach(p, ss.brief["markdown"], goal, ss.get("common", ""))
        if "outreach" in ss:
            subject, body = email_editor("out", ss.outreach)
            gmail_button("out", subject, body)
            if st.button("I sent the email"):
                update_tracker(p.get("name"), p.get("company"), status="Sent email",
                               next_step="Wait for reply")


def tab_reply():
    people = []
    if ss.get("profile", {}).get("name"):
        people.append({"name": ss.profile["name"], "company": ss.profile.get("company") or ""})
    for r in ss.get("tracker", []):
        if not any(r["name"] == x["name"] and r["company"] == x["company"] for x in people):
            people.append({"name": r["name"], "company": r["company"]})
    if not people:
        st.info("Parse a profile, or load your tracker in the Today tab, to pick who replied.")
        return

    who = st.selectbox("Who replied?", people, format_func=person_label)
    mine = st.text_area("Your last message to them (optional, gives context)", height=100)
    theirs = st.text_area("Paste their reply", height=150)
    offer_times = st.checkbox("If they said yes, offer my open times", value=True)

    if st.button("Read reply and draft response", disabled=not theirs.strip()):
        with st.spinner("Reading..."):
            t = triage_reply(theirs)
            slots = []
            if t["intent"] == "yes" and offer_times:
                try:
                    from agent.schedule import open_slots
                    slots = open_slots(limit=3)
                except Exception as e:
                    st.warning(f"Couldn't read your calendar, so no times offered: {e}")
            ss.reply = {"who": who, "triage": t,
                        "draft": draft_reply_response(who["name"], mine, theirs, t, slots)}

    if "reply" in ss:
        r = ss.reply
        st.markdown(f"**They said:** {r['triage']['intent']}. {r['triage']['summary']}")
        copy_box("Your reply (copy into LinkedIn)", r["draft"])
        status, next_step = INTENTS[r["triage"]["intent"]]
        if st.button(f"Update tracker: {status} / {next_step}"):
            update_tracker(r["who"]["name"], r["who"]["company"], status=status, next_step=next_step)


def tab_schedule():
    if not need("profile", "Parse a profile first."):
        return
    length = st.selectbox("Length (minutes)", [20, 30, 45], index=1)
    if st.button("Find open slots"):
        from agent.schedule import open_slots
        try:
            ss.slots = open_slots(length=length)
        except Exception as e:
            st.error(f"Calendar error: {e}")
    if ss.get("slots"):
        slot = st.radio("Pick a slot", ss.slots, format_func=lambda s: s.strftime("%a %d %b, %I:%M %p"))
        email = st.text_input("Their email (optional)")
        goal = st.text_input("Goal", "Coffee chat", key="sched_goal")
        if st.button("Create invite draft"):
            from agent.schedule import draft_invite
            try:
                link = draft_invite(ss.profile, slot, length, email or None, goal)
                st.success(f"Draft event created, no email sent. [Open in Calendar]({link})")
                update_tracker(ss.profile.get("name"), ss.profile.get("company"),
                               status="Meeting booked", next_step=f"Chat on {slot:%d %b}")
            except Exception as e:
                st.error(f"Calendar error: {e}")
    elif "slots" in ss:
        st.warning("No free slots in the next 7 days.")


def tab_prep():
    if not need("brief", "Generate a brief first (and common ground, for a better prep sheet)."):
        return
    p = ss.profile
    goal = st.text_input("Your goal for this chat", ss.get("goal", DEFAULT_GOAL), key="prep_goal")
    if "common" not in ss:
        st.caption("Tip: run Common ground in the Brief tab first so the plan uses your overlaps.")
    if st.button("Make prep sheet"):
        with st.spinner("Preparing your chat plan..."):
            ss.prep = make_chat_prep(p, ss.brief["markdown"], ss.get("common", ""),
                                     load_my_profile(), goal)
    if "prep" in ss:
        st.markdown(ss.prep)
        name = (p.get("name") or "chat").lower().replace(" ", "-")
        st.download_button("Download prep sheet", ss.prep, file_name=f"prep-{name}.md")


def tab_followup():
    if not need("profile", "Parse a profile first."):
        return
    p = ss.profile
    kind = st.radio("Type", ["Thank-you", "Check-in"], horizontal=True)
    notes = st.text_area("Your notes from the chat", height=180)
    weeks = st.number_input("Weeks since the chat", 1, 52, 4) if kind == "Check-in" else None
    if st.button("Draft follow-up", disabled=not notes.strip()):
        with st.spinner("Drafting..."):
            ss.followup = (draft_thank_you(p, notes) if kind == "Thank-you"
                           else draft_check_in(p, notes, weeks))
    if "followup" in ss:
        subject, body = email_editor("fu", ss.followup)
        copy_box("Or copy for LinkedIn", body)
        gmail_button("fu", subject, body)
        if st.button("I sent it"):
            status = "Chatted" if kind == "Thank-you" else "Checked in"
            # Notes are saved so future check-ins can use them.
            update_tracker(p.get("name"), p.get("company"), status=status,
                           next_step="Check in in ~4 weeks", notes=notes)


tabs = st.tabs(["Today", "1. Profile", "2. Brief", "3. Outreach", "4. Reply",
                "5. Schedule", "6. Chat prep", "7. Follow-up"])
for tab, render in zip(tabs, [tab_today, tab_profile, tab_brief, tab_outreach, tab_reply,
                              tab_schedule, tab_prep, tab_followup]):
    with tab:
        render()
