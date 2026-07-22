"""Integration tests for mock banking API — uses shared client fixture from conftest."""

import pytest

from tests.conftest import CUSTOMER_MARIA


class TestMockBankingAPI:
    @pytest.mark.asyncio
    async def test_mock_health(self, client):
        resp = await client.get("/mock/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_balance(self, client):
        resp = await client.get(f"/mock/accounts/{CUSTOMER_MARIA}/balance")
        assert resp.status_code == 200
        data = resp.json()
        assert "balance" in data
        assert data["customer_id"] == CUSTOMER_MARIA

    @pytest.mark.asyncio
    async def test_get_transactions(self, client):
        resp = await client.get(f"/mock/accounts/{CUSTOMER_MARIA}/transactions")
        assert resp.status_code == 200
        data = resp.json()
        assert "transactions" in data

    @pytest.mark.asyncio
    async def test_get_cards(self, client):
        resp = await client.get(f"/mock/cards/{CUSTOMER_MARIA}")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_investments(self, client):
        resp = await client.get(f"/mock/investments/{CUSTOMER_MARIA}")
        assert resp.status_code == 200
        data = resp.json()
        assert "investments" in data


class TestHealthEndpoint:
    @pytest.mark.asyncio
    @pytest.mark.requires_db
    async def test_health(self, client, require_db):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestSessionEndpoint:
    @pytest.mark.asyncio
    @pytest.mark.requires_db
    async def test_create_session(self, client, require_db):
        resp = await client.post(
            "/sessions",
            json={"customer_id": CUSTOMER_MARIA, "language": "pt"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert data["language"] == "pt"

    @pytest.mark.asyncio
    @pytest.mark.requires_db
    async def test_create_session_invalid_customer(self, client, require_db):
        resp = await client.post(
            "/sessions",
            json={"customer_id": "00000000-0000-0000-0000-000000000000", "language": "pt"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_session_invalid_uuid(self, client):
        resp = await client.post(
            "/sessions",
            json={"customer_id": "not-a-uuid", "language": "pt"},
        )
        assert resp.status_code == 400
