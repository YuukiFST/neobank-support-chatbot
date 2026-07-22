<!-- label: wayfinder:grilling -->
<!-- blocks: T02 -->
<!-- assignee: (unclaimed) -->

# T05 — Agent capabilities / intents catalog

## Question

Given the domain (T02), decide exactly which support intents the agent handles end-to-end, and which it escalates.

Decide the intent list (e.g. order status, track shipment, return/refund request, stock/availability, account changes, billing question, product recommendation, complaint → human). For each: what tools/APIs it calls, what data it reads, success criteria, and the escalation trigger. This is the functional spec the whole agent is measured against.

Output: intent catalog table. Blocks memory (T07), multi-agent (T08), evaluation (T10), escalation (T11). Use `/grilling` + `/domain-modeling`.
