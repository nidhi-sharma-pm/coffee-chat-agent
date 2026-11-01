"""Every prompt lives here. Edit these, then re-run evals/run_evals.py."""

TONE = (
    "Tone: warm, short, specific. No flattery, no buzzwords, no 'I hope this finds you well'. "
    "Sound like a real person, not a template."
)

HOOK = """How to use common ground (follow exactly):
- Only use an overlap if it is STRONG and specific: the same college, the same company (past
  or present), or very similar work (same domain, same kind of product, same career switch).
- Never use country, nationality, city or region (for example "India" or "Bangalore"), and
  never generic things like "both love tech" or "both in product".
- Don't announce it. No "we both", "like you", "same as you", "fellow", "we have in common".
  Instead, mention the fact about ME in passing, so they notice the link themselves.
  Good: "I spent two years as an engineer at a fintech startup before moving into product."
  Bad: "Like you, I moved from engineering to product!"
- One light mention, at most one sentence. The message stays about them and the ask.
- If there is no strong overlap, leave it out and use one specific detail from the brief
  that is NOT marked [UNVERIFIED]."""

PROFILE_EXTRACT = """Extract fields from this pasted profile. Use ONLY what the text says.
If a field is not in the text, use null. Never guess or fill gaps.

Return JSON with exactly these keys:
name, current_role, company, past_roles (list of strings), education (list of strings),
location, topics (list of strings: what they post or talk about), linkedin_url

<profile>
{profile}
</profile>"""

BRIEF = """Write a prep brief for a coffee chat with this person.

<profile>
{profile}
</profile>

Search the web for recent work, talks, posts or company news about them. Then write markdown
with these sections: ## Who they are, ## Recent work and news, ## Talking points, ## Questions to ask.

Hard rules:
- In the first two sections, every bullet states one fact and ends with its source as a
  markdown link, like [source](https://...).
- If you cannot find a source for a fact, end that bullet with [UNVERIFIED].
- Facts from the pasted profile may cite [source](profile) instead of a URL.
- If a search result might be a different person with the same name, leave it out.
- Never guess. Fewer true bullets beat more shaky ones.
- Talking points and questions are your suggestions, so they need no source."""

OUTREACH = """Draft a first message asking {name} for a 20-minute coffee chat.

About me: {me}
My goal for this chat: {goal}

<profile>
{profile}
</profile>

<brief>
{brief}
</brief>

<common_ground>
{common}
</common_ground>

{tone}
{hook}
Under 120 words.
End with an easy yes/no ask. First line must be "Subject: ..." then a blank line, then the body."""

THANK_YOU = """Draft a thank-you note to {name} after our coffee chat today.

About me: {me}

<my_notes>
{notes}
</my_notes>

{tone}
Under 100 words. Refer to one or two specific things from my notes. If my notes include a
promise I made (to send something, intro someone), say I'm doing it. Do not invent details.
First line must be "Subject: ..." then a blank line, then the body."""

CHECK_IN = """Draft a light check-in to {name}. We had a coffee chat {weeks} weeks ago.

About me: {me}

<my_notes>
{notes}
</my_notes>

{tone}
Under 90 words. Share one short update or something useful to them tied to my notes.
No ask beyond staying in touch, unless my notes say otherwise. Do not invent details.
First line must be "Subject: ..." then a blank line, then the body."""

INVITE = """Write a 2-sentence calendar invite description for a coffee chat between {me_name}
and {name} ({role} at {company}). Mention the goal: {goal}. Plain text, no greeting."""

EVAL_JUDGE = """You are checking a prep brief for factual errors.

<pasted_profile>
{profile}
</pasted_profile>

<brief>
{brief}
</brief>

List every claim in the brief that CONTRADICTS the pasted profile (wrong company, wrong role,
wrong school, wrong dates, wrong person). Claims the profile simply doesn't mention are fine.

Return JSON: {{"contradictions": [{{"claim": "...", "why": "..."}}]}}
Return {{"contradictions": []}} if there are none."""

LINKEDIN = """Draft LinkedIn outreach to {name}.

About me: {me}
My goal for this chat: {goal}

<profile>
{profile}
</profile>

<brief>
{brief}
</brief>

<common_ground>
{common}
</common_ground>

{tone}
Write two messages:
1. "note": a connection request note. HARD LIMIT 280 characters including spaces.
   Follow the common ground rules below.
2. "dm": the first message to send after they accept. Under 90 words. Ask for a
   20-minute chat with an easy yes/no. Don't repeat the note's detail word for word.

{hook}

Return ONLY JSON: {{"note": "...", "dm": "..."}}"""

SHORTEN = """Shorten this LinkedIn note to under {limit} characters. Keep the specific detail
and the ask. Return only the note.

{text}"""

NUDGE = """Draft a gentle LinkedIn follow-up to {name}. I messaged them {days} days ago
asking for a short coffee chat and haven't heard back.

Context from my tracker: {context}

{tone}
Under 50 words. No guilt, no "just bumping this". Make it easy to say yes or no.
Return only the message."""

REPLY_TRIAGE = """Someone replied to my coffee chat request. Classify their reply.

<reply>
{reply}
</reply>

intent must be one of:
- "yes": they agreed to chat
- "no": they declined
- "later": they're open but busy now
- "question": they asked something before deciding

Return ONLY JSON: {{"intent": "...", "summary": "one short sentence on what they said"}}"""

REPLY_DRAFT = """Draft my LinkedIn reply to {name}.

About me: {me}

<my_last_message>
{my_message}
</my_last_message>

<their_reply>
{reply}
</their_reply>

Their intent: {intent}
My open times (only use these if they said yes; "none" means ask what suits them):
{times}

{tone}
Under 80 words. No subject line.
- yes: thank them and offer 2-3 of my open times, or ask what suits them.
- no: thank them warmly, no pushing.
- later: thank them and say I'll reach out again in a few weeks.
- question: answer only from what I've told you. If you can't, write [ADD ANSWER] where I need to fill in.
Return only the message."""

COMMON_GROUND = """Compare my profile with theirs to find genuine common ground for a coffee chat.

<my_profile>
{me}
</my_profile>

<their_profile>
{them}
</their_profile>

Write markdown with these sections:

## What we have in common
Bullets. Each names the overlap and ends with (strong), (medium) or (light).
Only count overlaps visible in BOTH profiles: same school, company, city, industry, role,
career switch, side projects, topics or communities. Don't stretch: "both like tech" is not
common ground. Ignore country, nationality, city and region entirely. If there's little
overlap, say so honestly.

## Where our paths differ
1-3 bullets on things they've done that I'm trying to do. These make the best questions.

## How to use this in the chat
- **Opener:** one natural first line that mentions the relevant fact about me in passing,
  without saying "we both" or "like you".
- **Bridge questions:** 3 questions that link my experience to theirs.
- **What I can offer:** one thing from my profile that could be useful to them.
- **Avoid:** one thing not to do (for example, overplaying a weak link)."""

CHAT_PREP = """Write my one-page prep sheet for a 20-minute coffee chat with {name}.

My goal for this chat: {goal}

<my_profile>
{me}
</my_profile>

<their_profile>
{them}
</their_profile>

<brief>
{brief}
</brief>

<common_ground>
{common}
</common_ground>

Write markdown with these sections. Keep it scannable: I'll read it 5 minutes before the call.

## My 30-second intro
3-4 sentences in first person, tailored to them: who I am (mention the fact that links to
them in passing, never "we both" or "like you") and why I wanted to talk. Natural, not a pitch.

## 20-minute plan
A short timeline: warm open (use the strongest overlap), main questions, what I can offer,
close. Give minutes for each part.

## Questions, best first
6 questions. Mark the 2 I must ask with **(must ask)**. Build them on the brief and common
ground, never on facts marked [UNVERIFIED]. No questions they could answer with a Google search.

## If the conversation stalls
2 backup topics from the brief or common ground.

## Close and ask
One specific, small ask that fits my goal (advice, a resource, an intro to one person).
Not a job. Plus the exact line to say.

## Don't
2 things to avoid with this person."""
