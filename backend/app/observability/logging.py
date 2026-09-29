"""Structured JSON logging configuration with request-id tracking and PII phone scrubbing.

ARCHITECTURE.md §11 & PRD §7:
- Standardized structlog JSON output.
- Request-ID injection via contextvars.
- Strict PII scrubbing: Provider and student phone numbers are NEVER logged.
"""

from __future__ import annotations

import logging
import re
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import structlog

# Regular expressions for phone numbers (Indian mobile formats and standard 10-12 digit numbers)
PHONE_REGEX = re.compile(
    r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}|\b(?:\+?\d{1,3}[-.\s]?)?\d{10,12}\b"
)
WHATSAPP_URL_REGEX = re.compile(r"(https?://wa\.me/)(?:\+?91)?[0-9]+")

SENSITIVE_KEYS = {
    "phone",
    "phone_number",
    "contact_number",
    "mobile",
    "mobile_number",
    "whatsapp",
    "whatsapp_url",
}


def scrub_string(value: str) -> str:
    """Redact phone numbers and WhatsApp URLs from string text."""
    if not isinstance(value, str):
        return value
    # Scrub WhatsApp link target digits first
    value = WHATSAPP_URL_REGEX.sub(r"\1[REDACTED_PHONE]", value)
    # Scrub raw phone numbers
    return PHONE_REGEX.sub("[REDACTED_PHONE]", value)


def scrub_sensitive_data(obj: Any) -> Any:
    """Recursively scrub phone numbers from dictionaries, lists, and strings."""
    if isinstance(obj, str):
        return scrub_string(obj)
    if isinstance(obj, dict):
        scrubbed_dict: dict[str, Any] = {}
        for key, val in obj.items():
            key_lower = str(key).lower()
            if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
                scrubbed_dict[key] = "[REDACTED_PHONE]"
            else:
                scrubbed_dict[key] = scrub_sensitive_data(val)
        return scrubbed_dict
    if isinstance(obj, list):
        return [scrub_sensitive_data(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(scrub_sensitive_data(item) for item in obj)
    return obj


def phone_scrubber_processor(
    _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Structlog processor to ensure phone numbers never appear in log events."""
    scrubbed = scrub_sensitive_data(dict(event_dict))
    if isinstance(scrubbed, dict):
        event_dict.clear()
        event_dict.update(scrubbed)
    return event_dict


def configure_logging(json_format: bool = True) -> None:
    """Configure structlog and intercept standard library logging."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        phone_scrubber_processor,
    ]

    renderer: structlog.types.Processor
    if json_format:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Avoid duplicate handlers on re-configuration
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
