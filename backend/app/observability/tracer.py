"""Langfuse observability integration with zero-cost no-op default.

ARCHITECTURE.md §11:
- Decorators and tracers around each agent and every LLM call.
- Completely silent no-op when LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY are absent.
- When enabled, records agent observations and LLM generations with latency and model metadata.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def is_langfuse_enabled(settings: Settings | None = None) -> bool:
    """Return True only if both public and secret keys are non-empty."""
    cfg = settings or get_settings()
    pk = (cfg.langfuse_public_key or os.getenv("LANGFUSE_PUBLIC_KEY", "")).strip()
    sk = (cfg.langfuse_secret_key or os.getenv("LANGFUSE_SECRET_KEY", "")).strip()
    return bool(pk and sk)


class AgentTraceContext:
    """Helper context object to set output, metadata, or error during agent execution."""

    def __init__(self, agent_name: str, input_data: Any = None) -> None:
        self.agent_name = agent_name
        self.input_data = input_data
        self.output_data: Any = None
        self.error: str | None = None
        self.duration_ms: int = 0
        self.metadata: dict[str, Any] = {}

    def set_output(self, output: Any) -> None:
        self.output_data = output

    def set_error(self, error: str | Exception) -> None:
        self.error = str(error)


class LLMTraceContext:
    """Helper context object to set prompt, model, and generation output."""

    def __init__(self, model: str, prompt: str) -> None:
        self.model = model
        self.prompt = prompt
        self.output: Any = None
        self.error: str | None = None
        self.duration_ms: int = 0
        self.metadata: dict[str, Any] = {}

    def set_output(self, output: Any) -> None:
        self.output = output

    def set_error(self, error: str | Exception) -> None:
        self.error = str(error)


class LangfuseTracer:
    """Manager for Langfuse traces. Defaults to a clean no-op when unconfigured."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: Any = None
        self._enabled = is_langfuse_enabled(self._settings)

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _get_client(self) -> Any:
        if not self._enabled:
            return None
        if self._client is None:
            try:
                from langfuse import Langfuse

                pk = self._settings.langfuse_public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
                sk = self._settings.langfuse_secret_key or os.getenv("LANGFUSE_SECRET_KEY")
                host = (
                    self._settings.langfuse_host
                    or os.getenv("LANGFUSE_HOST")
                    or "https://cloud.langfuse.com"
                )
                self._client = Langfuse(
                    public_key=pk,
                    secret_key=sk,
                    host=host,
                )
            except Exception as exc:
                logger.warning("Failed to initialize Langfuse client: %s", exc)
                self._enabled = False
                return None
        return self._client

    def trace_agent(
        self,
        agent_name: str,
        input_data: Any,
        output_data: Any,
        duration_ms: int,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an agent execution span when Langfuse is enabled."""
        client = self._get_client()
        if client is None:
            return

        try:
            span = client.start_observation(
                name=f"agent-{agent_name}",
                as_type="agent",
                input=input_data,
                metadata=metadata or {},
            )
            span.update(
                output=output_data,
                level="ERROR" if error else "DEFAULT",
                status_message=error,
            )
            span.end()
        except Exception as exc:
            logger.debug("Langfuse trace_agent suppressed error: %s", exc)

    def trace_generation(
        self,
        name: str,
        model: str,
        prompt: str,
        output: Any,
        duration_ms: int,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an LLM generation observation when Langfuse is enabled."""
        client = self._get_client()
        if client is None:
            return

        try:
            gen = client.start_observation(
                name=name,
                as_type="generation",
                input=prompt,
                model=model,
                metadata=metadata or {},
            )
            gen.update(
                output=output,
                level="ERROR" if error else "DEFAULT",
                status_message=error,
            )
            gen.end()
        except Exception as exc:
            logger.debug("Langfuse trace_generation suppressed error: %s", exc)

    def flush(self) -> None:
        """Flush pending trace events."""
        if self._client is not None:
            try:
                self._client.flush()
            except Exception as exc:
                logger.debug("Langfuse flush warning: %s", exc)


# Singleton tracer instance
_global_tracer: LangfuseTracer | None = None


def get_tracer(settings: Settings | None = None) -> LangfuseTracer:
    """Return global or configured LangfuseTracer instance."""
    global _global_tracer
    if settings is not None:
        return LangfuseTracer(settings)
    if _global_tracer is None:
        _global_tracer = LangfuseTracer()
    return _global_tracer


@contextmanager
def trace_agent_context(
    agent_name: str, input_data: Any = None, tracer: LangfuseTracer | None = None
) -> Generator[AgentTraceContext, None, None]:
    """Context manager for tracing an agent execution with timing."""
    t = tracer or get_tracer()
    ctx = AgentTraceContext(agent_name=agent_name, input_data=input_data)
    start_time = time.time()
    try:
        yield ctx
    except Exception as exc:
        ctx.set_error(exc)
        raise
    finally:
        ctx.duration_ms = max(0, int((time.time() - start_time) * 1000))
        if t.is_enabled:
            t.trace_agent(
                agent_name=ctx.agent_name,
                input_data=ctx.input_data,
                output_data=ctx.output_data,
                duration_ms=ctx.duration_ms,
                error=ctx.error,
                metadata=ctx.metadata,
            )


@contextmanager
def trace_llm_context(
    model: str, prompt: str, tracer: LangfuseTracer | None = None
) -> Generator[LLMTraceContext, None, None]:
    """Context manager for tracing an LLM generation call with timing."""
    t = tracer or get_tracer()
    ctx = LLMTraceContext(model=model, prompt=prompt)
    start_time = time.time()
    try:
        yield ctx
    except Exception as exc:
        ctx.set_error(exc)
        raise
    finally:
        ctx.duration_ms = max(0, int((time.time() - start_time) * 1000))
        if t.is_enabled:
            t.trace_generation(
                name="llm-generate-structured",
                model=ctx.model,
                prompt=ctx.prompt,
                output=ctx.output,
                duration_ms=ctx.duration_ms,
                error=ctx.error,
                metadata=ctx.metadata,
            )
