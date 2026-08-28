---
type: regex
pattern: '"verdict"\s*:\s*"(strong|worth-tailoring|stretch|skip)"'
match: "contains"
target: "files"
---

Plugin-discriminating: score-jd persists the scored job to ~/.career-copilot/jobs.json with the
verdict field set to exactly one of the four enum values. A no-plugin baseline run won't write this
file in this schema, so this grader isolates plugin-attributable behavior AND locks the verdict enum
in the persisted data (not just the chat message).
