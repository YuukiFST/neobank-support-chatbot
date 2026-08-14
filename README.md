# NeoBank Support Chatbot

A support agent for a fictional digital bank: it answers customer questions about balances, PIX transfers, cards and fraud, and escalates to a human when the request is beyond it.

Built as a portfolio project. It is a **prototype under active rework** — the section below states exactly what runs today and what does not.

## Stack

FastAPI + LangGraph for the agent, LiteLLM for provider switching (Ollama, Groq, Gemini), Postgres for domain data, Chroma for embeddings, Redis for the worker queue, Streamlit for the chat UI.

## Run it

```bash
docker compose --profile core up -d    # Postgres, Redis, Chroma
./start.sh                             # start.bat on Windows, start.py anywhere
```

`start.sh` creates the venv, installs dependencies, seeds the database, and opens the UI on `:8501` against the API on `:8000`.
It checks the datastores rather than starting them: without Postgres it falls back to mock data, without Chroma the FAQ path is dead.

NixOS users: `./setup-nixos.sh`.

Pick the model provider with one env var:

```bash
LLM_PROVIDER=ollama     # local
LLM_PROVIDER=groq       # free tier, needs GROQ_API_KEY
LLM_PROVIDER=gemini     # free tier, needs GEMINI_API_KEY
```

## What works today

- A 9-node LangGraph flow: input guardrail, intent classification, four specialist branches, escalation, output guardrail.
- Read operations against the domain database: balance, transfer status, card list, invoice.
- Prompt-injection and PII guardrails on the way in, financial-advice and secret-leak guardrails on the way out (regex, English patterns only).
- Per-customer authorization: the customer id travels in session context and is never extracted by the model.
- Human escalation, mandatory on fraud disputes, persisted to Postgres.
- 62 tests running headless against named fakes, with `ruff` and `mypy --strict` enforced in CI.

## What does not work yet

Honest list, each one an open issue:

- **The model does not call tools.** Dispatch is a fixed intent-to-tool dictionary; the LLM only classifies. Consequence: `pay_invoice`, `block_card` and `request_limit_increase` are never executed in production.
- **RAG is broken.** Ingestion embeds with `bge-m3` while queries use Chroma's default embedding function, and nothing ever enqueues the ingestion job. FAQ answers come back ungrounded.
- **No conversation memory.** The graph compiles without a checkpointer, so every request is a fresh turn.
- **No cost or token tracking**, and no LLM tracing.
- **CI runs unit tests only.** Integration, e2e and the 15-case eval set are not gated.
- **No cloud deployment.**

## Where it is going

The rework is planned in the open, as a [wayfinder map](https://github.com/YuukiFST/neobank-support-chatbot/issues/16): repositioning this from a chatbot that answers into an agent that executes actions under an explicit autonomy boundary, measured per decision on accuracy, latency and cost.
