# Coverage matrix — bullet by bullet

Status legend: **demonstrated** (working code/evidence in the project) · **cited** (present but shallow; defensible with the noted framing) · **not covered** (gap, owned openly).
Soft skills and client-facing bullets are out of a portfolio's reach — marked *n/a (interview)*.

## Vaga 1 — Jr. AI Agent Developer

| Requirement | Status | Where / framing |
|---|---|---|
| Traduzir requisitos em funcionalidades | demonstrated | PRD → build: the repo itself is the evidence (wayfinder + PRD §13 phases) |
| Agentes de IA em Python, integrações complexas de APIs | demonstrated | LangGraph agents; mock banking APIs with fault injection + 2 real APIs (ViaCEP, currency) |
| Validação / homologação com clientes | cited | Eval set + LLM-as-judge = "homologação" story (PRD §9); no real client — say so |
| Monitorar métricas, ajustar comportamento, evolução contínua | demonstrated | Langfuse traces + Grafana + eval tagged by prompt version (PRD §8–9) |
| Troubleshooting / sustentação pós-implantação | demonstrated | Health checks, structured logs, retry/backoff, dead-letter, fault-rate testing (PRD §3, §15.2, §15.10) |
| IA como aliada (dev, testes, code review) | demonstrated | `docs/ai-assisted-development.md` + optional AI review step in CI (PRD §11) |
| Domínio forte de Python | demonstrated | Whole codebase; mypy/ruff/pytest gates |
| LLMs (GPT, Claude, Vertex, HF...) | demonstrated | LiteLLM multi-provider (Ollama/Groq/Gemini); swap = same interface as GPT/Claude |
| Prompt Engineering (técnicas, APIs, workflows) | demonstrated | Versioned prompts per node, eval-compared versions (PRD §9, §15.7) |
| Memórias de agentes + histórico conversacional | demonstrated | Tri-tier memory (PRD §6) — strongest match of this vaga |
| Desejável: LangChain, CrewAI, Agno | cited | LangGraph (LangChain family) at depth; CrewAI/Agno not used — one framework deep beats three shallow (PRD §3 note) |
| Soft skills | n/a (interview) | — |

## Vaga 2 — AI dev (texto perdido — auditado contra o resumo reconstruído)

| Requirement | Status | Where / framing |
|---|---|---|
| LangGraph / CrewAI | demonstrated | LangGraph supervisor multi-agent (PRD §6) |
| RAG | demonstrated | Chroma + bge-m3 + retrieval node (PRD §6) |
| ETL/ELT, data pipelines | demonstrated | Ingestion worker: extract→transform→chunk→embed→load, idempotent, scheduled (PRD §6) |
| Microsserviços + Docker | demonstrated | 2 services + 3 datastores, Compose profiles (PRD §5) — honest count |
| Cloud | **not covered** | Zero-cost constraint; Groq live run is the proxy (PRD §3 note) |
| Observabilidade | demonstrated | Langfuse + Prometheus/Grafana (PRD §8) |

> Re-audit when the real JD text is found.

## Vaga 3 — Sustentação de chatbot com IA

| Requirement | Status | Where / framing |
|---|---|---|
| AWS Lambda | not covered | Zero-cost; worker consuming a queue = same event-driven shape, different runtime — framing, not equivalence |
| SQS / SNS | cited | Redis queue (SQS-shape) + pub/sub (SNS-shape), retry + dead-letter (PRD §5, §15.10); concepts demonstrated, AWS services not |
| Docker / containers | demonstrated | Everything containerized, Compose profiles |
| Kubernetes / ECS | cited | `kind`-validated manifests with committed evidence (PRD §13.8) |
| n8n (orquestração de fluxos) | cited | Optional flex (PRD §13.8c) — **now justified by this vaga**; promote to "done" if time allows |
| AWS Bedrock | not covered | Paid; Gemini + LiteLLM show the same integration pattern — LiteLLM even has a Bedrock provider, say that |
| Google Gemini | demonstrated | LiteLLM Gemini free tier (PRD §7) |
| Ajuste de parâmetros de geração / evolução de system prompts / testes de comportamento | demonstrated | Versioned prompts + eval runs compared per version (PRD §9) |
| Métricas: latência, custo por sessão, consistência | demonstrated | FinOps cost-per-session + p50/p95 + Grafana — star metric of the project (PRD §8) |
| Go ou Python | demonstrated | Python |
| API/REST, CI/CD | demonstrated | FastAPI + GitHub Actions (PRD §11, §3) |
| Análise de dados / métricas operacionais | demonstrated | session_metrics table + Grafana dashboards |
| Desejável: RAG, embeddings, few-shot | demonstrated | RAG pipeline; few-shot in specialist prompts (note it explicitly in prompt specs) |
| Desejável: FinOps de IA generativa | demonstrated | Equivalent-cost table + per-session persistence — direct hit |
| Desejável: CloudWatch / OpenSearch / Datadog | cited | Prometheus/Grafana são o equivalente OSS; conceito idêntico (dashboards, alertas, logs estruturados) |
| Segurança, performance, compliance | demonstrated | Authz invariant, PII masking, guardrails, injection test (PRD §10, §14) |

## Vaga 4 — AI Engineer Specialist

| Requirement | Status | Where / framing |
|---|---|---|
| IA Generativa + LLMs | demonstrated | Core of the project |
| Agentes / fluxos multiagentes | demonstrated | LangGraph supervisor + 5 specialists (PRD §6) |
| APIs backend p/ integração de IA | demonstrated | agent_api FastAPI + SSE streaming contract (PRD §15.3) |
| Definições arquiteturais / boas práticas | demonstrated | ADRs, wayfinder decision record, PRD itself |
| RAG + Prompt Engineering + avaliação de modelos | demonstrated | PRD §6, §9 — eval com deterministic + judge é o diferencial |
| Qualidade, observabilidade, segurança, escalabilidade | demonstrated | §8, §10; "escalabilidade" = stateless agent_api + queue — say it, don't overclaim |
| Python backend | demonstrated | — |
| LangChain / LangGraph ou similares | demonstrated | LangGraph |
| FastAPI | demonstrated | agent_api |
| Microsserviços, REST, integração | demonstrated | PRD §5 |
| Relacionais + NoSQL | demonstrated | Postgres + Redis + Chroma (vector DB) — frame Redis+Chroma as the NoSQL answer (PRD §3) |
| Docker, Kubernetes, Cloud (pref. Azure) | cited / not covered | Docker demonstrated; K8s = kind-validated flex; Azure/cloud real not covered (zero-cost) |
| Git + CI/CD | demonstrated | GitHub Actions full gates |
| Diferencial: Multi-Agent Systems / Agentic AI | demonstrated | — |
| Diferencial: LiteLLM / Azure AI Search / MLflow | demonstrated (partial) | LiteLLM nominal e central; AI Search/MLflow fora (Langfuse = "plataforma similar") |
| Diferencial: Databricks | not covered | Out of scope, assumed |
| Diferencial: Kafka, Redis, event-driven | cited | Redis + queue + pub/sub = event-driven demonstrated; Kafka excluded with recorded rationale (PRD §3) — the "why no Kafka" answer is itself senior signal |
| Diferencial: Grafana / Prometheus | demonstrated | Nominal hit (PRD §8) |
| Diferencial: Clean Architecture, DDD, Design Patterns | demonstrated | Layered services + DDD model + LangGraph placement rule (PRD §12) |
| Diferencial: POCs / avaliação de tecnologias | demonstrated | The project is a POC with recorded decision process (wayfinder) |

## Summary

- **Not covered anywhere (owned openly):** real cloud (Azure/AWS/Bedrock/Lambda), Databricks. All consequences of the zero-cost mother-constraint; each has a documented proxy/framing.
- **Weakest vaga:** 3 (sustainment) — most AWS-specific. Mitigations in place: queue/eventos shape, Gemini, FinOps direct hit, n8n flex now prioritized.
- **Strongest vagas:** 1 and 4 — near-total coverage.
