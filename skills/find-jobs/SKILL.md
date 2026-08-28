---
name: find-jobs
description: Use to discover relevant jobs across multiple sources (HTTP job APIs, connected LinkedIn/Naukri/Indeed, company career pages), dedup and staleness-filter them, then score each against the profile using the score-jd rubric. Multi-agent fan-out for speed; writes ranked results to ~/.career-copilot/jobs.json for the user to mark pursue/pass/maybe.
---

# Find jobs (Step 4 — discovery)

Discover many roles, then rank them. (For a single JD the user already found, use `score-jd` — the
quick path.) Reuses `score-jd`'s scoring rubric — don't reinvent it; score discovered jobs the same
way.

## Criteria
Read `~/.career-copilot/preferences.json` if present (roles, seniority, location/remote, comp,
company stage, **deal-breakers as hard filters**). If absent, derive targets from
`profile.json.target_keywords` + `current` and confirm a few criteria inline (don't build the full
Step-3 flow here).

## Multi-modal sweep — API-FIRST, browser only as fallback
Prefer HTTP APIs (no browser needed, structured, fast, ToS-clean, parallelizable). Only use the
shared browser for login-gated or no-API sources. Each source returns normalized listings
(title, company, location, url, posted_date, jd_text) — never raw pages (token-lean).

**Speed:** fire all API-source calls **concurrently** (background curl `&` + `wait`, or one subagent
per source) — never serialize them; then dedup + score in a single fast local pass. Multi-query per
source (role × location) also runs concurrently. Only browser sources are serial (shared browser).

**1. API sources (HTTP + key — fan out in PARALLEL, no Playwright).** Read keys from
`~/.career-copilot/config.json` (`{ "adzuna": {"app_id","app_key"}, "jooble": {"key"}, "serpapi": {"key"} }`).
Use whichever keys are present; skip the rest and say so.
- **Adzuna** (free dev tier; global) — `GET api.adzuna.com/v1/api/jobs/<cc>/search/1?app_id=..&app_key=..&what=<role>&where=<city>` where `<cc>` is the country code derived from `preferences.target_countries` (`in`, `gb`, `us`, …), not hardcoded.
- **Jooble** (free key) — `POST jooble.org/api/<key>` with `{keywords, location}`.
- **Remotive** (free, remote roles) — `GET remotive.com/api/remote-jobs?search=<role>`.
- **Google Jobs** — **no official API**; programmatically only via a paid aggregator (SerpApi
  `engine=google_jobs`) if a `serpapi` key exists. Do NOT scrape the Google SERP over raw HTTP
  (unreliable + ToS violation).

**2. Browser sources (serial, via `connect-portal` session — only if no API / login-gated):**
LinkedIn, Naukri, Indeed, company career pages. Browser tools are
`mcp__plugin_career-copilot_playwright__browser_*`. Run **serially** on the one shared browser;
never parallelize it. Best-effort DOM extraction; respect rate limits.

**If no API keys are set** (`~/.career-copilot/config.json` missing/empty): don't just fail — run
**`connect-portal adzuna`** to onboard the user (it walks the free signup, captures the key, saves +
verifies it). Adzuna is the recommended free default. Until a key exists, fall back to browser
sources (serial) and say so.

## Clean up
- **Dedup** cross-source by (normalized company + title + location).
- **Staleness:** flag postings >14 days old (still keep, just mark).
- **Comp vs current (from `preferences.compensation`):** where a posting lists comp, **normalize it
  to `base_currency`** using the `fx` rates (note the `as_of`; if rates are stale/missing, ask or
  refresh — don't silently use a wrong rate), then compute the delta vs `current.total_ctc` and flag
  ▲/▼ (e.g. "▲ +35% vs current"). Always show **native + normalized** amounts. If `expected.min` is
  set, **drop** postings clearly below it (hard filter). Where a posting omits comp, mark "comp
  undisclosed" — don't guess. For cross-country roles, add a **cost-of-living/PPP caveat** (raw FX
  overstates or understates real value). Comp is a filter + surfaced flag, not a fake score dimension.
- Respect source limits: documented max queries/day, min call interval; on throttle back off and
  fall back to the remaining API sources or (serial) browser sources — queue the rest. Disclose the
  policy; no retry-hammering.

## Score + record
Score each deduped job with the `score-jd` rubric (show the per-dimension breakdown + gaps).
Append to `~/.career-copilot/jobs.json` (same schema as `score-jd`), `status: "discovered"`.
**Persist the `jd_text` each source returned** — without it scores can't be reproduced or rescored;
an entry with empty `jd_text` must be flagged as needing a full JD (per `score-jd` rescore rule).
Present a ranked list; the user marks each **pursue / pass / maybe** (updates `status`).
For "pursue" jobs, offer `tailor-resume`. Loop the sweep until the pursue-list hits the user's
target count.

## Run modes (cost control)
- **On-demand** (default): run once now.
- **Weekly digest** (opt-in, not daily): only if the user asks; log what sources ran and what was
  skipped/queued — never hide dropped work behind parallelism.

## Guardrails
Own reads only; human-paced; per-source ToS/rate policy disclosed. Deal-breakers are hard filters,
not soft weights — drop, don't down-rank.
