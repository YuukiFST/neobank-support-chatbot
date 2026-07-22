"""Application configuration — pydantic-settings from env vars."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"
    llm_models_path: str = "/mnt/Others/LLMs"  # Custom path for LLM models
    groq_api_key: str = ""
    gemini_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://neobank:neobank_secret@localhost:5432/neobank"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Chroma
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    # Mock API
    fault_rate: float = 0.0

    # Security
    api_key: str = ""  # empty = auth disabled (local dev)
    environment: str = "dev"  # set to "prod" to require api_key on /mock
    rate_limit_per_minute: int = 30

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
