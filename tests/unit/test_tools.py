"""Unit tests for agent tools."""

import pytest

from services.agent_api.application.tools import (
    INTENT_TOOLS,
    TOOL_REGISTRY,
    execute_tools_for_intent,
    get_balance,
    get_cards,
)
from tests.conftest import CUSTOMER_MARIA


class TestToolRegistry:
    def test_registry_has_core_tools(self):
        assert "get_balance" in TOOL_REGISTRY
        assert "get_transactions" in TOOL_REGISTRY
        assert "get_cards" in TOOL_REGISTRY

    def test_intent_tools_mapped(self):
        assert "balance" in INTENT_TOOLS
        assert "pix_status" in INTENT_TOOLS
        assert "fraud_dispute" in INTENT_TOOLS


class TestToolExecution:
    @pytest.mark.asyncio
    async def test_get_balance_returns_data(self):
        result = await get_balance(CUSTOMER_MARIA)
        assert "5250.75" in result

    @pytest.mark.asyncio
    async def test_get_cards_returns_data(self):
        result = await get_cards(CUSTOMER_MARIA)
        assert "4532" in result

    @pytest.mark.asyncio
    async def test_execute_tools_for_balance_intent(self):
        results = await execute_tools_for_intent("balance", CUSTOMER_MARIA)
        assert len(results) == 1
        assert "5250.75" in results[0]

    @pytest.mark.asyncio
    async def test_execute_tools_for_unknown_intent(self):
        results = await execute_tools_for_intent("unknown", CUSTOMER_MARIA)
        assert results == []
