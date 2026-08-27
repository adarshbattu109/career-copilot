---
name: connect-portal
description: Use to connect the applicant's accounts — log into cookie portals (LinkedIn, Naukri, Indeed, company sites) in a real browser so the session persists, and register API accounts (GitHub) by username. Saves both the cookie AND the account URLs into profile.json for extraction and later updation. Opt-in, ToS/ban-risk disclosed, cookies stored locally only.
---

# Connect accounts (Step 2)

One place to connect the accounts every later step uses. Two kinds:
- **Cookie portals** (LinkedIn, Naukri, Indeed, company sites) — need a real browser login; the
  session persists in `~/.career-copilot/browser-profile/` (local only).
- **API accounts** (GitHub) — no cookie/login; just capture + verify the username (public API).

Always write the resulting URL/handle into `profile.json` → `contact.links` (`linkedin`, `github`,
`naukri`, …) so both extraction (`capture-profile`) and future updation (`profile-grooming`) have
one source of truth.

Browser tools: `mcp__plugin_career-copilot_playwright__browser_*` (navigate, snapshot, wait_for).
**One shared browser — serial only.** Never drive it from parallel agents.

## Args
`linkedin | naukri | indeed | github | adzuna | jooble | serpapi | <company-url>`

## Cookie-portal flow (linkedin / naukri / indeed / company)
1. **Disclose + opt-in.** State the ToS/ban risk (LinkedIn especially bans automation) and that
   cookies are saved locally. Get an explicit yes before opening anything. Suggest a throwaway
   account for testing.
2. `browser_navigate` to the login URL (`linkedin.com/login`, `naukri.com`, `indeed.com`, or the
   company site). Tell the user: **log in yourself in the opened window** (handle OTP/SSO/captcha).
3. `browser_wait_for` a logged-in signal, or ask the user to confirm "done".
4. Verify with `browser_snapshot` — look for a profile/avatar/menu element. Don't assume success.
5. Record in `~/.career-copilot/portals.json`:
   `{ "portals": [ { "portal": "", "logged_in": true, "last_verified": "YYYY-MM-DD", "notes": "" } ] }`
   and write the profile URL into `profile.json` → `contact.links`.

## Job-source API keys (adzuna / jooble / serpapi) — onboard the user
`find-jobs` is API-first; these are the keys it needs. Don't assume they exist — walk the user
through getting one. **These are API keys, NOT a login password; never ask for or reuse a password.**
1. Explain the value + that **Adzuna is free** (the recommended default): structured job search, no
   browser, ToS-clean. (Jooble = free key; SerpApi = paid, only for Google Jobs.)
2. Open the signup page for them: `browser_navigate` to `https://developer.adzuna.com/signup`
   (Jooble: `https://jooble.org/api/about`; SerpApi: `https://serpapi.com/users/sign_up`). Tell them
   to register with a **fresh** password (not one reused elsewhere), verify the email, and copy the
   **App ID + App Key** from the dashboard. Email verification is theirs to complete — we don't
   automate account creation.
3. Ask them to paste the credentials. Write to `~/.career-copilot/config.json` (create if absent),
   under the provider (`adzuna: {app_id, app_key}` / `jooble: {key}` / `serpapi: {key}`), then
   `chmod 600` it.
4. **Verify** with one test call and report pass/fail, e.g.:
   `curl -s "https://api.adzuna.com/v1/api/jobs/in/search/1?app_id=$ID&app_key=$KEY&what=test&results_per_page=1"`
   (HTTP 200 + JSON `count` = working).
Keys stored locally only (config.json, 600); never transmitted or committed.

## GitHub flow (no cookie)
1. Ask for the username. Verify: `curl -s -o /dev/null -w "%{http_code}" https://api.github.com/users/USER`
   (200 = exists). No login needed.
2. Write `https://github.com/USER` into `profile.json` → `contact.links.github`. Record in
   `portals.json` as `{ "portal": "github", "logged_in": true, "notes": "public API" }`.
   (The connected GitHub MCP can be used for richer/authenticated reads during harvest.)

## Re-entry
Check `portals.json`, then a quick `browser_navigate` to confirm the session is still live.
Only re-prompt login if it lapsed — don't make the user re-auth needlessly (token-lean).

## Guardrails
- Opt-in per portal; risk disclosed before first open.
- Cookies local only, never transmitted/committed; `chmod 700` the profile dir.
- Human approves every outward action (apply/connect/message). Human-paced, no scrape-hammering.
- Own-profile reads only for harvest — don't scrape others' data.

This connection is also the data source for `capture-profile` (LinkedIn/Naukri own-profile harvest).
