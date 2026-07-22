"""LangGraph multi-agent graph — supervisor + specialists + guardrails.

Architecture:
input → [guardrail_in] → [supervisor/router] → specialist → [guardrail_out] → response
                                                ↘ [escalation] → handoff
"""

from __future__ import annotations

import json
import re
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

from shared.infrastructure.llm import llm_completion
from shared.infrastructure.chroma_client import query_kb
from shared.infrastructure.observability import log
from services.agent_api.infrastructure.guardrails import guardrail_in, guardrail_out
from services.agent_api.application.tools import execute_tools_for_intent


# --- State ---

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    customer_id: str
    customer_document: str
    session_id: str
    language: str
    intent: str
    tool_calls: list[dict]
    tool_results: list[str]
    response: str
    handoff: dict | None
    guardrail_in_result: dict | None
    guardrail_out_result: dict | None
    error: str | None


def _router_prompt(language: str) -> str:
    lang_name = "Portuguese" if language == "pt" else "English"
    return f"""You are the NeoBank support router. Classify the customer's intent.

Respond with ONLY a JSON object: {{"intent": "<intent_name>"}}
Valid intents: balance, pix_status, card_invoice, card_pay, limit_increase, block_card, fraud_dispute, faq, human

The customer is speaking {lang_name}.
Customer context: customer_id is provided in session — NEVER extract it from the message.

Examples:
User: "Qual meu saldo?" -> {{"intent": "balance"}}
User: "I want to block my card" -> {{"intent": "block_card"}}
User: "Someone used my card fraudulently" -> {{"intent": "fraud_dispute"}}
User: "How do fees work?" -> {{"intent": "faq"}}
User: "I want to talk to a human" -> {{"intent": "human"}}
"""


def _specialist_prompt(specialist: str, language: str) -> str:
    lang_name = "Portuguese" if language == "pt" else "English"
    prompts = {
        "account": f"""You are NeoBank's account specialist. Help with balance, statements, PIX, and transfers.
Speak in {lang_name}. Use ONLY the tool results provided in the context below.
Never fabricate financial data — only use what tools return.""",
        "card": f"""You are NeoBank's card specialist. Help with invoices, payments, limits, and blocking.
Speak in {lang_name}. Use ONLY the tool results provided in the context below.
Never fabricate financial data — only use what tools return.""",
        "kb": f"""You are NeoBank's knowledge base specialist. Answer FAQ questions about products and fees.
Speak in {lang_name}. Use the retrieved KB context provided below.
If you don't know, say so honestly — never make up product information.""",
        "risk": f"""You are NeoBank's risk specialist. Evaluate limit increase requests and fraud disputes.
Speak in {lang_name}. Use the transaction and card data provided in context.
Apply these rules:
- Limit increase: auto-approve up to 1.5x current limit if no risk-flagged transactions in 90 days, else escalate.
- Fraud dispute: always escalate with risk assessment.""",
    }
    return prompts.get(specialist, f"You are a NeoBank {specialist} specialist.")


# --- Graph nodes ---

def node_guardrail_in(state: AgentState) -> dict:
    """Pre-LLM guardrail: detect injection and out-of-scope requests."""
    last_msg = state["messages"][-1]
    content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    result = guardrail_in(content, state.get("customer_document", ""))
    log.info("guardrail_in", passed=result.passed, reason=result.reason)
    return {"guardrail_in_result": {"passed": result.passed, "reason": result.reason}}


async def async_router(state: AgentState) -> dict:
    """Async router node."""
    last_msg = state["messages"][-1]
    content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    language = state.get("language", "pt")

    messages = [
        {"role": "system", "content": _router_prompt(language)},
        {"role": "user", "content": content},
    ]

    result = await llm_completion(messages, temperature=0.0, max_tokens=100)
    content_text = result["content"].strip()

    intent = "human"
    try:
        json_match = re.search(r"\{[^}]+\}", content_text)
        if json_match:
            parsed = json.loads(json_match.group())
            intent = parsed.get("intent", "human")
    except (json.JSONDecodeError, KeyError):
        pass

    log.info("router", intent=intent, tokens_in=result["tokens_in"], tokens_out=result["tokens_out"])
    return {"intent": intent}


def _make_specialist_node(specialist_name: str):
    """Create an async specialist node that runs tools before LLM."""
    async def specialist_node(state: AgentState) -> dict:
        language = state.get("language", "pt")
        intent = state.get("intent", "")
        customer_id = state["customer_id"]
        system_prompt = _specialist_prompt(specialist_name, language)

        # Execute tools based on intent
        tool_results = await execute_tools_for_intent(intent, customer_id)

        # KB specialist: also query RAG
        if specialist_name == "kb":
            last_msg = state["messages"][-1]
            query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            kb_docs = query_kb(query)
            if kb_docs:
                tool_results.append("Knowledge base context:\n" + "\n---\n".join(kb_docs))

        context_block = ""
        if tool_results:
            context_block = "\n\n[Tool results — use ONLY this data]:\n" + "\n".join(tool_results)

        messages = [
            {"role": "system", "content": system_prompt + context_block},
            {"role": "system", "content": f"[Session: customer_id={customer_id}]"},
        ]

        for msg in state["messages"][-5:]:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            messages.append({"role": role, "content": msg.content})

        result = await llm_completion(messages, temperature=0.2, max_tokens=1024)
        log.info(
            f"specialist_{specialist_name}",
            tokens_in=result["tokens_in"],
            tokens_out=result["tokens_out"],
            tools_run=len(tool_results),
        )

        return {"response": result["content"], "tool_results": tool_results}

    return specialist_node


async def node_escalation(state: AgentState) -> dict:
    """Build handoff payload for human escalation."""
    language = state.get("language", "pt")
    intent = state.get("intent", "unknown")

    summary_parts = []
    for msg in state["messages"][-10:]:
        role = "Customer" if isinstance(msg, HumanMessage) else "Agent"
        content = msg.content if hasattr(msg, "content") else str(msg)
        summary_parts.append(f"{role}: {content[:200]}")
    summary = "\n".join(summary_parts)

    handoff = {
        "session_id": state["session_id"],
        "customer_id": state["customer_id"],
        "intent": intent,
        "conversation_summary": summary,
        "entities": {},
        "risk_outcome": state.get("response", ""),
        "suggested_resolution": f"Manual review required for intent: {intent}",
    }

    if language == "pt":
        response = (
            "Entendi. Vou transferir você para um atendente humano que poderá ajudá-lo melhor. "
            "Aguarde um momento, por favor."
        )
    else:
        response = (
            "I understand. I'm transferring you to a human agent who can help you further. "
            "Please hold on for a moment."
        )

    log.info("escalation_created", session_id=state["session_id"], intent=intent)
    return {"handoff": handoff, "response": response}


async def node_guardrail_out(state: AgentState) -> dict:
    """Post-LLM guardrail: check response for leaks and advice."""
    response = state.get("response", "")
    result = guardrail_out(response, state.get("customer_document", ""))
    log.info("guardrail_out", passed=result.passed, reason=result.reason)

    if not result.passed:
        return {
            "response": "I'm sorry, I cannot provide that information. Let me connect you with a human agent.",
            "guardrail_out_result": {"passed": False, "reason": result.reason},
        }
    return {"guardrail_out_result": {"passed": True}}


# --- Route logic ---

def route_after_guardrail_in(state: AgentState) -> str:
    if state.get("guardrail_in_result", {}).get("passed", True):
        return "router"
    return "blocked_response"


def route_after_router(state: AgentState) -> str:
    intent = state.get("intent", "human")
    if intent in ("balance", "pix_status"):
        return "account_specialist"
    if intent in ("card_invoice", "card_pay", "limit_increase", "block_card"):
        return "card_specialist"
    if intent == "fraud_dispute":
        return "risk_specialist"
    if intent == "faq":
        return "kb_specialist"
    return "escalation"


async def node_blocked_response(state: AgentState) -> dict:
    """Response when guardrail_in blocks the message."""
    return {"response": "I'm sorry, I cannot process that request. Please try rephrasing your question."}


def merge_graph_state(accumulated: dict, delta: dict) -> dict:
    """Merge LangGraph node deltas into accumulated state."""
    merged = {**accumulated}
    for key, value in delta.items():
        if value is not None:
            merged[key] = value
    return merged


# --- Build graph ---

def create_agent_graph():
    """Build the LangGraph multi-agent graph."""
    graph = StateGraph(AgentState)

    graph.add_node("guardrail_in", node_guardrail_in)
    graph.add_node("blocked_response", node_blocked_response)
    graph.add_node("router", async_router)
    graph.add_node("account_specialist", _make_specialist_node("account"))
    graph.add_node("card_specialist", _make_specialist_node("card"))
    graph.add_node("kb_specialist", _make_specialist_node("kb"))
    graph.add_node("risk_specialist", _make_specialist_node("risk"))
    graph.add_node("escalation", node_escalation)
    graph.add_node("guardrail_out", node_guardrail_out)

    graph.set_entry_point("guardrail_in")
    graph.add_conditional_edges("guardrail_in", route_after_guardrail_in, {
        "router": "router",
        "blocked_response": "blocked_response",
    })
    graph.add_conditional_edges("router", route_after_router, {
        "account_specialist": "account_specialist",
        "card_specialist": "card_specialist",
        "kb_specialist": "kb_specialist",
        "risk_specialist": "risk_specialist",
        "escalation": "escalation",
    })

    for specialist in ["account_specialist", "card_specialist", "kb_specialist"]:
        graph.add_edge(specialist, "guardrail_out")

    graph.add_edge("risk_specialist", "escalation")
    graph.add_edge("escalation", "guardrail_out")
    graph.add_edge("guardrail_out", END)
    graph.add_edge("blocked_response", END)

    return graph.compile()
