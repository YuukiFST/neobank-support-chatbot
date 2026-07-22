# CONTEXT — NeoBank Support Chatbot (glossary)

Ubiquitous language for the project. Glossary only — no implementation details.

## Domain

Fictional digital bank ("NeoBank"). An AI support **chatbot** answers customer questions and resolves support intents against simulated banking data. All financial actions are **simulated** against mocks — no real money movement, ever.

## Terms

- **Customer** — the bank's end user talking to the chatbot. Identified by a customer id. Has PII (name, document) shown unmasked only where the operator needs it; masked in logs.
- **Account** — a customer's digital checking account. Holds balance and a statement (list of Transactions).
- **Transaction** — a movement on an Account: PIX, transfer, card charge, fee. Has status (pending/settled/failed) and a risk flag.
- **Card** — a credit or debit card tied to an Account. Has a limit, an invoice (fatura), and a state (active/blocked).
- **Invoice (fatura)** — the monthly bill for a credit Card. Can be queried and "paid" (simulated).
- **Limit** — the credit ceiling on a Card. A limit-increase request is subject to a **risk rule**.
- **Investment** — a simple product (CDB/savings) the customer holds. Read-only; no buy/sell.
- **Intent** — a support goal the chatbot handles end-to-end (see the 8-intent catalog). Distinct from a free-form question.
- **Risk rule** — a deterministic business rule gating sensitive intents (limit increase above a ceiling, fraud/dispute). Its outcome may force escalation.
- **Escalation** — handing a conversation to a human when the agent can't or shouldn't resolve (fraud, above-ceiling limit, explicit request, repeated failure). Produces a structured handoff with full context.
- **Knowledge base (KB)** — FAQ, fees/tariffs, product docs. Answered via RAG, never via API.
- **Session** — one continuous conversation with a Customer. The unit for cost/latency metrics (FinOps).
- **Handoff** — the structured payload transferred to the human queue on Escalation: conversation summary, customer context, suggested resolution.
- **Session binding** — the invariant that a Session is bound to exactly one Customer id, carried only in session context (never extracted by the LLM); every tool filters and re-validates ownership by it. The core authz control.

## Language boundaries

- "Account" = the bank Account (money), NOT a login/User. Auth identity is out of scope (fictional customer id passed in).
- "Pay invoice" / "block card" = **simulated** state changes on mocks, never real actions.
- "Chatbot" = the whole product; "agent" = the LangGraph orchestration inside it.

## Fixed rules (from grilling)

- Zero monetary cost. Local/free tiers only.
- LLM provider-swappable via **LiteLLM**: local Ollama (Qwen3.5-9B) / Groq free / Gemini free.
- Agent bilingual PT+EN; repo docs/code/commits in English.
- No real financial actions. No paid cloud. No K8s in the core.
