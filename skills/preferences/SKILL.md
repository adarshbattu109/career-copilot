---
name: preferences
description: Use to curate the applicant's job-search preferences with them — roles, seniority, location/remote, comp, company stage, must-haves vs nice-to-haves, deal-breakers, and target countries. Writes ~/.career-copilot/preferences.json, which drives find-jobs filtering and tailor-resume locale.
---

# Preferences (Step 3)

Curate search preferences with the user; confirm before they drive discovery. `mkdir -p ~/.career-copilot`.

## Flow
Ask in a short pass (one topic at a time; pre-fill guesses from `profile.json` and confirm — don't
ask what you can infer):
- **Roles / titles** targeted; **seniority**.
- **Location / remote** (onsite / hybrid / remote; cities); **target countries** (drives resume locale).
- **Compensation** (sensitive — optional, local only). Capture the *structure* (not just a number):
  current/last CTC (base + variable + ESOP), itemized benefits by category with a taxable flag,
  expected min/target, and multi-currency (`base_currency` + `fx`). **Fastest: ingest a
  salary-structure/payslip PDF** with the Read tool — **extract only comp figures, never PII**.
  Full rules + the tax-uplift/FX/PPP detail are in **`assets/compensation-guide.md`** — follow it.
  Used to filter jobs below current and compare offers (Step 7).
- **Company stage / type** (startup / growth / enterprise / specific industries).
- **Must-haves** vs **nice-to-haves**.
- **Deal-breakers** — HARD filters (e.g. no relocation, no on-call, min base). These drop a job in
  find-jobs; they are not soft weights.

Read them back for confirmation before saving.

## Re-entry (token-lean)
Summarize current prefs in one line; ask "anything changed?" Patch only that.

## Schema (`~/.career-copilot/preferences.json`)
```json
{
  "roles": [], "seniority": "",
  "locations": [], "remote": "onsite|hybrid|remote|any", "target_countries": [],
  "compensation": {
    "base_currency": "INR",
    "current": {
      "currency": "INR", "base": 0, "variable": 0, "esop_annual": 0,
      "benefits": [ { "name": "", "category": "statutory|allowance|reimbursement|benefit_in_kind", "value_annual": 0, "taxable": true } ],
      "total_fixed": 0, "total_ctc": 0, "total_effective_note": "", "as_of": "YYYY-MM"
    },
    "last": null,
    "expected": { "currency": "INR", "min": 0, "target": 0, "must_have_benefits": [], "non_negotiables": [] },
    "fx": { "as_of": "YYYY-MM-DD", "rates_to_base": { "USD": 0, "EUR": 0, "GBP": 0, "AED": 0 } }
  },
  "company_stage": [], "industries": [],
  "must_haves": [], "nice_to_haves": [], "deal_breakers": [],
  "updated": "YYYY-MM-DD"
}
```
After saving, offer `find-jobs` (these now filter + rank discovery).
