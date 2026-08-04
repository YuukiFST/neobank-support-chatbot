"""Observability — structured logging, Langfuse tracing, Prometheus metrics."""

# --- Structured logging ---
import logging

import structlog
from prometheus_client import Counter, Gauge, Histogram

from shared.infrastructure.config import settings

_log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if settings.log_level == "DEBUG"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(_log_level),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger("neobank")

# --- Prometheus metrics ---
CHAT_REQUESTS = Counter(
    "neobank_chat_requests_total", "Total chat requests", ["intent", "language"]
)
CHAT_TOKENS_IN = Counter("neobank_chat_tokens_in_total", "Total input tokens")
CHAT_TOKENS_OUT = Counter("neobank_chat_tokens_out_total", "Total output tokens")
CHAT_LATENCY = Histogram(
    "neobank_chat_latency_seconds", "Chat request latency", buckets=[0.5, 1, 2, 5, 10, 30]
)
ACTIVE_SESSIONS = Gauge("neobank_active_sessions", "Active sessions")
ESCALATIONS = Counter("neobank_escalations_total", "Total escalations", ["intent"])
KB_RETRIEVALS = Counter("neobank_kb_retrievals_total", "KB retrieval calls")
KB_CACHE_HITS = Counter("neobank_kb_cache_hits_total", "KB cache hits")
