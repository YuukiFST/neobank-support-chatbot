"""Unit tests for domain models."""

import uuid
from decimal import Decimal

import pytest
from shared.domain.models import (
    Account,
    Card,
    CardKind,
    CardState,
    Customer,
    HandoffPayload,
    Intent,
    Investment,
    InvestmentProduct,
    Language,
    Transaction,
    TransactionStatus,
    TransactionType,
)


class TestCustomer:
    def test_create_customer(self):
        c = Customer(name="Maria", document="123.456.789-00")
        assert c.name == "Maria"
        assert c.language == Language.PT

    def test_customer_with_english(self):
        c = Customer(name="John", document="987.654.321-00", language=Language.EN)
        assert c.language == Language.EN


class TestAccount:
    def test_create_account(self):
        a = Account(customer_id=uuid.uuid4(), balance=Decimal("1500.50"))
        assert a.balance == Decimal("1500.50")


class TestTransaction:
    def test_pix_transaction(self):
        t = Transaction(
            account_id=uuid.uuid4(),
            type=TransactionType.PIX,
            amount=Decimal("100.00"),
        )
        assert t.type == TransactionType.PIX
        assert t.status == TransactionStatus.SETTLED

    def test_risk_flagged_transaction(self):
        t = Transaction(
            account_id=uuid.uuid4(),
            type=TransactionType.CARD,
            amount=Decimal("2500.00"),
            risk_flag=True,
        )
        assert t.risk_flag is True


class TestCard:
    def test_credit_card(self):
        c = Card(
            account_id=uuid.uuid4(),
            kind=CardKind.CREDIT,
            limit_amount=Decimal("5000.00"),
            last_four="4532",
        )
        assert c.kind == CardKind.CREDIT
        assert c.state == CardState.ACTIVE

    def test_block_card(self):
        c = Card(
            account_id=uuid.uuid4(),
            kind=CardKind.DEBIT,
            state=CardState.BLOCKED,
        )
        assert c.state == CardState.BLOCKED


class TestInvestment:
    def test_cdb_investment(self):
        inv = Investment(
            customer_id=uuid.uuid4(),
            product=InvestmentProduct.CDB,
            principal=Decimal("10000.00"),
        )
        assert inv.product == InvestmentProduct.CDB


class TestHandoffPayload:
    def test_create_handoff(self):
        h = HandoffPayload(
            session_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            intent=Intent.FRAUD_DISPUTE,
            conversation_summary="Customer reports unauthorized card usage",
            entities={"card_id": "1234"},
            risk_outcome="2 suspicious transactions found",
            suggested_resolution="Escalate to fraud team",
        )
        assert h.intent == Intent.FRAUD_DISPUTE
        assert "fraud" in h.suggested_resolution.lower()
