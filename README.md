# coffee-chat-agent

AI agent that helps me prep for and follow up on networking coffee chats.
**Drafts only. I always hit send.**

## What it does

| Tab | What happens | Model |
|---|---|---|
| Today | Who hasn't replied in 7+ days (nudge draft) and who is due a check-in after 4+ weeks. One-click status updates | Haiku / Sonnet |
| 1. Profile | Upload their LinkedIn PDF (More → Save to PDF) or paste a profile, get clean fields. The PDF is read on your Mac | Haiku |
| 2. Brief | Prep brief with web search. Every fact has a source link or is marked `[UNVERIFIED]` | Sonnet |
| 3. Outreach | LinkedIn connection note (under 300 chars) + first DM with copy buttons, or an email saved to Gmail drafts | Sonnet |
| 4. Reply | Paste their LinkedIn reply: it reads yes / no / later / question, drafts your response (with your open times if yes) and updates the tracker | Haiku + Sonnet |
| 5. Schedule | Finds open slots in your calendar, creates a `[DRAFT]` event without emailing anyone | Haiku |
| 6. Follow-up | Thank-you or check-in drafted from your notes; notes are saved for future check-ins | Sonnet |

The tracker is a Google Sheet that updates when you click "I sent it" buttons.

**Why no LinkedIn automation:** LinkedIn has no API for personal messages, and bots or scraping break its rules.
So the app drafts, you copy-paste and send, and the Today tab works purely from tracker dates.

## Setup

1. Install:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Anthropic:** get an API key at console.anthropic.com. Make sure web search is enabled for your org in the Console.
3. **Google (one time):**
   - Go to console.cloud.google.com, create a project.
   - Enable the **Google Sheets API**, **Google Calendar API** and **Gmail API**.
   - OAuth consent screen: External, add yourself as a test user.
   - Credentials: Create OAuth client ID, type **Desktop app**, download it as `credentials.json` into this folder.
   - Create a Google Sheet for the tracker. Copy its ID from the URL (`/d/<THIS PART>/edit`).
4. Fill in `.env` (copy from `.env.example`).
5. Run:
   ```bash
   streamlit run app.py
   ```
   The first Google action opens a browser to log in. After that, `token.json` is reused.

## Evals

Save 5-6 real profiles as `.txt` files or LinkedIn PDFs in `evals/profiles/` (they are gitignored, so they stay off GitHub), then:

```bash
python evals/run_evals.py
```

For each profile it generates a brief and checks two things:
- **Unflagged facts:** bullets with no source link and no `[UNVERIFIED]` tag.
- **Wrong facts:** claims that contradict the pasted profile (judged by Haiku).

Re-run after every change to `agent/prompts.py`. Full briefs go to `evals/results/`.

## Safety

- The code never sends email. `integrations/gmail.py` only creates drafts.
  (Google's `gmail.compose` scope would technically allow sending; the code just never does.)
- Calendar events are created with `sendUpdates="none"` and titled `[DRAFT]`. Send the invite from Google Calendar yourself.
- `.env`, `credentials.json`, `token.json` and eval profiles are gitignored.

## Layout

```
app.py              Streamlit app, one tab per step
agent/              Claude calls, prompts, and one file per step
integrations/       Google Sheets, Calendar, Gmail (drafts only)
evals/              profiles + run_evals.py
```
