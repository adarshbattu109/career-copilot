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

### Codex
The skills are harness-agnostic and load in Codex via the plugin manifests in this repo
(`.agents/plugins/marketplace.json` for discovery, `.codex-plugin/plugin.json` for the
plugin). Install:
```
codex plugin marketplace add <repo-path>
codex plugin add career-copilot@career-copilot-mp
```
Note: `commands/` are Claude-relative slash commands and don't map to Codex; prompt
Codex to run the skill you want (e.g. "run the capture-profile skill") instead. Connect
portals still need the Playwright MCP from `.mcp.json`.

## What works today
- **connect-portal** — log into LinkedIn / Naukri / company sites in a real browser (bundled
  Playwright MCP, persistent profile). Login persists for harvest + later steps. Opt-in;
  cookies stored locally only.
- **capture-profile** — auto-harvest from resume + GitHub + connected LinkedIn/Naukri + portfolio
  URLs → reconcile stale/conflicting sources into one canonical timeline → mine quantified impact.
  Writes `profile.json`.
- **preferences** — curate roles, seniority, location, comp, and deal-breakers (hard filters) →
  `preferences.json`; drives find-jobs filtering and tailor-resume locale.
- **find-jobs** — discover roles across job APIs (Adzuna / Jooble / Remotive, fired concurrently) +
  connected portals + company pages, dedup + staleness-filter, score each with the `score-jd` rubric
  → ranked `jobs.json`. Or paste one JD for the quick path. API-first; the browser is fallback only.
- **score-jd** — paste/link a JD → transparent fit score (uses `preferences.json` when present) +
  gap breakdown → `jobs.json`. Verdict is one of strong / worth-tailoring / stretch / skip.
- **tailor-resume** — craft one balanced, ATS-parseable, locale-aware resume (HTML→PDF) + cover
  letter from a chosen template (registry in `assets/templates.json`; default **Classic**, plus
  Zenith and The Ledger). Optional multi-agent variant+critic panel with a truthfulness veto.
- **apply** — assemble + submit a pursued job with per-application human confirmation (connector
  or manual hand-off), logged to `applications.json`. Never auto-submits.

## Design & data
- Resume templates: registry at `skills/tailor-resume/assets/templates.json` (Classic / Zenith /
  The Ledger — open any `.html` standalone to preview). Locale conventions: `assets/locales.json`.
- Browser cookies: `~/.career-copilot/browser-profile/` (local only, sensitive).
- Full design/roadmap: `docs/career-copilot-plan.md`. Template refs: `docs/visualcv-template-urls.md`.

## Quality
- `pytest -q` (7 tests): ATS-safe templates, PDF reading-order, profile/data schema. `claude plugin
  validate` passes.
- `evals/` — `claude plugin eval` behavior cases (scoring verdict vocab, truthfulness veto). Runs
  once `plugin eval` early access is enabled on your account.

## Not built yet
Reach-the-right-people outreach (Step 4.5), tracking/offers (Step 7), profile grooming, interview
prep, feedback loop. These grow onto the same `~/.career-copilot/` data model and the multi-agent
patterns in the plan.
