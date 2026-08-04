"""FastAPI application — agent_api service.

Endpoints:
- POST /sessions — create a session (customer_id, language)
- POST /chat — SSE streaming chat
- GET /health — health check
- GET /metrics — Prometheus metrics
- Mock banking APIs mounted at /mock
"""

from __future__ import annotations

import json
import time
import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field
from sqlalchemy import text

from services.agent_api.application.agent import create_agent_graph, merge_graph_state
from services.agent_api.infrastructure.mock_banking_api import load_seed_data
from services.agent_api.infrastructure.mock_banking_api import router as mock_router
from shared.infrastructure.auth import verify_api_key
from shared.infrastructure.config import settings
from shared.infrastructure.database import Base, async_session, engine
from shared.infrastructure.observability import (
    ACTIVE_SESSIONS,
    CHAT_LATENCY,
    CHAT_REQUESTS,
    ESCALATIONS,
    log,
)
from shared.infrastructure.rate_limit import check_rate_limit

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

MAX_MESSAGE_LENGTH = 4000


# --- Lifespan ---


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown lifecycle."""
    log.info("starting_agent_api", provider=settings.llm_provider)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _load_seeds()

    app.state.agent_graph = create_agent_graph()
    log.info("agent_graph_compiled")

    yield

    log.info("shutting_down_agent_api")
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory for uvicorn --factory."""
    application = FastAPI(
        title="NeoBank Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(mock_router)
    _register_routes(application)
    return application


# --- Seed data loader ---


async def _load_seeds() -> None:
    """Load seed data from SQL seeds into the mock API."""
    async with async_session() as session:
        result = await session.execute(
            text("SELECT id, name, document, address_cep, language FROM customers")
        )
        customers = [
            {"id": str(r[0]), "name": r[1], "document": r[2], "address_cep": r[3], "language": r[4]}
            for r in result.fetchall()
        ]

        result = await session.execute(text("SELECT id, customer_id, balance FROM accounts"))
        accounts_list = [
            {"id": str(r[0]), "customer_id": str(r[1]), "balance": float(r[2])}
            for r in result.fetchall()
        ]

        result = await session.execute(
            text(
                "SELECT id, account_id, type, amount, status, risk_flag, description, "
                "reference, created_at FROM transactions ORDER BY created_at DESC LIMIT 50"
            )
        )
        transactions = [
            {
                "id": str(r[0]),
                "account_id": str(r[1]),
                "type": r[2],
                "amount": float(r[3]),
                "status": r[4],
                "risk_flag": r[5],
                "description": r[6],
                "reference": r[7],
                "created_at": str(r[8]),
            }
            for r in result.fetchall()
        ]

        result = await session.execute(
            text("SELECT id, account_id, kind, state, limit_amount, last_four FROM cards")
        )
        cards = [
            {
                "id": str(r[0]),
                "account_id": str(r[1]),
                "kind": r[2],
                "state": r[3],
                "limit_amount": float(r[4]),
                "last_four": r[5],
            }
            for r in result.fetchall()
        ]

        result = await session.execute(
            text("SELECT id, card_id, month, total, status, due_date FROM invoices")
        )
        invoices = [
            {
                "id": str(r[0]),
                "card_id": str(r[1]),
                "month": r[2],
                "total": float(r[3]),
                "status": r[4],
                "due_date": str(r[5]) if r[5] else None,
            }
            for r in result.fetchall()
        ]

        result = await session.execute(
            text("SELECT id, customer_id, product, principal FROM investments")
        )
        investments = [
            {"id": str(r[0]), "customer_id": str(r[1]), "product": r[2], "principal": float(r[3])}
            for r in result.fetchall()
        ]

    load_seed_data(
        {
            "customers": {c["id"]: c for c in customers},
            "accounts": {a["id"]: a for a in accounts_list},
            "transactions": transactions,
            "cards": cards,
            "invoices": invoices,
            "investments": investments,
        }
    )
    log.info(
        "seeds_loaded", customers=len(customers), accounts=len(accounts_list), cards=len(cards)
    )


# --- Request/Response models ---


class SessionRequest(BaseModel):
    customer_id: str
    language: str = "pt"


class SessionResponse(BaseModel):
    session_id: str
    customer_id: str
    language: str


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., max_length=MAX_MESSAGE_LENGTH)


def _register_routes(application: FastAPI) -> None:
    """Register API routes on the application."""

    @application.get("/health")
    async def health() -> dict[str, str]:
        """Health check — verifies database connectivity."""
        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "healthy"}
        except Exception as e:
            log.error("health_check_failed", error=str(e))
            raise HTTPException(status_code=503, detail="Service unhealthy") from e

    @application.post(
        "/sessions", response_model=SessionResponse, dependencies=[Depends(verify_api_key)]
    )
    async def create_session(req: SessionRequest) -> SessionResponse:
        """Create a new chat session."""
        try:
            customer_uuid = uuid.UUID(req.customer_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid customer_id format") from exc

        async with async_session() as session:
            result = await session.execute(
                text("SELECT id FROM customers WHERE id = :id"),
                {"id": customer_uuid},
            )
            if not result.fetchone():
                raise HTTPException(status_code=404, detail="Customer not found")

            session_id = str(uuid.uuid4())
            await session.execute(
                text(
                    "INSERT INTO sessions (id, customer_id, language) "
                    "VALUES (:id, :customer_id, :language)"
                ),
                {
                    "id": uuid.UUID(session_id),
                    "customer_id": customer_uuid,
                    "language": req.language,
                },
            )
            await session.commit()

        ACTIVE_SESSIONS.inc()
        log.info("session_created", session_id=session_id, customer_id=req.customer_id)
        return SessionResponse(
            session_id=session_id, customer_id=req.customer_id, language=req.language
        )

    @application.post("/chat", dependencies=[Depends(verify_api_key)])
    async def chat(req: ChatRequest, request: Request) -> StreamingResponse:
        """SSE streaming chat endpoint."""
        start_time = time.time()
        graph = request.app.state.agent_graph

        if not check_rate_limit(req.session_id, settings.rate_limit_per_minute):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")

        try:
            session_uuid = uuid.UUID(req.session_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid session_id format") from exc

        async with async_session() as session:
            result = await session.execute(
                text("SELECT customer_id, language FROM sessions WHERE id = :id"),
                {"id": session_uuid},
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Session not found")
            customer_id = str(row[0])
            language = row[1]

            result = await session.execute(
                text("SELECT document FROM customers WHERE id = :id"),
                {"id": uuid.UUID(customer_id)},
            )
            cust_row = result.fetchone()
            customer_document = cust_row[0] if cust_row else ""

        async def event_stream() -> AsyncIterator[str]:
            try:
                state: dict[str, Any] = {
                    "messages": [HumanMessage(content=req.message)],
                    "customer_id": customer_id,
                    "customer_document": customer_document,
                    "session_id": req.session_id,
                    "language": language,
                    "intent": "",
                    "tool_calls": [],
                    "tool_results": [],
                    "response": "",
                    "handoff": None,
                    "guardrail_in_result": None,
                    "guardrail_out_result": None,
                    "error": None,
                }

                accumulated: dict[str, Any] = dict(state)
                response_streamed = False

                async for event in graph.astream(state):
                    for node_name, node_output in event.items():
                        accumulated = merge_graph_state(accumulated, node_output)

                        if node_name == "router" and node_output.get("intent"):
                            intent = node_output["intent"]
                            CHAT_REQUESTS.labels(intent=intent, language=language).inc()
                            routed = json.dumps({"type": "tool", "data": f"Routed to: {intent}"})
                            yield f"data: {routed}\n\n"

                        if node_output.get("response"):
                            response_text = node_output["response"]
                            for i in range(0, len(response_text), 10):
                                chunk = response_text[i : i + 10]
                                yield f"data: {json.dumps({'type': 'token', 'data': chunk})}\n\n"
                            response_streamed = True

                        if node_output.get("handoff"):
                            handoff = node_output["handoff"]
                            intent_label = accumulated.get("intent", "unknown")
                            ESCALATIONS.labels(intent=intent_label).inc()

                            async with async_session() as db:
                                await db.execute(
                                    text(
                                        "INSERT INTO handoffs "
                                        "(id, session_id, customer_id, payload, status) "
                                        "VALUES (:id, :session_id, :customer_id, :payload, "
                                        "'queued')"
                                    ),
                                    {
                                        "id": uuid.uuid4(),
                                        "session_id": session_uuid,
                                        "customer_id": uuid.UUID(customer_id),
                                        "payload": json.dumps(handoff),
                                    },
                                )
                                await db.commit()

                            yield f"data: {json.dumps({'type': 'handoff', 'data': handoff})}\n\n"

                final_response = accumulated.get("response", "")
                if not response_streamed and final_response:
                    yield f"data: {json.dumps({'type': 'token', 'data': final_response})}\n\n"
                elif not response_streamed and not final_response:
                    fallback = "I'm sorry, I couldn't process your request. Please try again."
                    yield f"data: {json.dumps({'type': 'token', 'data': fallback})}\n\n"

                yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

                latency = time.time() - start_time
                CHAT_LATENCY.observe(latency)

                async with async_session() as db:
                    await db.execute(
                        text(
                            "INSERT INTO session_metrics "
                            "(session_id, turns, latency_p95_ms, updated_at) "
                            "VALUES (:session_id, 1, :latency, NOW()) "
                            "ON CONFLICT (session_id) DO UPDATE SET "
                            "turns = session_metrics.turns + 1, "
                            "latency_p95_ms = :latency, updated_at = NOW()"
                        ),
                        {"session_id": session_uuid, "latency": int(latency * 1000)},
                    )
                    await db.commit()

            except Exception as e:
                log.error("chat_error", error=str(e), session_id=req.session_id)
                error_payload = json.dumps(
                    {"type": "error", "data": "An internal error occurred. Please try again."}
                )
                yield f"data: {error_payload}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @application.get("/metrics")
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app = create_app()
