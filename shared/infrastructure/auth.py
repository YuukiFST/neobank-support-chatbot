"""API key authentication — optional in dev, required when api_key is set."""

from __future__ import annotations

from fastapi import Header, HTTPException

from shared.infrastructure.config import settings


async def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """Reject requests when api_key is configured and header is missing/wrong."""
    if not settings.api_key:
        return
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
