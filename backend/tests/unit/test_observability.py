"""Unit tests for observability: structlog JSON logging, PII phone scrubbing, and Langfuse tracing.

ARCHITECTURE.md §11 & PRD §7:
- Verify phone numbers NEVER appear in logs (scrubbed to [REDACTED_PHONE]).
- Verify structured JSON logs contain request_id, agent, duration_ms.
- Verify Langfuse tracing is a silent no-op when keys are absent.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
import structlog

from app.config import Settings
from app.observability.logging import (
    configure_logging,
    get_logger,
    phone_scrubber_processor,
    scrub_sensitive_data,
)
from app.observability.tracer import (
    LangfuseTracer,
    is_langfuse_enabled,
    trace_agent_context,
    trace_llm_context,
)


class TestPhoneScrubbing:
    """Test suite ensuring student and provider phone numbers are never logged."""

    @pytest.mark.parametrize(
        "raw_phone, expected_redacted",
        [
            ("+91 98300 00000", "[REDACTED_PHONE]"),
            ("+919830012345", "[REDACTED_PHONE]"),
            ("9830012345", "[REDACTED_PHONE]"),
            ("+91-98765-43210", "[REDACTED_PHONE]"),
            ("09830012345", "[REDACTED_PHONE]"),
            ("https://wa.me/919830000000?text=Hello", "https://wa.me/[REDACTED_PHONE]?text=Hello"),
        ],
    )
    def test_scrub_various_phone_formats(self, raw_phone: str, expected_redacted: str) -> None:
        result = scrub_sensitive_data(raw_phone)
        assert expected_redacted in result
        assert "98300" not in result

    def test_scrub_nested_structures(self) -> None:
        data = {
            "provider_name": "Annapurna Mess",
            "phone": "+91 98300 11111",
            "metadata": {
                "owner_mobile": "9876543210",
                "nested_list": ["Contact at +91 99999 88888", 12345],
            },
        }
        scrubbed = scrub_sensitive_data(data)
        assert scrubbed["phone"] == "[REDACTED_PHONE]"
        assert scrubbed["metadata"]["owner_mobile"] == "[REDACTED_PHONE]"
        assert "[REDACTED_PHONE]" in scrubbed["metadata"]["nested_list"][0]
        assert "98300" not in str(scrubbed)
        assert "9876543210" not in str(scrubbed)
        assert "99999" not in str(scrubbed)

    def test_phone_scrubber_processor_in_structlog(self) -> None:
        event_dict = {
            "event": "provider_registered",
            "phone": "+91 98300 12345",
            "message": "Assigned phone 9830012345 to cluster",
        }
        processed = phone_scrubber_processor(None, "info", event_dict)
        assert processed["phone"] == "[REDACTED_PHONE]"
        assert "[REDACTED_PHONE]" in processed["message"]
        assert "98300" not in str(processed)


class TestStructuredLogging:
    """Test suite verifying structlog JSON formatting with request_id, agent, and duration."""

    def test_json_logging_with_contextvars(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(json_format=True)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id="req-test-uuid-1234")

        log = get_logger("test_logger")
        log.info(
            "agent_step_completed",
            agent="demand",
            duration_ms=42,
            student_phone="+91 98300 99999",
        )

        captured = capsys.readouterr()
        output = captured.out.strip()
        assert output, "Log output should not be empty"

        parsed = json.loads(output)
        assert parsed.get("event") == "agent_step_completed"
        assert parsed.get("request_id") == "req-test-uuid-1234"
        assert parsed.get("agent") == "demand"
        assert parsed.get("duration_ms") == 42
        # Verify phone is scrubbed in JSON log output
        assert parsed.get("student_phone") == "[REDACTED_PHONE]"
        assert "98300" not in output


class TestLangfuseTracing:
    """Test suite verifying Langfuse tracing behavior and zero-cost no-op default."""

    def test_disabled_by_default(self) -> None:
        settings = Settings(langfuse_public_key="", langfuse_secret_key="")
        assert not is_langfuse_enabled(settings)
        tracer = LangfuseTracer(settings)
        assert not tracer.is_enabled

        # All operations should be silent no-ops without exceptions
        tracer.trace_agent("demand", {"area": "Uluberia"}, {"status": "ok"}, 25)
        tracer.trace_generation("menu-gen", "llama-3", "prompt", "output", 150)
        tracer.flush()

    def test_trace_agent_context_when_disabled(self) -> None:
        settings = Settings(langfuse_public_key="", langfuse_secret_key="")
        tracer = LangfuseTracer(settings)

        with trace_agent_context("match", {"req": 1}, tracer=tracer) as ctx:
            ctx.set_output({"matches": 5})

        assert ctx.agent_name == "match"
        assert ctx.duration_ms >= 0
        assert ctx.output_data == {"matches": 5}

    def test_trace_llm_context_when_disabled(self) -> None:
        settings = Settings(langfuse_public_key="", langfuse_secret_key="")
        tracer = LangfuseTracer(settings)

        with trace_llm_context("test-model", "test prompt", tracer=tracer) as ctx:
            ctx.set_output({"result": "valid"})

        assert ctx.model == "test-model"
        assert ctx.output == {"result": "valid"}

    def test_enabled_mock_client_recording(self) -> None:
        settings = Settings(
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key="sk-lf-test",
            langfuse_host="http://localhost:1234",
        )
        assert is_langfuse_enabled(settings)

        tracer = LangfuseTracer(settings)
        assert tracer.is_enabled

        mock_client = MagicMock()
        mock_span = MagicMock()
        mock_client.start_observation.return_value = mock_span
        tracer._client = mock_client

        tracer.trace_agent(
            agent_name="menu",
            input_data={"provider": "p1"},
            output_data={"days": 7},
            duration_ms=250,
            error=None,
        )

        mock_client.start_observation.assert_called_once()
        mock_span.update.assert_called_once()
        mock_span.end.assert_called_once()
