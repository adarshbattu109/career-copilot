---
name: score-jd
description: The scoring engine. Score a specific job description against the applicant's profile (quick path), OR rescore ALL saved jobs when the profile/preferences change (feedback loop). Transparent fit score + gap breakdown → ~/.career-copilot/jobs.json. Used by find-jobs too — one rubric, no duplication.
---

# Score a job (Step 4 — quick path)

Score ONE job description against `~/.career-copilot/profile.json`. This is the fast lane:
the user already found the JD elsewhere; we score fit and expose gaps, no discovery needed.

## Flow
1. Load `profile.json`. If missing → run **capture-profile** first.
2. Get the JD: pasted text, a file path, or a URL (fetch it). Extract: title, seniority,
   required + preferred skills, location/remote, and posting date if present.
3. **Staleness:** if a posting date is present and >14 days old, flag it — still scoreable,
   just note the age.
4. Score with this rubric and **show the breakdown** — never a bare number:

   | Dimension | Weight | Based on |
   |---|---|---|
   | Skills overlap | 40% | required/preferred skills vs. profile.skills + project tools; normalize with `skills/tailor-resume/assets/skill-keywords.json` **and semantic synonyms** (the bank is a seed, not a whitelist — match beyond listed terms so real overlaps aren't missed) |
   | Seniority / title fit | 25% | JD seniority vs. profile.current + years_experience |
   | Location / remote fit | 20% | JD location vs. profile.contact.location (ask if unknown) |
   | Preference fit | 15% | comp/stage/role preferences — until Step 3 exists, ask inline or skip and renormalize the other weights to 100% |

5. Output:
   - **Score /100** with the per-dimension breakdown and one-line reasons.
   - **Gaps** — required skills the profile lacks (this feeds resume tailoring AND is the
     honest input for profile grooming later).
   - **Verdict** — a plain recommendation: strong / worth-tailoring / stretch / skip.
6. Append to `~/.career-copilot/jobs.json` (create if absent):
```json
{ "jobs": [
  { "id": "slug-or-timestamp", "title": "", "company": "", "url": "", "posted": "",
    "score": 0, "breakdown": {}, "gaps": [], "verdict": "", "status": "scored",
    "jd_text": "", "added": "YYYY-MM-DD" }
] }
```
Then offer to tailor a resume for it (`tailor-resume`) if the verdict is worth pursuing.

## Rescore mode (re-evaluate saved jobs — the feedback loop)
When `profile.json` or `preferences.json` changes (new/corrected skill, comp or deal-breaker update),
re-run scoring over **all** of `jobs.json` — don't leave stale scores. Same rubric, current profile.
- Update `score`, `breakdown`, `gaps`, `verdict` in place; add a short `note` on **what moved and why**
  (e.g. "61→77: GenAI/LLM validation added to profile").
- Report the **movers** (biggest changes) so the impact is visible.
- Fast/local: score every entry in one concurrent pass. Entries without `jd_text`
  (meta-only/provisional) stay flagged as needing a full JD.
This engine serves both `find-jobs` (new jobs) and post-change rescoring — one rubric.

## Don't
Don't inflate the score to be encouraging. An honest "stretch" that surfaces real gaps is more
useful than false confidence.
