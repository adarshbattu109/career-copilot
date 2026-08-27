---
description: Discover and score relevant jobs across sources (or paste one JD for the quick path).
argument-hint: "[optional: paste/link a single JD for quick scoring]"
---

# Find jobs

- If `$ARGUMENTS` contains a single JD or link → run the **score-jd** skill (quick path).
- Otherwise → run the **find-jobs** skill (multi-source discovery → dedup → score → ranked list).

Needs `~/.career-copilot/profile.json` (run `capture-profile` first if missing). Portal sources
require `connect-portal`. Results land in `~/.career-copilot/jobs.json`.
