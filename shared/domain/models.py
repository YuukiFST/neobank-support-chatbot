"""DDD domain models — entities, value objects, enums."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

# --- Enums ---


class TransactionType(enum.StrEnum):
    PIX = "pix"
    TRANSFER = "transfer"
    CARD = "card"
    FEE = "fee"


class TransactionStatus(enum.StrEnum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"


class CardKind(enum.StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class CardState(enum.StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class InvoiceStatus(enum.StrEnum):
    OPEN = "open"
    PAID = "paid"


class InvestmentProduct(enum.StrEnum):
    CDB = "cdb"
    SAVINGS = "savings"


class HandoffStatus(enum.StrEnum):
    QUEUED = "queued"
    CLAIMED = "claimed"
    RESOLVED = "resolved"


class Intent(enum.StrEnum):
    BALANCE = "balance"
    PIX_STATUS = "pix_status"
    CARD_INVOICE = "card_invoice"
    CARD_PAY = "card_pay"
    LIMIT_INCREASE = "limit_increase"
    BLOCK_CARD = "block_card"
    FRAUD_DISPUTE = "fraud_dispute"
    FAQ = "faq"
    HUMAN = "human"


class Language(enum.StrEnum):
    PT = "pt"
    EN = "en"


# --- Entities ---


class Customer(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    document: str  # CPF mask
    address_cep: str | None = None
    language: Language = Language.PT
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Account(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID
    balance: Decimal = Decimal("0.00")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    account_id: uuid.UUID
    type: TransactionType
    amount: Decimal
    status: TransactionStatus = TransactionStatus.SETTLED
    risk_flag: bool = False
    description: str | None = None
    reference: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Card(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    account_id: uuid.UUID
    kind: CardKind
    state: CardState = CardState.ACTIVE
    limit_amount: Decimal = Decimal("0.00")
    last_four: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Invoice(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    card_id: uuid.UUID
    month: str  # YYYY-MM
    total: Decimal = Decimal("0.00")
    status: InvoiceStatus = InvoiceStatus.OPEN
    due_date: date | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Investment(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID
    product: InvestmentProduct
    principal: Decimal
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID
    language: Language = Language.PT
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)


class Handoff(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID
    customer_id: uuid.UUID
    payload: dict[str, Any]
    status: HandoffStatus = HandoffStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionMetrics(BaseModel):
    session_id: uuid.UUID
    tokens_in: int = 0
    tokens_out: int = 0
    cost_brl_equiv: Decimal = Decimal("0.00")
    latency_p95_ms: int = 0
    turns: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerFact(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID
    fact: str
    source_session_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- Handoff payload (structured escalation) ---


class HandoffPayload(BaseModel):
    session_id: uuid.UUID
    customer_id: uuid.UUID
    intent: Intent
    conversation_summary: str
    entities: dict[str, Any] = Field(default_factory=dict)
    risk_outcome: str | None = None
    suggested_resolution: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
