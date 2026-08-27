# Plan — Career Copilot: balanced resume, portal-auth, rich capture, multi-agent & token-lean

## Context
The `career-copilot` plugin (built this session; repo was otherwise empty) currently has a
quick-path slice: `capture-profile` → `score-jd` → `tailor-resume` (plain `.docx`), plus a
`career-wizard` command. Two new requirements from the user:

1. **Resume** should be **one balanced artifact** — visually stunning yet minimal *and*
   ATS-parseable — inspired by VisualCV templates, using the frontend-design **"The Ledger"**
   direction. (User rejected the two-file split.)
2. The plugin should **use Playwright to open job portals (LinkedIn, Naukri, company sites),
   prompt the user to log in, and persist cookies for later reuse** — the browser-auth pattern
   from the `linkedin-mcp-server` reference, so one login scales across any portal.

Grounding done: reviewed all 36 VisualCV templates (visual) + parsed sample content guides
(Playwright). The stunning-vs-ATS tension dissolves at "minimal" — the genuinely clean
single-column, one-accent, real-text templates are **ATS, Monte, Standard, Zenith, Monaco**
(usage skews hard to these: Monte ~2.07M, Standard ~605k). The **ATS** template's bones (name,
contact line, thin-rule section headers, each entry = role-left/dates-right + bullets, grouped
skills) map exactly onto "The Ledger". The other ~30 (sidebars, photos, skill bars/dots/rings,
image backgrounds) are ATS-risky and avoided. **Correction from the full review:** Arya and
Corporate are NOT clean — their left-margin label gutters are a specific ATS failure mode, so the
Ledger's spine must be decoration only (see Part A hard constraint).

Key architecture win: a **Playwright MCP server is already connected** in this environment
(`mcp__plugin_playwright_playwright__browser_*`). We reuse it rather than bundling our own — Claude
drives the browser through MCP tools; a persistent profile dir handles cookie reuse.

---

## Part A — Resume: "The Ledger" (one balanced artifact)

**Design (locked):**
- Color: `--ink #1A1A1A`, `--paper #FCFCFA`, `--muted #6B6B6B`, `--hair #E4E3DD`,
  `--accent #2F5D62` (muted teal — the one swappable/removable knob; name mark, left spine,
  section ticks only).
- Type: **Fraunces** (name only), **Inter** (body/skim), **JetBrains Mono** (dates, location,
  labels, tech tags — the "ledger" system). Google Fonts `<link>`; all real selectable text.
- Layout: single column, generous margin, hairline left spine; per-entry dates/location
  right-aligned in mono on the title line (reads two-column, single-column in source order).
- Section headings: accent-colored with a thin rule + a small accent left tick-mark (Zenith
  idea) — rhythm/scannability while staying plain text.
- Entry hierarchy: **bold role / regular company / mono right-aligned dates** — visual structure
  from weight + alignment alone, no tables/columns (Standard/Zenith pattern).
- Skills: plain grouped **text** (Soft / Hard / Languages, pipe- or comma-separated) — never
  bars/dots/rings/charts (the #1 ATS failure across the other 30 templates).
- Signature: name lockup (Fraunces name + mono `role · location · open-to` ticker) over the
  mono date-ledger. No animation. Quality floor: mobile-responsive, visible focus,
  `prefers-reduced-motion` respected.
- ATS-safe by construction: single-column DOM in reading order, standard headings
  (Summary/Experience/Projects/Skills/Education), no layout tables, no sidebars, no text-in-images.
- **Hard constraint (template-review finding):** the left spine is pure CSS decoration
  (`border-left`/pseudo-element) — NEVER a margin label-gutter that pushes text into a second
  column (the Arya/Corporate ATS failure mode). One true linear reading order, always.

**Changes:**
- **New `skills/tailor-resume/assets/resume-template.html`** — self-contained (embedded CSS,
  fonts link, no JS), print CSS (`@page A4`, `@media print`), realistic sample content so it
  renders standalone as preview + fill pattern.
- **Edit `skills/tailor-resume/SKILL.md`** — fill template with truthful JD-tailored content
  (keep no-fabrication guardrail); render PDF with **no new dependency** (headless Chrome
  `--print-to-pdf` if present, else instruct browser Print→PDF); keep a plain-text paste fallback
  for form fields; output `~/.career-copilot/resumes/{job_id}.{pdf,html}`; note `--accent` knob.

---

## Part B — Portal auth via the existing Playwright MCP (cookie persistence)

**Approach:** reuse the connected Playwright MCP server. Configure it with a **persistent
profile** so logins survive across sessions — bundle an MCP entry in the plugin (`.mcp.json`)
running the official server with a fixed user-data-dir:
`npx @playwright/mcp@latest --user-data-dir ${HOME}/.career-copilot/browser-profile --browser chromium`
(headed, so the user can complete login/OTP/SSO/captcha). Cookies + localStorage persist in that
dir automatically — that IS "save cookies for later use". No custom playwright code needed.
(`${CLAUDE_PLUGIN_DATA}` is the harness-managed alternative, but we keep the profile under
`~/.career-copilot/` so all career data — and the sensitive cookie store — live in one place the
user can find, back up, and delete; skills reference concrete paths, not the placeholder.)

**Changes (confirmed against docs):**
- **New `.mcp.json`** at the **plugin root** (NOT inside `.claude-plugin/` — it won't load there),
  declaring the Playwright MCP server with the persistent `--user-data-dir` above. Tools resolve
  as `mcp__plugin_career-copilot_playwright__browser_*` (use the full scoped name in any
  permission rule / allowed-tools / hook matcher). `.mcp.json` edits need `/reload-plugins`; the
  server auto-starts when the plugin is enabled and can be toggled in `/mcp`.
- **New `skills/connect-portal/SKILL.md`** (Step 2 connector). Flow:
  1. Args: `linkedin | naukri | indeed | <company-url>`. Disclose ToS/ban risk (esp. LinkedIn)
     and get explicit opt-in before opening anything.
  2. `browser_navigate` to the portal's login URL; tell the user to log in *in the opened
     window*; `browser_wait_for` / user confirms "done".
  3. Verify session via `browser_snapshot` (look for a logged-in signal, e.g. profile menu).
  4. Record status in `~/.career-copilot/portals.json`
     (`{ portal, logged_in, last_verified, notes }`). Cookies persist in the profile dir.
  5. Re-entry: check `portals.json` + a quick `browser_navigate` to confirm the session is still
     live; only re-prompt login if it lapsed.
- **Edit `commands/career-wizard.md`** — add `connect-portal` to routing (Step 2), gated on opt-in.
- **Edit `README.md`** — document the browser-auth capability + the persistent-profile install
  step (`npx playwright install chromium`).

**Guardrails (extend existing set):**
- Browser profile holds live session cookies → sensitive. Store only under
  `~/.career-copilot/browser-profile/` (outside the repo), `chmod 700`, never transmitted,
  never committed.
- Opt-in + ToS/ban-risk disclosed per portal before first open.
- Human approves every outward action (apply/connect/message); human-paced, no scrape-hammering.
- Downstream steps (full job discovery = Step 4, apply = Step 6) reuse this authenticated session
  via the same MCP tools — enabled by this primitive, built later.

---

## Part C — Rich profile capture (maximize data for a great resume)
A great resume needs strong raw material: quantified achievements, seniority/scope signals, and
ATS keywords — not just job titles. Strategy: **auto-harvest from every source first, then probe
only for gaps.** Minimize what we ask the user; maximize what we collect.

**Sources (harvest, reconcile, don't re-ask what we scraped):**
- Resume file (parse) — baseline.
- GitHub API (public) — repos, languages, stars, pinned, contribution signal, README impact.
- **LinkedIn own profile** — via the authenticated Playwright session from Part B
  (`browser_navigate` to own profile → `browser_snapshot`): experience, education, skills,
  certifications, recommendations, projects. Own-profile read only = low ToS risk.
- **Naukri own profile** — same pattern where connected.
- User-shared URLs (portfolio, personal site, Google Scholar) via WebFetch.

**Then — targeted interview (gap-fill + metric mining only):**
- For each role, probe for quantified impact (before/after, %, $, users, latency, scale, time
  saved) — this is what separates a great resume from a list of duties.
- Seniority/scope signals (team size led, ownership, on-call, cross-team, design authority).
- Differentiators: awards, certifications, publications, talks, patents, open-source, notable
  projects, spoken languages, target-role keywords.

**Expanded `profile.json` schema** — add to the existing schema:
`achievements[]`, `certifications[]`, `publications[]`, `talks[]`, `awards[]`, `open_source[]`,
`portfolio_links[]`, `spoken_languages[]`, `target_keywords[]`, and per-experience
`scope { team_size, ownership, cross_functional }`. Keep `sources[]` per field for provenance so
reconciliation conflicts are traceable and surfaced (never silently pick one).

**Timeline / freshness reconciliation (sources go stale and disagree):** a résumé captured months
ago and a LinkedIn updated last week will contradict each other on dates/titles. Build ONE
canonical chronological timeline as the reconciliation backbone:
- Every harvested fact carries `source` + `as_of` (when that source was last updated/captured).
- Merge duplicate experience/education/project entries across sources by (company, role,
  overlapping dates) into a single canonical entry.
- On conflict (e.g. résumé says "Present", LinkedIn shows an end date), prefer the **most recent /
  most authoritative** source but **surface the conflict** with both values + dates and ask —
  never silently pick.
- Order everything by date; auto-detect and flag **gaps** (unexplained time) and **overlaps**
  (concurrent roles) so the resume doesn't confuse a reader or trip an ATS.
- Store as `timeline[]` (sorted, canonical) alongside the raw per-source `experience[]`; the resume
  and scoring read the reconciled timeline, not any single stale source.

**Changes:**
- **Edit `skills/capture-profile/SKILL.md`** — multi-source harvest flow (above), expanded schema,
  metric-mining interview, provenance + conflict surfacing. On re-entry, re-pull live sources and
  ask only "anything changed?" for the rest.

---

## Part D — Locale-aware output (International CV conventions)
CV conventions differ by country (per VisualCV's International guide,
https://www.visualcv.com/international/ — ~48 countries). A US résumé must NOT look like a German
*Lebenslauf* (photo, DOB, signature) or an Indian résumé (often photo + DOB) or a GDPR-conscious
EU CV (no photo/DOB). Targeting Naukri (India) + global portals makes this mandatory, not optional.

**Approach (lazy, extend-on-demand):**
- **New `skills/tailor-resume/assets/locales.json`** — country → conventions:
  `{ term: "Resume"|"CV"|"Lebenslauf", photo: bool, personal_details: ["dob","nationality",
  "marital_status","address"], max_pages, date_format, privacy_notes }`. Seed the targeted set
  (US, UK, India, Germany, UAE/GCC, Canada, Australia); note the VisualCV guide as the source to
  add more when a new target country comes up.
- **Template** (`resume-template.html`) exposes *optional* slots — a photo block and a
  personal-details block — hidden by default, toggled on only when the target locale calls for
  them. Ledger design unchanged; these are conditional additions, not a second layout.
- **`tailor-resume`** determines target country (from the JD / `preferences.json`), applies the
  locale's conventions (term in the heading, which personal fields to show, page target, date
  format), and warns if the profile lacks a field that locale expects.
- **`capture-profile`** stores optional personal fields (`dob`, `nationality`, `photo_path`,
  `marital_status`) **only if** a target locale needs them — asked explicitly, never volunteered,
  and never rendered for locales (US/UK) where they're a liability.

---

## Multi-agent orchestration (supercharge)
The heavy steps fan out to subagents; skills are authored to dispatch them (via the Task/Agent
tool), with the orchestrating session merging results. For large runs the user can opt into the
Workflow tool. **Hard constraint (from Part B): the Playwright MCP is ONE shared browser** — any
step touching a logged-in portal is serial at the browser. So the governing rule is:
**parallelize API / web-search / compute-bound work; serialize (queue) browser-bound work.**

- **Data prep (Part C):** parallel harvest agents — GitHub API, resume parse, portfolio/Scholar
  URLs — return normalized JSON; LinkedIn/Naukri harvest is **queued serially** on the shared
  browser. Barrier → reconcile into the canonical `timeline[]`.
- **Job retrieval (Step 4):** multi-modal sweep — one agent per API/web-search source in parallel
  (each blind to the others, different query angles); browser-portal sources queued serially →
  merge + dedup cross-source → parallel scoring of the deduped set. Loop until the pursue-list
  hits the target count.
- **Resume crafting (Step 5):** judge-panel — generate N tailored variants in parallel
  (impact-first / keyword-first / leadership-first) → parallel critics: an **ATS-parse critic**
  (`pdftotext` reading-order + JD keyword hit-rate), a **recruiter-persona critic** (6-second
  skim), and a **truthfulness auditor** (flags any claim not grounded in `profile.json` — a
  guardrail agent with veto, not just quality) → synthesize the winner, grafting the best *real*
  bullets from runners-up. **Scale to need:** quick = 1 draft + ATS/truthfulness check; thorough =
  full panel.
- **Applying (Step 6):** parallel PREP across queued applications (map form fields, draft
  screening answers from `profile.json`) → **serial submit** (browser), each human-approved.

**Fan-out guardrails:**
- Parallel prep is fine; parallel *sending / applying / connecting* is NOT — every outward action
  stays per-action human-approved and human-paced (ToS/rate limits). Multi-agent must never
  multiply outward actions.
- Concurrency is capped (harness ~10 live agents; browser steps are effectively concurrency-1).
  Log what was queued/skipped so parallelism never hides dropped work.
- The truthfulness auditor's veto is absolute: a variant that wins on ATS but fabricates is killed.

*Implementation note:* the orchestration lives inside the step skills (Step 4 `find-jobs`, Step 5
`tailor-resume`, Step 6 `apply`, Part C `capture-profile`) as subagent-dispatch instructions.
`find-jobs` and `apply` skills are roadmap (from the original 7-step plan), built when their steps
land; they'll carry the fan-out patterns above.

## Token efficiency — caveman + headroom principles (unemployed = cost-sensitive)
Governing principle: no wasted tokens.
- **caveman** — INSTALLED (`caveman@caveman`), active next session. Terse output mode.
- **headroom** — SKIPPED. Its Claude-Code plugin is just hooks that shell out to a `headroom`
  engine binary (Rust/proxy) we didn't install; the hooks would error/timeout on every Bash call.
  So we fold headroom's *compression principles* into the skills manually (below) instead of
  running the engine.

**Caveman — terse:**
- Skills emit compact results (tables/bullets, no filler, no restating the prompt); scoring and
  critique reasons are one line each, not essays.
- SKILL.md files kept lean — they load into context on every trigger. Short, imperative.

**Headroom — context/token budget:**
- **Cache, don't refetch:** `profile.json` / `jobs.json` / stored `jd_text` are the store; never
  re-parse a resume or re-scrape a profile already captured. Re-entry pulls only "what changed".
- **Extract, don't dump:** `browser_evaluate` targeted pulls over full-page snapshots/screenshots;
  `pdftotext` + grep over reading whole files; persist distilled fields, not raw HTML.
- **Subagents = headroom:** fan-out isolates big dumps (page reads, multi-source harvest) and
  returns distilled JSON — the main thread stays lean. The same agents that supercharge also save
  tokens (proven this session: Explore agents returned tables, not screenshots).
- **Model tiering:** cheap model + low effort for mechanical stages (parse, dedup, form-field map);
  strong model only for judgment (scoring, resume crafting, critics). Set per-agent model/effort.
- **Bound fan-out to need:** quick = 1 draft; thorough = full panel — don't spawn critics when one
  draft suffices. Log what was skipped.
- **Scheduling:** weekly digest is opt-in, not daily polling.

Track **tokens/application** as a first-class KPI alongside apply-faster / interview / hire metrics.

## Critical files
- `skills/capture-profile/SKILL.md` (edit — multi-source harvest + expanded schema)
- `skills/tailor-resume/assets/resume-template.html` (new — optional photo/personal-details slots)
- `skills/tailor-resume/assets/locales.json` (new — per-country CV conventions)
- `skills/tailor-resume/SKILL.md` (edit)
- `skills/connect-portal/SKILL.md` (new)
- `.mcp.json` (new — Playwright MCP w/ persistent profile)
- `commands/career-wizard.md` (edit — route connect-portal + capture harvest)
- `README.md` (edit — resume + browser-auth + rich capture)

## Evidence — content patterns from VisualCV samples (parsed via Playwright plugin)
Parsed Software Engineer + Engineering Manager sample guides (`/resume-samples/<role>/`) with
`browser_navigate` + `browser_evaluate`. Concrete patterns to bake into the template + skills:
- **Summary formula:** `[Role] with [N yrs] experience of [top 2–3 skills]. Achieved [top
  achievement w/ metric]. Expert at [X], [Y], [Z].` (quantified, seniority-forward). → capture the
  inputs in `capture-profile`; generate via `tailor-resume`.
- **Experience:** reverse-chronological; bullets not paragraphs; lead with action verbs; quantify
  impact (%, $, users, downloads, time); per-entry header `Company | Title | Dates` (matches the
  Ledger date-right rail); tailor bullets to JD keywords.
- **Skills:** grouped **Soft / Hard / Languages**; explicitly keyword-matched to the JD for ATS.
- **SWE-specific:** a dedicated **Personal Projects** section is a differentiator; export as PDF.
- **Header/contact:** `Name · City, ST · phone · LinkedIn`; professional email address.
These refine Part A (template sections: Summary, Experience, Projects, Skills grouped, Education;
contact line) and Part C (mine the summary-formula inputs + quantified achievements). Visual
template-review findings (all 36) are folded into Part A: accent-only-on-name+headings, thin-rule
+ left tick headings, bold-role/regular-company/right-dates hierarchy, skills as plain text,
spine-as-decoration-not-gutter.

**Reference asset:** all 36 VisualCV "View Template" full-render URLs are captured in
`docs/visualcv-template-urls.md`. Before building `resume-template.html`, open the 5 ATS-clean
full renders (**ats, monte, standard, zenith, monaco**) to lift exact spacing, type scale, and
entry hierarchy for the Ledger — these are the visual reference. (Not opened yet — a build-time
step, per user.)

## Build order
1. Part B connect-portal (enabling primitive — also feeds Part C's LinkedIn/Naukri harvest).
2. Part C rich profile capture (the raw material for a great resume).
3. Part A resume (renders that material into "The Ledger").

## Develop & test on the fly
The plugin is ~all markdown skills + one HTML template + JSON config. The dev loop splits by
artifact: fast deterministic loops for the things with real logic, scenario runs for the prose
skills. Guardrail: never point dev/test runs at the user's real live profiles for write/apply
actions — use fixtures and throwaway accounts.

1. **Fixtures (build once):** `fixtures/profile.sample.json` + `fixtures/jd.sample.txt` so every
   skill runs deterministically without re-harvesting live sources. Seed `~/.career-copilot/`
   from fixtures for a test run.
2. **Resume template — tightest loop (no LLM, no plugin install):** the template is a standalone
   file. Edit `resume-template.html` → `chrome --headless --print-to-pdf=out.pdf resume-template.html`
   → `pdftotext out.pdf -` (ATS reading-order check) + open in browser (look). ~90% of Part A
   iteration lives here; wrap it in a one-line shell helper.
3. **Skills — local dev loop (confirmed):** start with `claude --plugin-dir ./career-copilot`
   (a local `--plugin-dir` overrides an installed same-name plugin — no uninstall needed). Invoke
   `/career-copilot:<skill>` / `/career-wizard` against fixture data. **SKILL.md text edits
   hot-reload live** in the session. Edits to `.mcp.json`, `agents/`, or `hooks/` do NOT — run
   `/reload-plugins`. Check loaded skills/agents via `/context`.
   Ref: code.claude.com/docs/en/plugins#test-your-plugins-locally
4. **Regression — `claude plugin eval` (early access, org-gated):** eval suites live in `evals/`,
   one dir per case: `prompt.md` (+ frontmatter) and `graders/*.md`. Assert skill behavior with a
   `tool_used` grader (`tool: Skill`, `input_match` on the skill name), plus `file_exists`
   (capture-profile wrote `profile.json`), `regex` (score-jd emits a per-dimension breakdown), and
   `llm` graders (tailor-resume added no skill absent from `profile.json`). Run
   `claude plugin eval . --json --threshold 1.0`; emits `results/<ts>/aggregate-result.json` +
   optional `report.html`. `/skill-doctor` = per-skill token/usage report. If the org isn't in
   early access these two are unavailable — fall back to fixture scenario runs (items 1–3).
5. **Portal auth (Part B) — manual loop:** headed login once → verify `portals.json`; kill the
   session, start fresh, re-run `connect-portal` → confirm still-authed from the persisted profile
   (cookie reuse). Use a throwaway/test account first given ToS/ban risk.

## Verification (end-to-end)
- **Resume:** open `resume-template.html` (sample content) in a browser → confirm Ledger look
  (single column, teal only on name/spine/ticks, mono dates aligned, mobile-responsive); Print→PDF
  → one clean page; **ATS proof:** `pdftotext out.pdf - | less` → all text extracts in correct
  reading order, headings intact, nothing scrambled.
- **Portal auth:** run `connect-portal linkedin` → browser opens LinkedIn login → log in →
  session verified → `portals.json` updated. Then start a *new* session and re-run → confirms
  still-logged-in from the persisted profile without re-login (cookie reuse proven).
