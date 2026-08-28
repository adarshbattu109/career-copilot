---
type: llm
criteria: "The response's final verdict/recommendation is EXACTLY one of these four labels: strong, worth-tailoring, stretch, or skip — never 'pass', 'maybe', or any other label. This JD is a STRONG match for the profile (senior Go/Kubernetes/Kafka payments backend, 8 yrs), so the verdict MUST be 'strong' or 'worth-tailoring'. Any of 'stretch', 'skip', 'pass', or 'maybe' fails — the verdict must track the high score, not just be a legal label."
focus: "verdict vocabulary and score-consistency"
target: "last_message"
---

Enforces the pinned verdict vocabulary (F3 fix): strong / worth-tailoring / stretch / skip only,
and the verdict must track the score. A verdict of "pass" or "maybe", or a skip on a high score,
fails this grader.
