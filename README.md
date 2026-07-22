# NeoBank Support Chatbot

> AI-powered customer support chatbot for a fictional digital bank — portfolio project demonstrating generative AI, multi-agent architecture, RAG, and clean software engineering.

## Problem Statement

NeoBank needs an AI support chatbot that can handle 8 customer intents end-to-end: balance inquiries, PIX/transfer status, card management, credit limit increases, fraud disputes, FAQ, and human escalation. The system must be bilingual (PT/EN), cost zero to run, and demonstrate production-grade engineering practices.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Streamlit     │────▶│   agent_api      │────▶│   Ollama    │
│   Chat UI       │ SSE │   (FastAPI)      │     │   / Groq    │
└─────────────────┘     │                  │     └─────────────┘
                        │   LangGraph      │
                        │   Supervisor     │────▶ Postgres (domain)
                        │   + Specialists  │────▶ Chroma (RAG)
                        │                  │────▶ Redis (queue)
                        └──────────────────┘
                                │
                        ┌───────▼────────┐
                        │ ingestion_     │
                        │ worker         │
                        └────────────────┘
```

### Services

| Service | Role | Stack |
|---------|------|-------|
| `agent_api` | Online serving: chat, routing, tool calls | FastAPI + LangGraph + LiteLLM |
| `ingestion_worker` | Batch: KB ingestion, escalation processing | Python + Redis queue |

### Datastores

| Store | Purpose |
|-------|---------|
| Postgres | Domain data + LangGraph checkpointer |
| Redis | Job queue + pub/sub events |
| Chroma | Vector embeddings for RAG |

## Quickstart

### Prerequisites
- Python 3.12+
- Docker + Docker Compose (optional, for databases)
- NixOS users: see [NixOS Setup](#nixos-setup) below

### Option 1: One-click start (recommended)

```bash
# Linux/macOS
./start.sh

# Windows
start.bat

# Or with Python (cross-platform)
python start.py
```

This will:
1. Create a virtual environment if needed
2. Install dependencies
3. Start required services (PostgreSQL, Redis, ChromaDB)
4. Initialize the database with seed data
5. Start the Agent API on port 8000
6. Start the Streamlit frontend on port 8501
7. Open your browser automatically

### Option 2: Docker

```bash
# Clone and configure
cp .env.example .env

# Start core services
docker compose --profile core up -d

# Open Streamlit
streamlit run frontend/app.py
```

### Option 3: Manual setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Start databases (if not using Docker)
# PostgreSQL, Redis, ChromaDB must be running

# Run migrations
psql -h localhost -U neobank -d neobank -f ops/init.sql

# Start agent API
uvicorn services.agent_api.interface.app:create_app --factory --reload

# Start ingestion worker (in another terminal)
python -m services.ingestion_worker.interface.worker

# Start Streamlit (in another terminal)
streamlit run frontend/app.py
```

## NixOS Setup

For NixOS users, a development shell with all required services is provided:

### Quick setup (recommended)

```bash
# Run the automated setup script
./setup-nixos.sh

# This will:
# 1. Backup your current NixOS configuration
# 2. Add PostgreSQL, Redis, and Docker
# 3. Rebuild your system
# 4. Verify services are running
```

### Manual setup

```bash
# Enter development shell
nix-shell

# Start services manually
pg_ctl -D /tmp/neobank-pg start
redis-server --daemonize yes
```

### NixOS configuration

See `nixos-setup.nix` for the complete NixOS configuration snippet to add to your `/etc/nixos/configuration.nix`.

## LLM Provider Switch

Switch providers by changing one env var:

```bash
# Local Ollama
LLM_PROVIDER=ollama

# Groq (free tier, no GPU needed)
LLM_PROVIDER=groq
GROQ_API_KEY=your_key

# Gemini (free tier)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

## LLM Models Location

Models should be stored in `/mnt/Others/LLMs` to avoid filling the main disk:

```bash
# Pull model to custom location
OLLAMA_MODELS=/mnt/Others/LLMs ollama pull qwen3.5:9b

# Or set in .env
LLM_MODELS_PATH=/mnt/Others/LLMs
```

## Intent Catalog

| # | Intent | Reads | Escalates |
|---|--------|-------|-----------|
| 1 | Balance / statement | Account API | no |
| 2 | PIX / transfer status | Transactions API | no |
| 3 | Query card invoice | Card API | no |
| 4 | Pay card invoice | Card API (simulated) | no |
| 5 | Credit limit increase | Card API + risk rule | yes, above ceiling |
| 6 | Block card | Card API (simulated) | no |
| 7 | Fraud dispute | Transactions + risk | **yes, mandatory** |
| 8 | FAQ | RAG over KB | no |
| 9 | Talk to human | — | **yes** |

## Security

- **Per-customer authorization**: Every tool filters by session customer_id
- **Guardrail_in**: Detects prompt injection and PII leakage
- **Guardrail_out**: Blocks financial advice and secret patterns
- **Customer ID isolation**: ID flows only through session context, never through LLM extraction

## Observability

- **Langfuse**: LLM tracing (full profile)
- **Prometheus**: Ops metrics (throughput, latency, errors)
- **Grafana**: Dashboards (full profile)
- **FinOps**: Cost-per-session tracking

## Running the Demo

1. Start services: `docker compose --profile core up -d`
2. Open Streamlit: `streamlit run frontend/app.py`
3. Select a customer and start chatting
4. Try the fraud dispute flow: "Alguém usou meu cartão sem autorização!"

## Project Structure

```
neobank-support/
├── services/
│   ├── agent_api/         # FastAPI + LangGraph agent
│   └── ingestion_worker/  # KB ingestion + escalation processing
├── shared/                # Domain models, config, infrastructure
├── data/                  # Seeds + KB sources
├── eval/                  # Eval set + runner
├── ops/                   # Docker, Prometheus, Grafana
├── frontend/              # Streamlit chat
├── prompts/               # Versioned system prompts
├── docs/                  # Architecture, ADRs
└── tests/                 # Unit, integration, E2E
```

## Honest Coverage Notes

- **Real cloud deploy**: Not covered — consequence of zero-cost constraint
- **Kafka**: Deliberately excluded — Redis queue covers the requirement at this scale
- **CrewAI**: Not used — one framework (LangGraph) at depth beats three shallow ones
- **Kubernetes**: Optional flex, validated in `kind` with evidence in `docs/`
