"""Smoke tests — verify project structure and imports without external services."""

from __future__ import annotations

import importlib
import sys


def test_imports() -> None:
    """All core modules import cleanly."""
    modules = [
        "services.agent_api.interface.app",
        "services.agent_api.application.agent",
        "services.agent_api.application.tools",
        "services.agent_api.infrastructure.guardrails",
        "services.agent_api.infrastructure.mock_banking_api",
        "services.ingestion_worker.application.etl_pipeline",
        "shared.infrastructure.config",
        "shared.infrastructure.llm",
        "shared.infrastructure.chroma_client",
        "shared.domain.models",
    ]
    for mod in modules:
        importlib.import_module(mod)


def test_create_app_factory() -> None:
    """create_app() returns a FastAPI instance with routes."""
    from services.agent_api.interface.app import create_app

    app = create_app()
    paths: set[str] = set()
    for route in app.routes:
        if hasattr(route, "path"):
            paths.add(route.path)
        if hasattr(route, "routes"):
            for sub in route.routes:
                if hasattr(sub, "path"):
                    paths.add(sub.path)

    assert "/health" in paths
    assert "/sessions" in paths
    assert "/chat" in paths


def test_agent_graph_compiles() -> None:
    """LangGraph agent compiles without error."""
    from services.agent_api.application.agent import create_agent_graph

    graph = create_agent_graph()
    assert graph is not None


def test_merge_graph_state() -> None:
    """State merge accumulates deltas correctly."""
    from services.agent_api.application.agent import merge_graph_state

    base = {"intent": "", "response": ""}
    merged = merge_graph_state(base, {"intent": "balance"})
    assert merged["intent"] == "balance"
    merged = merge_graph_state(merged, {"response": "R$ 100"})
    assert merged["intent"] == "balance"
    assert merged["response"] == "R$ 100"


if __name__ == "__main__":
    tests = [test_imports, test_create_app_factory, test_agent_graph_compiles, test_merge_graph_state]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
    sys.exit(1 if failed else 0)
