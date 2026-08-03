"""Unit tests for API key auth and rate limiting."""

import pytest
from fastapi import HTTPException

from shared.infrastructure.rate_limit import check_rate_limit, reset_rate_limits


class TestRateLimit:
    def setup_method(self) -> None:
        reset_rate_limits()

    def test_allows_under_limit(self) -> None:
        for _ in range(5):
            assert check_rate_limit("test-key", limit=10) is True

    def test_blocks_over_limit(self) -> None:
        for _ in range(3):
            check_rate_limit("burst-key", limit=3)
        assert check_rate_limit("burst-key", limit=3) is False


class TestApiKey:
    @pytest.mark.asyncio
    async def test_auth_disabled_when_no_key(self, monkeypatch) -> None:
        from shared.infrastructure import auth
        from shared.infrastructure.config import Settings

        monkeypatch.setattr(
            auth,
            "settings",
            Settings(_env_file=None, api_key="", database_url="sqlite://", redis_url="redis://x"),
        )
        await auth.verify_api_key(None)

    @pytest.mark.asyncio
    async def test_auth_rejects_missing_key(self, monkeypatch) -> None:
        from shared.infrastructure import auth
        from shared.infrastructure.config import Settings

        monkeypatch.setattr(
            auth,
            "settings",
            Settings(
                _env_file=None, api_key="secret", database_url="sqlite://", redis_url="redis://x"
            ),
        )
        with pytest.raises(HTTPException) as exc:
            await auth.verify_api_key(None)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_accepts_valid_key(self, monkeypatch) -> None:
        from shared.infrastructure import auth
        from shared.infrastructure.config import Settings

        monkeypatch.setattr(
            auth,
            "settings",
            Settings(
                _env_file=None, api_key="secret", database_url="sqlite://", redis_url="redis://x"
            ),
        )
        await auth.verify_api_key("secret")
