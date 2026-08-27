---
name: capture-profile
description: Use to build or update the applicant's career profile from every available source (resume, GitHub, connected LinkedIn/Naukri, portfolio URLs) plus targeted metric-mining questions. Auto-harvests first, asks only for gaps. Writes ~/.career-copilot/profile.json — the single source of truth every other step reads.
---

# Capture profile (Step 1)

Goal: `~/.career-copilot/profile.json` — rich raw material for a great resume. `mkdir -p ~/.career-copilot`.
Strategy: **auto-harvest from every source first, then ask only for gaps.** Maximize collected,
minimize asked.

## Reading documents (resume, payslip, offer letter) — use the Read tool
The Claude Code **Read tool parses PDFs and images natively** (text layer + rendered-page vision) —
**no external dependency** (`pdftotext`/poppler NOT required; works in any Claude Code session).
Conventions so it never breaks:
- PDF or image (PNG/JPG of a doc) → Read the path directly.
- >10-page PDF → pass the `pages` arg.
- Scanned/image-only PDF → the rendered-page vision path still extracts; if truly unreadable, ask
  the user to paste the text.
- `.docx`/other → convert first (pandoc/`textutil`) or ask for a PDF/paste. Never assume a shell
  extractor exists.

## Harvest (fan out; browser is serial)
First read `profile.contact.links` — use handles/URLs already saved by `connect-portal`; only ask
for a source that isn't connected yet. Dispatch subagents in PARALLEL for source-bound work; each
returns normalized JSON, not raw dumps (token-lean — the main thread never sees the raw pages):
- **Resume** — parse the user's file/paste into structured entries.
- **GitHub** — `curl -s "https://api.github.com/users/USER/repos?per_page=100&sort=pushed"` (public,
  no auth). Infer real projects + skills from languages/topics/pinned/READMEs.
- **Portfolio / personal site / Google Scholar** — WebFetch the URLs the user shares.

Then, **serially** (one shared browser, via `connect-portal`'s session):
- **LinkedIn own profile** → `browser_navigate` to own profile → `browser_snapshot`: experience,
  education, skills, certs, recommendations, projects. Own-profile read only.
- **Naukri own profile** — same, where connected.
If a portal isn't connected, offer `connect-portal`; don't block on it.

## Metric-mining interview (gaps only — don't re-ask what we harvested)
- Per role: quantified impact (before/after, %, $, users, latency, scale, time saved).
- Seniority/scope: team size led, ownership, on-call, cross-team, design authority.
- Differentiators: awards, certs, publications, talks, patents, open-source, target keywords.
Ask highest-value gaps first; stop when the profile is strong enough. One topic at a time.

## Timeline reconciliation (sources go stale + disagree)
Every fact carries `source` + `as_of`. Merge duplicate experience/education/projects across sources
by (company, role, overlapping dates). On conflict (résumé "Present" vs LinkedIn end-date), prefer
the most recent/authoritative source but **surface it with both values + dates and ask** — never
silently pick. Order by date; flag gaps (unexplained time) and overlaps. Store the reconciled
`timeline[]`; downstream reads it, not any single stale source.

## Re-entry
Re-pull live sources (GitHub/LinkedIn are cheap), then ask only "anything changed?" for the rest.
Patch; don't rebuild.

## Schema (`~/.career-copilot/profile.json`)
```json
{
  "name": "",
  "contact": { "email": "", "phone": "", "location": "", "links": {} },
  "current": { "title": "", "company": "", "years_experience": 0 },
  "summary": "",
  "experience": [ { "title": "", "company": "", "start": "YYYY-MM", "end": "YYYY-MM|present",
    "scope": { "team_size": 0, "ownership": "", "cross_functional": "" },
    "bullets": [ { "text": "", "impact": "", "tools": [] } ],
    "sources": [], "as_of": "YYYY-MM-DD" } ],
  "timeline": [ { "kind": "experience|education|project", "label": "", "start": "", "end": "",
    "canonical_of": [], "conflicts": [] } ],
  "projects": [ { "name": "", "desc": "", "tools": [], "link": "", "impact": "" } ],
  "skills": { "languages": [], "frameworks": [], "tools": [], "domains": [] },
  "education": [ { "degree": "", "school": "", "year": "" } ],
  "achievements": [], "certifications": [], "publications": [], "talks": [], "awards": [],
  "open_source": [], "portfolio_links": [], "spoken_languages": [], "target_keywords": [],
  "personal": { "dob": "", "nationality": "", "photo_path": "", "marital_status": "" },
  "updated": "YYYY-MM-DD"
}
```
`personal.*` stays empty unless a target locale needs it (see `tailor-resume` locales). Write the
file, give a one-line summary + any surfaced conflicts, then point at `score-jd`.
