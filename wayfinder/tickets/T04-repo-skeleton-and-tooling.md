<!-- label: wayfinder:grilling -->
<!-- blocks: (none) -->
<!-- assignee: (unclaimed) -->

# T04 — Repo skeleton + tooling

## Question

Decide the project's foundation so every later build ticket has a home.

Decide: Python version; package/dependency manager (uv vs poetry vs pip-tools); project layout (`src/` package, `tests/`, `docs/`, `wayfinder/`); lint/format (ruff, mypy); test runner (pytest); pre-commit hooks; free CI (GitHub Actions — lint + test on push); core dependencies pinned (langchain, langgraph, langchain-groq, langchain-ollama, fastapi, the vector store, the web-chat lib). Naming/idioms in English.

Output: a decided skeleton (dir tree + tool choices + dependency list). Blocks observability (T09) and interface (T12). Use `/grilling`.
