---
name: tailor-resume
description: Use to craft a job-specific resume from profile.json + a scored job — one balanced artifact that is visually clean AND ATS-parseable, from a chosen template (registry in assets/templates.json, default Classic), locale-aware, truthful only. Optional multi-agent variant+critic panel for high-stakes roles. Renders HTML→PDF into ~/.career-copilot/resumes/.
---

# Tailor resume (Step 5)

Produce a job-specific resume from `profile.json` (its reconciled `timeline[]`) and a scored job.
**Truthful tailoring only — reorder, reweight, rephrase real experience. Never invent skills,
titles, dates, or achievements.**

Templates — **registry at `assets/templates.json`** (`id → file + style`, plus `default`). Read it,
show the user the options (name + style), and render their pick; default to `classic` if unsure.
Add a template later by dropping an HTML file in `assets/` + one registry entry — no other change.
All templates are single-column, real-text, ATS-safe clean-room designs.
Other assets: `assets/locales.json`, `assets/skill-keywords.json` (ATS keyword bank),
`assets/resume-guidelines.md` (best-practice rules — read it first and follow it).

## Flow
1. Load the job from `~/.career-copilot/jobs.json` (by `id`) + `profile.json`. Ask for any existing
   base resume.
2. **Evaluate base first** — score it vs the JD: what lands, what's buried, what's missing. Show
   this so the changes are justified.
3. **Locale** — determine target country (JD / `preferences.json`); read `assets/locales.json`.
   Set the heading term (Resume/CV/Lebenslauf), page target, date format, and whether the photo /
   personal-details slots show. Warn if the locale expects a field the profile lacks. Never render
   photo/DOB for US/UK/CA/AU.
4. **Compose (apply the parsed patterns):**
   - **Summary formula:** `[Role] with [N yrs] of [top 2-3 skills]. Achieved [top metric]. Expert
     at [X], [Y], [Z].`
   - **Experience:** reverse-chron; action-verb bullets; quantified impact; `role-left / company /
     dates-right`. Lead with what matches the JD's required skills — real evidence only.
   - **Skills:** grouped text (Soft / Hard / Languages), keyword-matched to the JD for ATS using
     `assets/skill-keywords.json` **plus semantic synonyms** (the bank is a seed, not a whitelist —
     don't limit matching to listed terms); surface gaps.
   - **Projects:** include a Personal Projects section (differentiator).
5. **Render** — fill the template `file` chosen from `assets/templates.json` (default `classic`);
   keep it a single true column (any spine/accent is decoration, never a text-shifting gutter).
   Use the ATS filename convention `{FirstName}_{LastName}_{Role}.pdf` (what `ats-audit` rewards).
   Write the `.html`, then PDF with no new
   dep: `chrome --headless --print-to-pdf=<name>.pdf <name>.html` (or Google Chrome path); if
   no Chrome, tell the user to open + Print→PDF. Don't ship a broken file. **Record the exact path
   back into the job's entry in `jobs.json` as `resume_file`** so `apply` loads it directly — no
   filename guessing.
6. **ATS gate:** run the **`ats-audit`** skill on the rendered PDF for the target role. Confirm text
   extracts in correct reading order and score ≥ 85 with no hard fail (layout table, image-only
   text, missing contact, >2 pages). Apply its fixes and re-render if it falls short.
7. **Cover letter** — short, company/role-specific, grounded in real achievements. Render it as the
   `resume_file` sibling `{FirstName}_{LastName}_{Role}.cover.pdf` and record that path in the job's
   entry as `cover_file` (mirror the `resume_file` contract) so `apply` uploads it directly.
8. Show a diff-style summary of what changed vs the base and why.

## Multi-agent (scale to need — token-lean)
- **Quick (default):** one draft → the two checks below.
- **Thorough (high-stakes role):** generate 3 variants in parallel (impact-first / keyword-first /
  leadership-first) → parallel critics, then synthesize the winner grafting the best *real* bullets:
  - **ATS-parse critic** — reading-order via the Read tool / pypdf (no pdftotext dep) + JD keyword hit-rate.
  - **Recruiter-persona critic** — 6-second skim: is the fit obvious?
  - **Truthfulness auditor** — flags any claim not grounded in `profile.json`. **Veto is absolute:**
    a variant that wins on ATS but fabricates is killed.

## Guardrail
If tailoring would need a claim the profile doesn't support, say so and suggest closing the gap for
real (a project, a cert) — never write it in. `--accent` in the template is the one color knob.
