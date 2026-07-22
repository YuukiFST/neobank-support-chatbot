"""In-memory fake database for E2E tests without PostgreSQL."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import patch

from tests.conftest import CUSTOMER_MARIA, _test_seed_data

_SEED = _test_seed_data()
_CUSTOMERS = _SEED["customers"]
_SESSIONS: dict[str, dict[str, Any]] = {}
_HANDOFFS: list[dict[str, Any]] = []
_METRICS: dict[str, dict[str, Any]] = {}


class _FakeResult:
    def __init__(self, rows: list[tuple[Any, ...]] | None = None) -> None:
        self._rows = rows or []

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows


class FakeSession:
    async def execute(self, query: Any, params: dict[str, Any] | None = None) -> _FakeResult:
        sql = str(query).lower()
        params = params or {}

        if "select 1" in sql:
            return _FakeResult([(1,)])

        if "from customers where id" in sql and "document" not in sql:
            cid = str(params.get("id", ""))
            if cid in _CUSTOMERS:
                return _FakeResult([(uuid.UUID(cid),)])
            return _FakeResult()

        if "document from customers" in sql:
            cid = str(params.get("id", ""))
            cust = _CUSTOMERS.get(cid)
            if cust:
                return _FakeResult([(cust["document"],)])
            return _FakeResult()

        if "from customers" in sql and "where" not in sql:
            rows = [
                (uuid.UUID(c["id"]), c["name"], c["document"], c["address_cep"], c["language"])
                for c in _CUSTOMERS.values()
            ]
            return _FakeResult(rows)

        if "from accounts" in sql:
            rows = [
                (uuid.UUID(a["id"]), uuid.UUID(a["customer_id"]), a["balance"])
                for a in _SEED["accounts"].values()
            ]
            return _FakeResult(rows)

        if "from transactions" in sql:
            rows = [
                (
                    uuid.UUID(t["id"]),
                    uuid.UUID(t["account_id"]),
                    t["type"],
                    t["amount"],
                    t["status"],
                    t["risk_flag"],
                    t["description"],
                    t["reference"],
                    t["created_at"],
                )
                for t in _SEED["transactions"]
            ]
            return _FakeResult(rows)

        if "from cards" in sql:
            rows = [
                (
                    uuid.UUID(c["id"]),
                    uuid.UUID(c["account_id"]),
                    c["kind"],
                    c["state"],
                    c["limit_amount"],
                    c["last_four"],
                )
                for c in _SEED["cards"]
            ]
            return _FakeResult(rows)

        if "from invoices" in sql:
            rows = [
                (
                    uuid.UUID(i["id"]),
                    uuid.UUID(i["card_id"]),
                    i["month"],
                    i["total"],
                    i["status"],
                    i["due_date"],
                )
                for i in _SEED["invoices"]
            ]
            return _FakeResult(rows)

        if "from investments" in sql:
            rows = [
                (uuid.UUID(i["id"]), uuid.UUID(i["customer_id"]), i["product"], i["principal"])
                for i in _SEED["investments"]
            ]
            return _FakeResult(rows)

        if "from sessions where id" in sql:
            sid = str(params.get("id", ""))
            sess = _SESSIONS.get(sid)
            if sess:
                return _FakeResult([(uuid.UUID(sess["customer_id"]), sess["language"])])
            return _FakeResult()

        if "insert into sessions" in sql:
            sid = str(params.get("id", ""))
            _SESSIONS[sid] = {
                "customer_id": str(params.get("customer_id", "")),
                "language": params.get("language", "pt"),
            }
            return _FakeResult()

        if "insert into handoffs" in sql:
            _HANDOFFS.append(params)
            return _FakeResult()

        if "insert into session_metrics" in sql:
            sid = str(params.get("session_id", ""))
            _METRICS[sid] = {"latency": params.get("latency", 0)}
            return _FakeResult()

        return _FakeResult()

    async def commit(self) -> None:
        pass

    async def __aenter__(self) -> FakeSession:
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


class FakeSessionMaker:
    """Drop-in replacement for async_sessionmaker."""

    def __call__(self) -> FakeSession:
        return FakeSession()


def reset_fake_db() -> None:
    _SESSIONS.clear()
    _HANDOFFS.clear()
    _METRICS.clear()


@asynccontextmanager
async def use_fake_db():
    """Patch async_session to use in-memory fake for E2E tests."""
    reset_fake_db()
    with patch("services.agent_api.interface.app.async_session", FakeSessionMaker()):
        yield
