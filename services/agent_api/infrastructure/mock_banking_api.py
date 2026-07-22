"""Mock banking APIs — FastAPI sub-app mounted at /mock.

Internal REST endpoints simulating banking operations.
Deliberate fault injection via FAULT_RATE for retry/backoff testing.
"""

from __future__ import annotations

import random
import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from shared.infrastructure.auth import verify_api_key
from shared.infrastructure.config import settings

_mock_deps = [Depends(verify_api_key)] if settings.api_key or settings.environment == "prod" else []
router = APIRouter(prefix="/mock", tags=["mock-banking"], dependencies=_mock_deps)


# --- Request/Response models ---

class BalanceResponse(BaseModel):
    customer_id: str
    account_id: str
    balance: float


class TransactionsResponse(BaseModel):
    customer_id: str
    transactions: list[dict[str, Any]]


class CardResponse(BaseModel):
    card_id: str
    account_id: str
    kind: str
    state: str
    limit_amount: float
    last_four: str


class InvoiceResponse(BaseModel):
    invoice_id: str
    card_id: str
    month: str
    total: float
    status: str
    due_date: str | None = None


class PayInvoiceResponse(BaseModel):
    invoice_id: str
    status: str
    message: str


class LimitIncreaseResponse(BaseModel):
    card_id: str
    approved: bool
    new_limit: float | None = None
    reason: str


class BlockCardResponse(BaseModel):
    card_id: str
    state: str
    message: str


class InvestmentsResponse(BaseModel):
    customer_id: str
    investments: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    error: dict[str, Any]


# --- Fault injection ---

def _check_fault() -> None:
    if settings.fault_rate > 0 and random.random() < settings.fault_rate:
        if random.random() < 0.5:
            raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": "Simulated failure", "retryable": True})
        raise HTTPException(status_code=504, detail={"code": "TIMEOUT", "message": "Simulated timeout", "retryable": True})


# --- In-memory seed data (loaded from SQL seeds at startup) ---

_SEED_DATA: dict[str, Any] = {}


def load_seed_data(data: dict[str, Any]) -> None:
    """Load seed data from the database at startup."""
    _SEED_DATA.update(data)


# --- Endpoints ---

@router.get("/health")
async def mock_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/accounts/{customer_id}/balance", response_model=BalanceResponse)
async def get_balance(customer_id: str) -> BalanceResponse:
    _check_fault()
    accounts = _SEED_DATA.get("accounts", {})
    for acc in accounts.values():
        if acc["customer_id"] == customer_id:
            return BalanceResponse(
                customer_id=customer_id,
                account_id=acc["id"],
                balance=float(acc["balance"]),
            )
    raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Account not found", "retryable": False})


@router.get("/accounts/{customer_id}/transactions", response_model=TransactionsResponse)
async def get_transactions(customer_id: str, limit: int = 20) -> TransactionsResponse:
    _check_fault()
    accounts = _SEED_DATA.get("accounts", {})
    transactions = _SEED_DATA.get("transactions", [])
    account_ids = [a["id"] for a in accounts.values() if a["customer_id"] == customer_id]
    txns = [t for t in transactions if t["account_id"] in account_ids]
    txns = sorted(txns, key=lambda t: t["created_at"], reverse=True)[:limit]
    return TransactionsResponse(customer_id=customer_id, transactions=txns)


@router.get("/cards/{customer_id}", response_model=list[CardResponse])
async def get_cards(customer_id: str) -> list[CardResponse]:
    _check_fault()
    accounts = _SEED_DATA.get("accounts", {})
    cards = _SEED_DATA.get("cards", [])
    account_ids = [a["id"] for a in accounts.values() if a["customer_id"] == customer_id]
    return [
        CardResponse(
            card_id=c["id"],
            account_id=c["account_id"],
            kind=c["kind"],
            state=c["state"],
            limit_amount=float(c["limit_amount"]),
            last_four=c["last_four"],
        )
        for c in cards
        if c["account_id"] in account_ids
    ]


@router.get("/cards/{card_id}/invoice", response_model=InvoiceResponse)
async def get_invoice(card_id: str) -> InvoiceResponse:
    _check_fault()
    invoices = _SEED_DATA.get("invoices", [])
    for inv in invoices:
        if inv["card_id"] == card_id and inv["status"] == "open":
            return InvoiceResponse(
                invoice_id=inv["id"],
                card_id=inv["card_id"],
                month=inv["month"],
                total=float(inv["total"]),
                status=inv["status"],
                due_date=inv.get("due_date"),
            )
    raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "No open invoice found", "retryable": False})


@router.post("/cards/{card_id}/pay", response_model=PayInvoiceResponse)
async def pay_invoice(card_id: str) -> PayInvoiceResponse:
    _check_fault()
    invoices = _SEED_DATA.get("invoices", [])
    for inv in invoices:
        if inv["card_id"] == card_id and inv["status"] == "open":
            inv["status"] = "paid"
            return PayInvoiceResponse(
                invoice_id=inv["id"],
                status="paid",
                message=f"Invoice for {inv['month']} paid successfully (simulated)",
            )
    raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "No open invoice found", "retryable": False})


@router.post("/cards/{card_id}/limit-increase", response_model=LimitIncreaseResponse)
async def request_limit_increase(card_id: str) -> LimitIncreaseResponse:
    _check_fault()
    cards = _SEED_DATA.get("cards", [])
    for card in cards:
        if card["id"] == card_id:
            current_limit = float(card["limit_amount"])
            max_auto = current_limit * 1.5
            return LimitIncreaseResponse(
                card_id=card_id,
                approved=True,
                new_limit=max_auto,
                reason=f"Auto-approved: {current_limit:.2f} -> {max_auto:.2f} (within 1.5x ceiling, no risk flags)",
            )
    raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Card not found", "retryable": False})


@router.post("/cards/{card_id}/block", response_model=BlockCardResponse)
async def block_card(card_id: str) -> BlockCardResponse:
    _check_fault()
    cards = _SEED_DATA.get("cards", [])
    for card in cards:
        if card["id"] == card_id:
            card["state"] = "blocked"
            return BlockCardResponse(
                card_id=card_id,
                state="blocked",
                message="Card blocked successfully (simulated). A replacement card will be sent.",
            )
    raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Card not found", "retryable": False})


@router.get("/investments/{customer_id}", response_model=InvestmentsResponse)
async def get_investments(customer_id: str) -> InvestmentsResponse:
    _check_fault()
    investments = _SEED_DATA.get("investments", [])
    return InvestmentsResponse(
        customer_id=customer_id,
        investments=[i for i in investments if i["customer_id"] == customer_id],
    )
