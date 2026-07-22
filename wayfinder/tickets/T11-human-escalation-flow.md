<!-- label: wayfinder:grilling -->
<!-- blocks: T05 -->
<!-- assignee: (unclaimed) -->

# T11 — Human escalation flow

## Question

Decide what happens when the agent can't or shouldn't resolve — the human-in-the-loop handoff.

Decide: escalation triggers (low confidence, sensitive intent, explicit user request, repeated failure); what the handoff produces (a structured ticket summary with context + suggested resolution); where it goes (a mock "human queue" table / a logged ticket); and how the conversation state transfers so a human resumes with full context. Ties to memory (T07) for context carry-over.

Output: escalation design + handoff payload schema. Use `/grilling`.
