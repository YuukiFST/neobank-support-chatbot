"""Shared pytest fixtures for NeoBank tests."""

from __future__ import annotations

import os
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


async def _db_available() -> bool:
    try:
        from sqlalchemy import text

        from shared.infrastructure.database import async_session

        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_db: test needs a running PostgreSQL instance")


_STDCXX = "/nix/store/hngmi01i8wgi25a0byrxcn4ysz5j79mw-gcc-15.2.0-lib/lib"
if os.path.isdir(_STDCXX):
    os.environ.setdefault("LD_LIBRARY_PATH", _STDCXX)

from services.agent_api.infrastructure.mock_banking_api import load_seed_data  # noqa: E402

CUSTOMER_MARIA = "11111111-1111-1111-1111-111111111111"
ACCOUNT_MARIA = "aaaa1111-1111-1111-1111-111111111111"
CARD_MARIA_CREDIT = "cccc1111-1111-1111-1111-111111111111"


def _test_seed_data() -> dict:
    """Static seed data for tests — no database required."""
    return {
        "customers": {
            CUSTOMER_MARIA: {
                "id": CUSTOMER_MARIA,
                "name": "Maria Silva",
                "document": "123.456.789-00",
                "address_cep": "01310-100",
                "language": "pt",
            },
        },
        "accounts": {
            ACCOUNT_MARIA: {
                "id": ACCOUNT_MARIA,
                "customer_id": CUSTOMER_MARIA,
                "balance": 5250.75,
            },
        },
        "transactions": [
            {
                "id": str(uuid.uuid4()),
                "account_id": ACCOUNT_MARIA,
                "type": "pix",
                "amount": 150.00,
                "status": "settled",
                "risk_flag": False,
                "description": "PIX to João",
                "reference": "PIX-001",
                "created_at": "2025-01-15 10:30:00",
            },
        ],
        "cards": [
            {
                "id": CARD_MARIA_CREDIT,
                "account_id": ACCOUNT_MARIA,
                "kind": "credit",
                "state": "active",
                "limit_amount": 5000.00,
                "last_four": "4532",
            },
        ],
        "invoices": [
            {
                "id": str(uuid.uuid4()),
                "card_id": CARD_MARIA_CREDIT,
                "month": "2025-01",
                "total": 456.78,
                "status": "open",
                "due_date": "2025-02-10",
            },
        ],
        "investments": [
            {
                "id": str(uuid.uuid4()),
                "customer_id": CUSTOMER_MARIA,
                "product": "cdb",
                "principal": 10000.00,
            },
        ],
    }


@pytest.fixture(autouse=True)
def seed_mock_api():
    """Load mock banking data before every test."""
    load_seed_data(_test_seed_data())


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for integration/e2e tests."""
    from services.agent_api.application.agent import create_agent_graph
    from services.agent_api.interface.app import app

    app.state.agent_graph = create_agent_graph()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def e2e_client():
    """E2E client with fake DB and mock LLM — no Postgres/Ollama required."""
    from unittest.mock import patch

    from services.agent_api.application.agent import create_agent_graph
    from services.agent_api.interface.app import app
    from tests.support.fake_db import FakeSessionMaker, reset_fake_db
    from tests.support.mock_llm import mock_llm_completion

    reset_fake_db()
    app.state.agent_graph = create_agent_graph()

    with (
        patch("services.agent_api.interface.app.async_session", FakeSessionMaker()),
        patch("services.agent_api.application.agent.llm_completion", mock_llm_completion),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture
async def require_db():
    """Skip test if PostgreSQL is not reachable."""
    if not await _db_available():
        pytest.skip("PostgreSQL not available")
