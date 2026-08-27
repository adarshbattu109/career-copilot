---
name: ats-audit
description: Use to gauge/score a résumé (an existing file the user shares, or one crafted by tailor-resume) from an ATS perspective for a target role. Scores /100 across Competencies, Information, Presentation, and Personal Details, with per-parameter findings and concrete fixes. Also runs as the ATS gate inside tailor-resume.
---

# ATS audit (score a résumé)

Act as an expert ATS résumé reviewer who knows how parsers actually behave. Score a résumé **out of
100 for a specific target role** and return actionable fixes — not vague praise.

## Inputs
- The résumé: a file path (**Read** the PDF/DOCX/image — native PDF/image support, no external dep;
  see capture-profile "Reading documents") or pasted text, or a `~/.career-copilot/resumes/*.pdf`.
- **Target role** (ask if not given — scoring is role-relative).
- For file-level checks, use the actual file: filename, type, size. For page/word/table counts you
  may use the repo venv: `.venv/bin/python -c "import pypdf; ..."` (word count, page count) — else
  estimate from the text.
- Load `skills/tailor-resume/assets/skill-keywords.json` (keyword bank) and
  `skills/tailor-resume/assets/resume-guidelines.md` (rules).

## Scoring rubric (weights sum to 100) — show the breakdown, never a bare number

**1. Competencies — 40**
- **Bullets** — accomplishment bullets, not paragraphs/duties.
- **Dates** — every role has clear MMM YYYY ranges, reverse-chronological, no gaps unexplained.
- **Measurable impact** — bullets carry real numbers (%, $, time, scale). Count how many do.
- **Keywords** — required/preferred terms for the target role present (match JD + keyword bank).
- **Tables** — NONE for layout (tables break parsers). Flag any.
- **File details** — parseable file: real text (not scanned image), PDF, not password-locked.

**2. Information — 30**
- **All sections** — Contact, Summary, Experience, Education, Skills present.
- **Education / Skills** — present, correctly placed (skills grouped; education brief for seniors).
- **Not-required headings** — flag noise: "Objective", "References available on request", "Declaration".
- **Additional sections** — relevant extras (Projects, Certifications, Awards) add value, not filler.
- **Action words** — bullets start with strong verbs (Architected, Led, Reduced…).
- **Buzzwords (negative)** — penalize fluff ("passionate", "hard-working", "team player", "synergy").

**3. Presentation — 20**
- **Font style** — standard, ATS-safe (no exotic/icon fonts); consistent.
- **Font size** — body ~10–12pt, name larger; nothing unreadably small.
- **Filename** — `FirstName_LastName_Role.pdf` convention (professional, role-tagged).
- **Page count** — 1–2 pages (senior: 2 ok); flag 3+.
- **Word count** — ~400–800 typical; flag too sparse (<300) or bloated (>1000).

**4. Personal Details — 10**
- **Phone** — present, valid format.
- **Email** — present, professional address.
- **LinkedIn** — present (URL). Flag a dead/placeholder link.
- **Images** — NONE on ATS résumés (photo/logos/icons hurt parsing) unless the target locale
  expects a photo (see `locales.json`); flag otherwise.

## Output
1. **Score /100** + a per-category table (Competencies /40, Information /30, Presentation /20,
   Personal /10) with a one-line reason per parameter.
2. **Top fixes** — ranked, concrete, each with the before→after or exact change.
3. **Verdict** — ATS-ready / minor fixes / needs work — for the stated target role.
Truthful only: recommend adding a real keyword/metric the person has; never fabricate.

## As tailor-resume's gate
When called by `tailor-resume`, run on the rendered PDF and **block finalize if score < 85 or any
hard fail** (layout table, image-only text, missing contact, >2 pages) — report the fixes to apply.
