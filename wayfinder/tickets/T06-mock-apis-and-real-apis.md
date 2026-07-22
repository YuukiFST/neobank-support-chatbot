<!-- label: wayfinder:research -->
<!-- blocks: T02 -->
<!-- assignee: (unclaimed) -->

# T06 — Mock API design + real free APIs

## Question

Design the API surface the agent integrates with — the job stresses "complex API integration."

Decide: which **mocked** endpoints to build (orders, stock, account, billing) with realistic schemas, auth, pagination, and *deliberate* failure modes (timeouts, 500s) so retry/backoff has something to handle. Then pick **1-2 real free APIs** to prove real integration (candidates: ViaCEP for address lookup, a free email/webhook service, GitHub API, a public shipping-tracking mock). Confirm each is truly free and keyless-or-free-key.

Output: API contract list (mock + real) with schemas and failure scenarios. Feeds capabilities (T05) build and evaluation (T10). Use `/research`.
