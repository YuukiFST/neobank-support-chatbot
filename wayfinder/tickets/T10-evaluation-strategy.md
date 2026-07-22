<!-- label: wayfinder:grilling -->
<!-- blocks: T05 -->
<!-- assignee: (unclaimed) -->

# T10 — Evaluation strategy

## Question

Decide how the agent's quality is tested — the "validation/homologation" the job mentions, and regression safety.

Decide: an **eval set** (labeled conversations per intent with expected outcomes); scoring method (exact-match on tool calls + **LLM-as-judge** for answer quality); regression harness that runs in CI; and homologation criteria (what "good enough to ship" means per intent). Decide which model judges (a free one) and how to keep judging cheap/deterministic.

Output: eval design + initial eval-set spec. Feeds CI (T04) and observability (T09). Use `/grilling`.
