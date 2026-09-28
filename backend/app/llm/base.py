"""LLM Provider layer for Tiffin Optimizer.

Protocol definition, custom exceptions, and provider implementations:
- LLMProvider: Protocol for structured LLM generation
- LLMUnavailable: Exception raised when LLM is offline, disabled, or fails
- NoneProvider: Null-object provider that always raises LLMUnavailable
- FakeProvider: Test double configurable for valid, invalid, timeout, and failure states
- GroqProvider: Hosted inference via Groq OpenAI-compatible chat API
- get_llm_provider: Factory returning the provider configured in Settings
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Literal, Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


class LLMUnavailable(Exception):
    """Raised when an LLM provider is disabled, unreachable, or exhausted retries."""


class LLMProvider(Protocol):
    """Protocol for structured output generation across LLM providers."""

    async def generate_structured(
        self, prompt: str, schema: type[T], *, timeout: float = 20.0
    ) -> T:
        """Generate structured data conforming to the given Pydantic schema."""
        ...


class NoneProvider:
    """Null provider used when LLM_PROVIDER=none or when LLM is explicitly disabled."""

    async def generate_structured(
        self, prompt: str, schema: type[T], *, timeout: float = 20.0
    ) -> T:
        """Always raise LLMUnavailable."""
        raise LLMUnavailable("LLM provider is disabled ('none').")


class FakeProvider:
    """Configurable test provider for unit, integration, and contract tests.

    Supports:
    - Returning canned schema instances or dicts
    - Simulating invalid json / schema validation failure
    - Simulating timeout
    - Simulating provider outage (LLMUnavailable)
    - Simulating transient failures with eventual success
    """

    def __init__(
        self,
        canned_response: BaseModel | dict[str, Any] | None = None,
        canned_responses: dict[type[Any], Any] | None = None,
        mode: Literal["valid", "invalid", "timeout", "unavailable"] = "valid",
        delay_seconds: float = 0.0,
        failures_before_success: int = 0,
    ) -> None:
        self.canned_response = canned_response
        self.canned_responses = canned_responses or {}
        self.mode = mode
        self.delay_seconds = delay_seconds
        self.failures_before_success = failures_before_success
        self.call_count = 0
        self.call_prompts: list[str] = []

    async def generate_structured(
        self, prompt: str, schema: type[T], *, timeout: float = 20.0
    ) -> T:
        """Generate fake structured output according to configured mode."""
        self.call_count += 1
        self.call_prompts.append(prompt)

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        # Handle transient failures before succeeding
        if self.call_count <= self.failures_before_success:
            raise LLMUnavailable(
                f"Simulated failure ({self.call_count}/{self.failures_before_success})"
            )

        if self.mode == "timeout":
            raise TimeoutError("Simulated LLM call timeout")

        if self.mode == "unavailable":
            raise LLMUnavailable("Simulated LLM service unavailable")

        if self.mode == "invalid":
            # Return data that intentionally violates schema validation
            try:
                return schema.model_validate({"_invalid_sentinel_key_": 999999})
            except ValidationError as exc:
                raise LLMUnavailable(f"Simulated schema validation failure: {exc}") from exc

        # Mode == "valid"
        target_resp = self.canned_responses.get(schema, self.canned_response)
        if target_resp is None:
            raise LLMUnavailable("FakeProvider configured with no canned_response")

        if isinstance(target_resp, schema):
            return target_resp

        if isinstance(target_resp, dict):
            return schema.model_validate(target_resp)

        raise LLMUnavailable(
            f"Canned response type {type(target_resp)} not compatible with {schema}"
        )


class GroqProvider:
    """Hosted LLM provider using Groq's OpenAI-compatible completions API."""

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.base_url = base_url or self.GROQ_API_URL

    async def generate_structured(
        self, prompt: str, schema: type[T], *, timeout: float = 20.0
    ) -> T:
        """Call Groq API with JSON schema enforcement and validate the response."""
        if not self.api_key:
            raise LLMUnavailable("Groq API key is missing or empty")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        json_schema = schema.model_json_schema()
        system_instructions = (
            "You are a structured data generator. "
            "You MUST respond ONLY with a single valid JSON object that conforms strictly "
            f"to the following JSON Schema:\n{json.dumps(json_schema)}\n"
            "Do NOT include markdown formatting (like ```json), explanations, or surrounding text."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)

            if response.status_code != 200:
                raise LLMUnavailable(
                    f"Groq API returned HTTP {response.status_code}: {response.text[:200]}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return schema.model_validate_json(content)

        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Groq request timed out after {timeout}s") from exc
        except (
            httpx.HTTPError,
            json.JSONDecodeError,
            ValidationError,
            KeyError,
            IndexError,
        ) as exc:
            raise LLMUnavailable(f"Groq generation failed: {exc}") from exc


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    """Return configured LLMProvider based on application settings."""
    cfg = settings or get_settings()
    provider_name = (cfg.llm_provider or "none").strip().lower()

    if provider_name == "groq":
        return GroqProvider(api_key=cfg.groq_api_key, model=cfg.llm_model or None)
    if provider_name in ("none", ""):
        return NoneProvider()

    # Default fallback for unknown or unimplemented provider types
    return NoneProvider()
