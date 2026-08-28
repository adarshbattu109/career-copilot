---
name: apply
description: Use to apply to a pursued job — assemble the tailored resume + answers, then fill the application form and upload attachments on ATS platforms (Workday, Greenhouse, Lever, iCIMS, Taleo) via the connected browser, pausing for per-application human confirmation before submit; hand off where automation can't proceed. Logs every application to ~/.career-copilot/applications.json. Never auto-submits.
---

# Apply (Step 6)

Submit an application for a "pursue" job. **Never auto-submit** — the user confirms every send.

Precondition: a tailored resume exists (`tailor-resume`) and, for portal submits, the portal is
connected (`connect-portal`). Browser tools are `mcp__plugin_career-copilot_playwright__browser_*` —
**one shared browser, serial only**.

## Flow
1. Load the job from `jobs.json` (status `pursue`) + `profile.json` + the resume at the job's
   recorded `resume_file` path (set by `tailor-resume`). If that field is absent, ask or pick the
   newest matching file in `~/.career-copilot/resumes/` — never guess a `{job_id}.pdf` name.
2. **Prep (parallelizable across queued apps, token-lean):** open the application page, map its
   form fields, and draft answers to screening questions from `profile.json` (truthful only —
   never fabricate). Prep may fan out across multiple queued jobs; **submitting does not.**
3. **Review with the user:** show the filled fields + drafted answers + which resume file. Get an
   explicit yes.
4. **Submit — serial, human-confirmed:**
   - **Connector path:** where the portal allows, fill the form via the browser (see ATS section)
     and **pause at the final submit** for the user's explicit confirmation.
   - **Hand-off path:** where automation can't proceed (hard captcha, anti-bot wall, unknown/opaque
     form), assemble everything and hand off for the user to submit manually.

## ATS form-filling (Workday, Greenhouse, Lever, iCIMS, Taleo, SmartRecruiters)
1. **Detect the platform** from the URL/DOM (`myworkdayjobs.com` → Workday; `greenhouse.io`,
   `lever.co`, `icims.com`, `taleo.net`, …) — each has known field patterns.
2. **Read the form first** with `browser_snapshot` to get field refs; never fill blind.
3. **Fill** with `browser_fill_form` (text/checkbox/combobox/radio) — name, email, phone, location,
   work authorization, experience, screening questions (answers drafted from `profile.json`, truthful).
4. **Attachments** — upload résumé + cover letter with `browser_file_upload` from the job's
   `resume_file` and `cover_file` paths (both recorded by `tailor-resume`).
5. **Multi-step wizards (esp. Workday):** proceed page-by-page — Workday often (a) requires an
   **account** (email+password; the user creates/enters it — we don't store site passwords), then
   (b) **auto-parses the résumé and pre-fills** fields, which you must **review and correct** (parse
   errors are common), across several steps (My Info → Experience → Questions → Review). Snapshot +
   verify each step; don't assume a step succeeded.
6. **Stop at Review/Submit** and show the user the full filled application; submit only on their yes.
Fall back to hand-off if a step blocks (captcha, SSO, unexpected required field you can't answer truthfully).
7. **Log immediately** (either path) to `~/.career-copilot/applications.json`:
```json
{ "applications": [
  { "job_id": "", "company": "", "title": "", "status": "applied",
    "applied_at": "YYYY-MM-DD", "method": "connector|manual", "resume": "", "notes": "" }
] }
```
Write `status: "applied"` only — leave pipeline/`reason_code` fields out here; **Step 7 `track`**
adds them on later status changes (don't write a field this step can't populate).

## Guardrails
- No auto-apply/auto-send — per-application confirmation, always.
- Human-paced; respect per-portal rate/ToS; disclosed. Multi-agent prep must never multiply submits.
- Truthful answers only — a screening answer the profile can't support gets flagged, not invented.
