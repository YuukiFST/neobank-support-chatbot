"""Agent tools — wrappers around mock banking APIs and external APIs.

Every tool receives customer_id from session context (NOT from LLM extraction)
and validates ownership before returning data.
"""

from __future__ import annotations

import re
from typing import Any

import httpx
from fastapi import HTTPException

from services.agent_api.infrastructure import mock_banking_api as mock_api


async def get_balance(customer_id: str) -> str:
    """Get account balance for the customer."""
    data = await mock_api.get_balance(customer_id)
    return f"Account balance: R$ {data.balance:.2f}"


async def get_transactions(customer_id: str, limit: int = 10) -> str:
    """Get recent transactions for the customer."""
    data = await mock_api.get_transactions(customer_id, limit=limit)
    txns = data.transactions
    if not txns:
        return "No recent transactions found."
    lines = []
    for t in txns:
        lines.append(
            f"- {t['created_at'][:10]} | {t['type']} | R$ {float(t['amount']):.2f} | {t['status']} | {t.get('description', '')}"
        )
    return "Recent transactions:\n" + "\n".join(lines)


async def get_cards(customer_id: str) -> str:
    """Get all cards for the customer."""
    cards = await mock_api.get_cards(customer_id)
    if not cards:
        return "No cards found."
    lines = []
    for c in cards:
        lines.append(
            f"- Card ****{c.last_four} (id={c.card_id}, {c.kind}) | {c.state} | Limit: R$ {c.limit_amount:.2f}"
        )
    return "Cards:\n" + "\n".join(lines)


async def get_invoice(card_id: str, customer_id: str) -> str:
    """Get the open invoice for a card. Validates card belongs to customer."""
    cards = await mock_api.get_cards(customer_id)
    owned_ids = {c.card_id for c in cards}
    if card_id not in owned_ids:
        return f"Error: Card {card_id} does not belong to this customer."

    try:
        inv = await mock_api.get_invoice(card_id)
        return (
            f"Invoice for {inv.month}: R$ {inv.total:.2f} "
            f"(status: {inv.status}, due: {inv.due_date or 'N/A'})"
        )
    except HTTPException:
        return "No open invoice found for this card."


async def pay_invoice(card_id: str, customer_id: str) -> str:
    """Pay the open invoice for a card (simulated). Validates ownership."""
    cards = await mock_api.get_cards(customer_id)
    owned_ids = {c.card_id for c in cards}
    if card_id not in owned_ids:
        return f"Error: Card {card_id} does not belong to this customer."

    result = await mock_api.pay_invoice(card_id)
    return result.message


async def request_limit_increase(card_id: str, customer_id: str) -> str:
    """Request a credit limit increase. Validates ownership."""
    cards = await mock_api.get_cards(customer_id)
    owned_ids = {c.card_id for c in cards}
    if card_id not in owned_ids:
        return f"Error: Card {card_id} does not belong to this customer."

    result = await mock_api.request_limit_increase(card_id)
    if result.approved:
        return f"Limit increase approved: R$ {result.new_limit:.2f}. {result.reason or ''}"
    return f"Limit increase denied. Reason: {result.reason or 'Risk assessment'}"


async def block_card(card_id: str, customer_id: str) -> str:
    """Block a card (simulated). Validates ownership."""
    cards = await mock_api.get_cards(customer_id)
    owned_ids = {c.card_id for c in cards}
    if card_id not in owned_ids:
        return f"Error: Card {card_id} does not belong to this customer."

    result = await mock_api.block_card(card_id)
    return result.message


async def get_investments(customer_id: str) -> str:
    """Get investment holdings for the customer."""
    data = await mock_api.get_investments(customer_id)
    invs = data.investments
    if not invs:
        return "No investments found."
    lines = [f"- {i['product'].upper()}: R$ {float(i['principal']):.2f}" for i in invs]
    return "Investments:\n" + "\n".join(lines)


async def lookup_cep(cep: str) -> str:
    """Look up a Brazilian CEP via ViaCEP (free, keyless)."""
    clean_cep = re.sub(r"\D", "", cep)
    if len(clean_cep) != 8:
        return "Error: Invalid CEP format."
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"https://viacep.com.br/ws/{clean_cep}/json/")
        resp.raise_for_status()
        data = resp.json()
        if data.get("erro"):
            return f"CEP {cep} not found."
        return (
            f"{data.get('logradouro', '')}, {data.get('bairro', '')}, "
            f"{data.get('localidade', '')} - {data.get('uf', '')}"
        )


async def get_currency_quote() -> str:
    """Get USD/BRL exchange rate via AwesomeAPI (free, keyless)."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
        resp.raise_for_status()
        data = resp.json()
        usd = data.get("USDBRL", {})
        return f"USD/BRL: R$ {usd.get('bid', 'N/A')} (ask: R$ {usd.get('ask', 'N/A')})"


# --- Tool registry for LangGraph ---

TOOL_REGISTRY: dict[str, Any] = {
    "get_balance": get_balance,
    "get_transactions": get_transactions,
    "get_cards": get_cards,
    "get_invoice": get_invoice,
    "pay_invoice": pay_invoice,
    "request_limit_increase": request_limit_increase,
    "block_card": block_card,
    "get_investments": get_investments,
    "lookup_cep": lookup_cep,
    "get_currency_quote": get_currency_quote,
}

# Intent → tools to run before specialist LLM call
INTENT_TOOLS: dict[str, list[str]] = {
    "balance": ["get_balance"],
    "pix_status": ["get_transactions"],
    "card_invoice": ["get_cards"],
    "card_pay": ["get_cards"],
    "limit_increase": ["get_cards"],
    "block_card": ["get_cards"],
    "fraud_dispute": ["get_transactions", "get_cards"],
}


async def execute_tools_for_intent(intent: str, customer_id: str) -> list[str]:
    """Run registered tools for the given intent and return result strings."""
    tool_names = INTENT_TOOLS.get(intent, [])
    results: list[str] = []
    for name in tool_names:
        fn = TOOL_REGISTRY[name]
        try:
            results.append(await fn(customer_id))
        except Exception as exc:
            results.append(f"Tool {name} failed: {exc}")

    # For card_invoice, also fetch invoice for first card if available
    if intent == "card_invoice" and results:
        cards = await mock_api.get_cards(customer_id)
        if cards:
            inv_result = await get_invoice(cards[0].card_id, customer_id)
            results.append(inv_result)

    return results
