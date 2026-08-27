# Career Copilot

A Claude Code plugin: a resumable wizard to help applicants **apply faster, get interviews, and
get hired**. Runs as instruction skills — Claude does the work, state persists in
`~/.career-copilot/`.

## Install
```
/plugin marketplace add /Users/adarshbattu/workspace/projects/career-copilot
/plugin install career-copilot
npx playwright install chromium   # once, for portal auth (connect-portal)
```
Then run `/career-wizard` (optionally paste or link a job description).

## What works today
- **connect-portal** — log into LinkedIn / Naukri / company sites in a real browser (bundled
  Playwright MCP, persistent profile). Login persists for harvest + later steps. Opt-in;
  cookies stored locally only.
- **capture-profile** — auto-harvest from resume + GitHub + connected LinkedIn/Naukri + portfolio
  URLs → reconcile stale/conflicting sources into one canonical timeline → mine quantified impact.
  Writes `profile.json`.
- **preferences** — curate roles, seniority, location, comp, and deal-breakers (hard filters) →
  `preferences.json`; drives find-jobs filtering and tailor-resume locale.
- **find-jobs** — discover roles across web + connected portals + company pages (multi-agent
  fan-out, serial browser), dedup + staleness-filter, score each with the `score-jd` rubric →
  ranked `jobs.json`. Or paste one JD for the quick path.
- **score-jd** — paste/link a JD → transparent fit score + gap breakdown → `jobs.json`.
- **tailor-resume** — craft "The Ledger": one balanced, ATS-parseable, locale-aware resume
  (HTML→PDF) + cover letter. Optional multi-agent variant+critic panel with a truthfulness veto.
- **apply** — assemble + submit a pursued job with per-application human confirmation (connector
  or manual hand-off), logged to `applications.json`. Never auto-submits.

## Design & data
- Resume template: `skills/tailor-resume/assets/resume-template.html` (open it standalone to
  preview). Locale conventions: `skills/tailor-resume/assets/locales.json`.
- Browser cookies: `~/.career-copilot/browser-profile/` (local only, sensitive).
- Full design/roadmap: `docs/career-copilot-plan.md`. Template refs: `docs/visualcv-template-urls.md`.

## Not built yet
Reach-the-right-people outreach (Step 4.5), tracking/offers (Step 7), profile grooming, interview
prep, feedback loop. These grow onto the same `~/.career-copilot/` data model and the multi-agent
patterns in the plan.
