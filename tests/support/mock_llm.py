"""Deterministic LLM mock for E2E tests — no Ollama/Groq required."""

from __future__ import annotations

from typing import Any


def _intent_from_message(text: str) -> str:
    lower = text.lower()
    if any(
        w in lower
        for w in ("fraude", "fraud", "sem autorização", "unauthorized", "sem autorizacao")
    ):
        return "fraud_dispute"
    if any(w in lower for w in ("saldo", "balance")):
        return "balance"
    if any(w in lower for w in ("cartão", "cartões", "cartao", "card")):
        return "card_invoice"
    if any(w in lower for w in ("taxa", "fee", "faq")):
        return "faq"
    if any(w in lower for w in ("pix", "transfer")):
        return "pix_status"
    return "human"


async def mock_llm_completion(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 1024,
    **kwargs: Any,
) -> dict[str, Any]:
    """Return deterministic responses based on message content."""
    user_msg = ""
    system_parts: list[str] = []
    for m in messages:
        if m.get("role") == "user":
            user_msg = m.get("content", "")
        if m.get("role") == "system":
            system_parts.append(m.get("content", ""))
    system_msg = "\n".join(system_parts)

    # Router call
    if "classify" in system_msg.lower() or "router" in system_msg.lower():
        intent = _intent_from_message(user_msg)
        return {
            "content": f'{{"intent": "{intent}"}}',
            "tokens_in": 10,
            "tokens_out": 5,
            "model": "mock",
        }

    # Specialist call — echo tool results
    if "tool results" in system_msg.lower():
        if "5250.75" in system_msg or "5250" in system_msg:
            return {
                "content": "Seu saldo atual é R$ 5.250,75.",
                "tokens_in": 50,
                "tokens_out": 20,
                "model": "mock",
            }
        if "4532" in system_msg:
            return {
                "content": "Você possui um cartão de crédito terminado em 4532.",
                "tokens_in": 50,
                "tokens_out": 20,
                "model": "mock",
            }
        return {
            "content": "Posso ajudar com informações sobre taxas e produtos NeoBank.",
            "tokens_in": 50,
            "tokens_out": 20,
            "model": "mock",
        }

    # Risk specialist
    if "risk specialist" in system_msg.lower():
        return {
            "content": "Identifiquei uma possível fraude. Estou escalando para análise.",
            "tokens_in": 50,
            "tokens_out": 20,
            "model": "mock",
        }

    return {
        "content": "Como posso ajudar?",
        "tokens_in": 10,
        "tokens_out": 10,
        "model": "mock",
    }
