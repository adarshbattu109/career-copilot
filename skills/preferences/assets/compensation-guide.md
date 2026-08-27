# Compensation capture guide (reference for the `preferences` skill)

Sensitive — store locally only in `preferences.json`. Capture *structure*, not just a number, so
jobs/offers compare like-for-like. Used to filter jobs below current and to compare offers (Step 7).

## What to capture
- **current / last CTC:** base (fixed), variable/bonus, ESOP/RSU (annualized) → `total_fixed` + `total_ctc`.
- **benefits / perks — itemized, each with annual value + a category:**
  - *statutory / retirement* — EPF, NPS, gratuity (deferred, employer contribution)
  - *allowances* — conveyance, equipment/setup, LTA
  - *reimbursements* — telephone, internet, fuel
  - *benefit-in-kind* — Pluxee/Sodexo meal card, insurance, wellness
  Tag each `taxable`. **Tax-exempt perks (meal card, reimbursements) are worth more than face value** —
  note an `effective` uplift; don't just sum face amounts. Postings rarely list perks → full benefits
  comparison lands at the offer stage; capture the *current* set now as the baseline.
- **expected:** `min` (walk-away) + `target`; any non-negotiables / must-have benefits.

## Currency
Each bucket carries its own currency; set a **`base_currency`** to normalize comparisons to (home
currency; switch if relocating). Keep an **`fx`** table (rate-to-base per foreign unit) with an
**`as_of` date** — rates drift, so refresh when stale and always show native + normalized amounts.
For cross-country moves, flag **cost-of-living / PPP** separately — raw FX ≠ real purchasing power.

## Ingest from a document (fastest)
User shares a salary-structure / payslip / CTC-breakup / offer-letter PDF → parse with the **Read
tool** (native PDF/image, no dep; see capture-profile "Reading documents") and auto-fill
base/variable/ESOP/benefits/total. **Extract ONLY comp figures; never store PII** (PAN, bank/account,
UAN, address); don't copy the raw file into the store. Read the extracted structure back to confirm
before saving. (Same parser serves offer letters in Step 7.)
