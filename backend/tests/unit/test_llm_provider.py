"""Unit tests for the LLM provider layer (offline, no external network)."""

import httpx
import pytest
from pydantic import BaseModel

from app.config import Settings
from app.llm.base import (
    FakeProvider,
    GroqProvider,
    LLMUnavailable,
    NoneProvider,
    get_llm_provider,
)


class DummySchema(BaseModel):
    message: str
    count: int


@pytest.mark.asyncio
async def test_none_provider_always_raises():
    provider = NoneProvider()
    with pytest.raises(LLMUnavailable, match="disabled"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_fake_provider_valid():
    expected = DummySchema(message="hello", count=42)
    provider = FakeProvider(canned_response=expected, mode="valid")

    result = await provider.generate_structured("test prompt", DummySchema)
    assert result == expected
    assert provider.call_count == 1
    assert provider.call_prompts == ["test prompt"]


@pytest.mark.asyncio
async def test_fake_provider_valid_from_dict():
    provider = FakeProvider(canned_response={"message": "from dict", "count": 10}, mode="valid")
    result = await provider.generate_structured("test prompt", DummySchema)
    assert result.message == "from dict"
    assert result.count == 10


@pytest.mark.asyncio
async def test_fake_provider_invalid_mode():
    provider = FakeProvider(mode="invalid")
    with pytest.raises(LLMUnavailable, match="Simulated schema validation failure"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_fake_provider_timeout_mode():
    provider = FakeProvider(mode="timeout")
    with pytest.raises(TimeoutError, match="timeout"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_fake_provider_unavailable_mode():
    provider = FakeProvider(mode="unavailable")
    with pytest.raises(LLMUnavailable, match="unavailable"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_fake_provider_transient_failure_then_success():
    expected = DummySchema(message="recovered", count=1)
    provider = FakeProvider(
        canned_response=expected,
        mode="valid",
        failures_before_success=2,
    )

    with pytest.raises(LLMUnavailable):
        await provider.generate_structured("call 1", DummySchema)

    with pytest.raises(LLMUnavailable):
        await provider.generate_structured("call 2", DummySchema)

    # 3rd call succeeds
    result = await provider.generate_structured("call 3", DummySchema)
    assert result == expected
    assert provider.call_count == 3


@pytest.mark.asyncio
async def test_groq_provider_missing_key():
    provider = GroqProvider(api_key="")
    with pytest.raises(LLMUnavailable, match="API key is missing"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_groq_provider_mock_success(monkeypatch):
    provider = GroqProvider(api_key="gsk_test_fake_key")

    mock_response_json = {
        "choices": [{"message": {"content": '{"message": "groq success", "count": 100}'}}]
    }

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_response_json

    async def mock_post(self, url, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    result = await provider.generate_structured("prompt", DummySchema)
    assert result.message == "groq success"
    assert result.count == 100


@pytest.mark.asyncio
async def test_groq_provider_mock_http_error(monkeypatch):
    provider = GroqProvider(api_key="gsk_test_fake_key")

    class MockErrorResponse:
        status_code = 500
        text = "Internal Server Error"

    async def mock_post(self, url, **kwargs):
        return MockErrorResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(LLMUnavailable, match="HTTP 500"):
        await provider.generate_structured("prompt", DummySchema)


@pytest.mark.asyncio
async def test_groq_provider_mock_timeout(monkeypatch):
    provider = GroqProvider(api_key="gsk_test_fake_key")

    async def mock_post(self, url, **kwargs):
        raise httpx.TimeoutException("Connection timed out")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(TimeoutError, match="timed out"):
        await provider.generate_structured("prompt", DummySchema)


def test_get_llm_provider_factory():
    # None / empty
    p1 = get_llm_provider(Settings(llm_provider="none"))
    assert isinstance(p1, NoneProvider)

    p2 = get_llm_provider(Settings(llm_provider=""))
    assert isinstance(p2, NoneProvider)

    # Groq
    p3 = get_llm_provider(Settings(llm_provider="groq", groq_api_key="test_key"))
    assert isinstance(p3, GroqProvider)
    assert p3.api_key == "test_key"
