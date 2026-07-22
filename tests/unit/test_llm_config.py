"""Unit tests for LLM configuration and tools."""

import pytest
from shared.infrastructure.config import Settings


class TestSettings:
    def test_default_settings(self):
        settings = Settings(
            _env_file=None,
            database_url="postgresql+asyncpg://test:test@localhost/test",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.llm_provider == "ollama"
        assert settings.fault_rate == 0.0

    def test_provider_switch(self):
        settings = Settings(
            _env_file=None,
            llm_provider="groq",
            database_url="postgresql+asyncpg://test:test@localhost/test",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.llm_provider == "groq"


class TestLLMModelResolution:
    def test_ollama_model(self):
        from shared.infrastructure.llm import _resolve_model

        cfg = Settings(
            _env_file=None,
            llm_provider="ollama",
            ollama_model="qwen3.5:9b",
            database_url="postgresql+asyncpg://test:test@localhost/test",
            redis_url="redis://localhost:6379/0",
        )
        model = _resolve_model(cfg)
        assert "qwen3.5" in model

    def test_groq_model(self):
        from shared.infrastructure.llm import _resolve_model

        cfg = Settings(
            _env_file=None,
            llm_provider="groq",
            database_url="postgresql+asyncpg://test:test@localhost/test",
            redis_url="redis://localhost:6379/0",
        )
        model = _resolve_model(cfg)
        assert "groq" in model.lower() or "llama" in model.lower()
