---
description: Reload full Telos project context — state, phase status, infra, and what's next
---

Restore working context on the Telos project. Do this before anything else, and
do not start changing code until you've reported back.

1. Read `TELOS_STATE.md` in the repo root. That is the living handoff document:
   what's live, infrastructure, phase status, open items, gotchas, conventions.
   It carries a one-line index of every settled decision; `TELOS_ARCHIVE.md`
   holds the reasoning behind each, and is worth opening only when you are
   about to reopen one of them.
2. Skim `TELOS_V2_SPEC.md` and `TELOS_V2_ADDENDUM.md` for the phase plan. The
   addendum reorders the phases and adds the mobile/PWA work, so it wins where
   they disagree.
3. Check the actual current state rather than trusting the docs:
   - `git log --oneline -12` and `git status --short`
   - `git branch -vv` (unmerged phase branches are work held for sign-off)
   - `railway status` to confirm the deploy is Online
   - `curl -sS -o /dev/null -w "%{http_code}" https://telosapp.co.uk/login`
4. If anything in `TELOS_STATE.md` contradicts what you actually find, trust
   the repo and the live service, and say so.

Then report back, briefly:
- which phases are live and what shipped most recently
- what is committed but NOT merged (held for sign-off)
- the open items that need the owner — especially the phone test of Phase 0.6,
  the real Stripe checkout test, and the `db.py` connection-check decision
- what the next phase is in the addendum's order

Do not start the next phase, modify code, or merge anything until the owner
says what they want. Offer to bring the local dev server up if useful:

    railway run .venv\Scripts\python.exe app.py

Full test suite, if a sanity check is wanted:

    railway run .venv\Scripts\python.exe tests\run_all.py
