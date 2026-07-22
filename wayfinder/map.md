<!-- label: wayfinder:map -->

# Map — NeoBank Support Chatbot (job-prep portfolio)

> **The decision phase is done.** All 12 decision tickets were resolved in one PRD grilling session.
> The build-ready spec is **[`../PRD.md`](../PRD.md)**; the glossary is **[`../CONTEXT.md`](../CONTEXT.md)**.
> What remains is *execution*, not decisions — follow the PRD's build phases (section 13).

## Destination

A complete, portfolio-grade **AI support chatbot for a fictional digital bank (NeoBank)**, engineered to cover four target AI-engineering roles at depth and at **zero monetary cost** (coverage is auditable bullet-by-bullet in the repo's `docs/jobs/`; known not-covered: real cloud deploy): generative AI + LLMs, multi-agent (LangGraph), RAG with an ETL ingestion pipeline, microservices + Docker, relational + NoSQL, observability + FinOps, security/compliance, Clean Architecture + DDD, CI/CD. Deliverable: a GitHub repo + recorded demo defended in interview.

## Notes

- **Scope locked at 4 job descriptions** (support agent + AI-engineer x2 + fintech chatbot). No more intake — converge, don't expand.
- Full spec in `../PRD.md`; ubiquitous language in `../CONTEXT.md`.
- **Zero cost is the mother-constraint.** Local/free only. No paid cloud, no billed API, no GPU host.
- **Anti-over-engineering held deliberately:** no Kafka (Redis queue/pub-sub covers the SQS/SNS-style requirement; rationale recorded in PRD §3), no K8s in the core (only a `kind`-validated flex), no service split beyond the 2 defined, no real cloud. Faking those would *lower* the project's value to a technical reviewer.
- Stack: Python 3.12 + uv, LangGraph, **LiteLLM** (Ollama Qwen3.5-9B / Groq / Gemini), Chroma + bge-m3, FastAPI + Streamlit, Postgres + Redis, Langfuse + Prometheus/Grafana, Docker Compose profiles.
- Agent bilingual PT+EN; repo docs/code/commits English.
- Built on a separate PC; this folder is the portable plan.

## Decisions so far

- **Destination & format** — flagship customer-support agent, then reshaped to a fintech chatbot covering 4 roles; deliverable = repo + recorded demo (option A), optional live via Groq (C).
- **Domain** — fictional digital bank "NeoBank"; 8-intent catalog; fraud dispute is the star case. See `CONTEXT.md`.
- **Providers** — LiteLLM gateway, swappable Ollama Qwen3.5-9B / Groq free / Gemini free.
- **Architecture** — 2 services (agent_api, ingestion_worker) + 3 datastores (Postgres, Redis queue/events — no Kafka, deliberate; Chroma), Docker Compose profiles, k8s optional flex validated once in `kind` with evidence.
- **Agent** — LangGraph supervisor multi-agent (router + account/card/risk/kb/escalation specialists), guardrail in/out.
- **Memory** — tri-tier: short (checkpointer), long (customer facts in Postgres), semantic (Chroma RAG).
- **RAG pipeline** — worker ETL extract→transform→chunk→embed(bge-m3)→load; idempotent, scheduled.
- **Ops** — Langfuse (LLM tracing) + Prometheus/Grafana (ops) + FinOps cost-per-session with equivalent-cost table.
- **Eval** — eval set + deterministic checks + LLM-as-judge + prompt versioning; subset in CI.
- **Security** — PII masking, prompt-injection guardrails, per-customer authz (customer id lives only in session context, never LLM-extracted; tools filter and re-validate ownership by it).
- **Delivery** — Clean Architecture + DDD layout, uv tooling, GitHub Actions CI, bilingual README, AI-as-ally doc.

## Not yet specified (fog → now the build)

The decision fog is cleared. What remains is implementation, sequenced in **PRD section 13 (build phases)**:
foundation → domain+data → RAG pipeline → agent core → ops → eval+security → interface+delivery → optional flexes.
Each phase is where an executing agent picks up next.

## Out of scope

- Desktop-native front (vercel-labs/native), paid LLM tiers, paid/real cloud deploy, self-hosted GPU.
- Real financial actions (payments/blocks are simulated).
- Kafka, K8s-at-scale, multi-cloud, service mesh, Azure AI Search, Databricks.
- Public live host of the local 9B model (Groq path covers live use).
- Study-curriculum companion + interview Q&A kit — optional side-efforts after the agent stands.
