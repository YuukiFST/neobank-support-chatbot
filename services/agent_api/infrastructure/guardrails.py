"""Guardrails — deterministic pre/post-LLM checks.

guardrail_in:  PII detection, prompt-injection heuristics, out-of-scope rejection.
guardrail_out: blocks data leakage, hallucinated financial advice, secret patterns.
"""

from __future__ import annotations

import re
from typing import Any

# --- PII patterns ---
CPF_PATTERN = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"\(?\d{2}\)?\s*\d{4,5}-?\d{4}")
ACCOUNT_MASK_PATTERN = re.compile(r"\d{4}\.\d{4}\.\d{4}\.\d{4}")

# --- Prompt injection heuristics ---
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"act\s+as\s+if", re.IGNORECASE),
    re.compile(r"pretend\s+you", re.IGNORECASE),
    re.compile(r"disregard", re.IGNORECASE),
    re.compile(r"new\s+instructions", re.IGNORECASE),
    re.compile(r"DAN\s+mode", re.IGNORECASE),
]

# --- Financial advice denylist ---
FINANCIAL_ADVICE_PATTERNS = [
    re.compile(r"i\s+(strongly\s+)?recommend\s+(investing|buying|selling|trading)", re.IGNORECASE),
    re.compile(r"you\s+should\s+(invest|buy|sell|trade|transfer\s+all)", re.IGNORECASE),
    re.compile(r"guaranteed\s+(returns?|profit|yield)", re.IGNORECASE),
    re.compile(r"risk[\s-]*free\s+investment", re.IGNORECASE),
]

# --- Secret patterns ---
SECRET_PATTERNS = [
    re.compile(r"api[_-]?key\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]+", re.IGNORECASE),  # OpenAI-style API keys
    re.compile(r"ghp_[A-Za-z0-9]+", re.IGNORECASE),  # GitHub tokens
]


class GuardrailResult:
    __slots__ = ("passed", "reason", "blocked_pii", "injection_detected", "advice_detected", "secret_detected")

    def __init__(
        self,
        passed: bool = True,
        reason: str = "",
        blocked_pii: list[str] | None = None,
        injection_detected: bool = False,
        advice_detected: bool = False,
        secret_detected: bool = False,
    ) -> None:
        self.passed = passed
        self.reason = reason
        self.blocked_pii = blocked_pii or []
        self.injection_detected = injection_detected
        self.advice_detected = advice_detected
        self.secret_detected = secret_detected


def guardrail_in(message: str, customer_document: str = "") -> GuardrailResult:
    """Pre-LLM guardrail: detect injection attempts and out-of-scope requests.

    Does NOT extract customer id from the message — that comes from session context only.
    """
    # Prompt injection detection
    for pattern in INJECTION_PATTERNS:
        if pattern.search(message):
            return GuardrailResult(
                passed=False,
                reason="Prompt injection attempt detected",
                injection_detected=True,
            )

    # Check if message contains another customer's CPF (potential injection)
    cpfs = CPF_PATTERN.findall(message)
    if customer_document and cpfs:
        # Normalize for comparison
        clean_doc = re.sub(r"\D", "", customer_document)
        for cpf in cpfs:
            clean_cpf = re.sub(r"\D", "", cpf)
            if clean_cpf != clean_doc and len(clean_cpf) == 11:
                return GuardrailResult(
                    passed=False,
                    reason="Attempt to access another customer's data",
                    blocked_pii=[cpf],
                )

    return GuardrailResult(passed=True)


def guardrail_out(response: str, customer_document: str = "") -> GuardrailResult:
    """Post-LLM guardrail: block data leakage and financial advice."""
    # Financial advice detection
    for pattern in FINANCIAL_ADVICE_PATTERNS:
        if pattern.search(response):
            return GuardrailResult(
                passed=False,
                reason="Financial advice detected in response",
                advice_detected=True,
            )

    # Secret leakage detection
    for pattern in SECRET_PATTERNS:
        if pattern.search(response):
            return GuardrailResult(
                passed=False,
                reason="Secret/token pattern detected in response",
                secret_detected=True,
            )

    # PII leakage — check for CPF patterns not belonging to the customer
    if customer_document:
        clean_doc = re.sub(r"\D", "", customer_document)
        cpfs = CPF_PATTERN.findall(response)
        for cpf in cpfs:
            clean_cpf = re.sub(r"\D", "", cpf)
            if clean_cpf != clean_doc and len(clean_cpf) == 11:
                return GuardrailResult(
                    passed=False,
                    reason="Customer PII leakage detected",
                    blocked_pii=[cpf],
                )

    return GuardrailResult(passed=True)
