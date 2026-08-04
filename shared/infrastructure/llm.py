"""LiteLLM gateway — provider-swappable LLM calls."""

from __future__ import annotations

from typing import Any

from shared.infrastructure.config import Settings, settings


def _resolve_model(cfg: Settings | None = None) -> str:
    """Map provider env to a LiteLLM model string."""
    cfg = cfg or settings
    provider = cfg.llm_provider.lower()
    if provider == "ollama":
        return f"ollama/{cfg.ollama_model}"
    if provider == "groq":
        return "groq/llama-3.1-8b-instant"
    if provider == "gemini":
        return "gemini/gemini-2.0-flash"
    return f"ollama/{cfg.ollama_model}"


def _litellm_kwargs(cfg: Settings | None = None) -> dict[str, Any]:
    """Provider-specific kwargs for LiteLLM."""
    cfg = cfg or settings
    kwargs: dict[str, Any] = {}
    provider = cfg.llm_provider.lower()
    if provider == "ollama":
        kwargs["api_base"] = cfg.ollama_base_url
    elif provider == "groq" and cfg.groq_api_key:
        kwargs["api_key"] = cfg.groq_api_key
    elif provider == "gemini" and cfg.gemini_api_key:
        kwargs["api_key"] = cfg.gemini_api_key
    return kwargs


async def llm_completion(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 1024,
    **kwargs: Any,
) -> dict[str, Any]:
    """Single completion call via LiteLLM."""
    import litellm

    litellm.suppress_debug_info = True
    model = _resolve_model()
    call_kwargs = {**_litellm_kwargs(), **kwargs}

    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **call_kwargs,
        )
    except Exception as exc:
        return {
            "content": (
                "I'm sorry, I'm having trouble connecting to the AI service. "
                "Please try again shortly."
            ),
            "tokens_in": 0,
            "tokens_out": 0,
            "model": model,
            "error": str(exc),
        }

    return {
        "content": response.choices[0].message.content or "",
        "tokens_in": response.usage.prompt_tokens if response.usage else 0,
        "tokens_out": response.usage.completion_tokens if response.usage else 0,
        "model": response.model,
    }
