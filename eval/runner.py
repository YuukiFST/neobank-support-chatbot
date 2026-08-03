"""Eval runner — runs eval set against the agent and scores results."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage

from services.agent_api.application.agent import create_agent_graph, merge_graph_state


async def run_eval_item(item: dict[str, Any], graph: Any) -> dict[str, Any]:
    """Run a single eval item and return the result."""
    state = {
        "messages": [HumanMessage(content=item["input"])],
        "customer_id": "11111111-1111-1111-1111-111111111111",
        "customer_document": "123.456.789-00",
        "session_id": f"eval-{item['id']}",
        "language": item["language"],
        "intent": "",
        "tool_calls": [],
        "tool_results": [],
        "response": "",
        "handoff": None,
        "guardrail_in_result": None,
        "guardrail_out_result": None,
        "error": None,
    }

    try:
        accumulated: dict[str, Any] = dict(state)
        async for event in graph.astream(state):
            for _node_name, node_output in event.items():
                accumulated = merge_graph_state(accumulated, node_output)

        actual_intent = accumulated.get("intent", "")
        actual_response = accumulated.get("response", "")
        handoff = accumulated.get("handoff")

        # Check results
        intent_correct = actual_intent == item["expected_intent"]
        escalation_correct = (handoff is not None) == item["expected_escalation"]

        # Check outcome contains expected phrases
        outcome_contains = all(
            phrase.lower() in actual_response.lower()
            for phrase in item.get("expected_outcome_contains", [])
        )

        return {
            "id": item["id"],
            "input": item["input"],
            "expected_intent": item["expected_intent"],
            "actual_intent": actual_intent,
            "intent_correct": intent_correct,
            "expected_escalation": item["expected_escalation"],
            "actual_escalation": handoff is not None,
            "escalation_correct": escalation_correct,
            "outcome_contains": outcome_contains,
            "response_preview": actual_response[:200],
            "passed": intent_correct and escalation_correct and outcome_contains,
        }
    except Exception as e:
        return {
            "id": item["id"],
            "input": item["input"],
            "error": str(e),
            "passed": False,
        }


async def run_eval(eval_path: str = "eval/eval_set.jsonl") -> dict[str, Any]:
    """Run the full eval set."""
    # Load eval items
    items = []
    with open(eval_path) as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))

    print(f"Running {len(items)} eval items...")

    # Build graph
    graph = create_agent_graph()

    # Run items
    results = []
    for item in items:
        result = await run_eval_item(item, graph)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {result['id']}: {result.get('actual_intent', 'error')}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\nResults: {passed}/{total} passed ({passed / total * 100:.1f}%)")

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "results": results,
    }


if __name__ == "__main__":
    asyncio.run(run_eval())
