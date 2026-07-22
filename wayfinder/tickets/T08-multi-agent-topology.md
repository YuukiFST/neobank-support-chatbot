<!-- label: wayfinder:grilling -->
<!-- blocks: T05 -->
<!-- assignee: (unclaimed) -->

# T08 — Multi-agent topology

## Question

Decide whether the agent is a single LangGraph agent or a multi-node/multi-agent graph, and the exact shape.

Weigh: single ReAct-style agent with tools vs a **triage → resolve → escalate** multi-agent graph (a router that classifies intent, specialist nodes per domain, an escalation node). The job desires multi-agent frameworks; a graph tells a stronger story but costs complexity. Decide node/edge topology, state shape, and where each intent (T05) routes.

Output: graph diagram + node responsibilities. Feeds the build and evaluation (T10). Use `/grilling`.
