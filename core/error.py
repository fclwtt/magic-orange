"""Error classification and retry."""

from __future__ import annotations
import random, time, logging
from enum import Enum

logger = logging.getLogger(__name__)


class FailoverReason(Enum):
    RATE_LIMITED = "rate_limited"
    AUTH_ERROR = "auth_error"
    CONTEXT_OVERFLOW = "context_overflow"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    BAD_REQUEST = "bad_request"
    UNKNOWN = "unknown"


def classify_api_error(error: Exception) -> tuple[FailoverReason, str]:
    """Classify an API error into a reason and a readable message."""
    msg = str(error)

    if hasattr(error, "status_code"):
        code = error.status_code
    elif hasattr(error, "code"):
        code = error.code
    else:
        code = 0

    if code == 429 or "rate_limit" in msg.lower() or "rate limit" in msg.lower():
        return FailoverReason.RATE_LIMITED, msg
    if code in (401, 403) or "auth" in msg.lower() or "api_key" in msg.lower():
        return FailoverReason.AUTH_ERROR, msg
    if code == 413 or "context_length" in msg.lower() or "too many tokens" in msg.lower():
        return FailoverReason.CONTEXT_OVERFLOW, msg
    if code in (500, 502, 503) or "server_error" in msg.lower():
        return FailoverReason.SERVER_ERROR, msg
    if "timeout" in msg.lower():
        return FailoverReason.TIMEOUT, msg
    if code in (400, 422):
        return FailoverReason.BAD_REQUEST, msg
    return FailoverReason.UNKNOWN, msg


def jittered_backoff(base: float = 1.0, cap: float = 60.0, attempt: int = 0) -> float:
    """Exponential backoff with jitter."""
    delay = min(cap, base * (2 ** attempt))
    return delay * (0.5 + random.random() * 0.5)


def adaptive_rate_limit_backoff(headers: dict | None = None, default: float = 2.0) -> float:
    """Extract retry-after from headers or use default."""
    if headers:
        retry_after = headers.get("retry-after") or headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass
    return default + random.random()


def should_fallback(reason: FailoverReason) -> bool:
    """Decide if the error warrants a model/provider fallback."""
    return reason in (FailoverReason.RATE_LIMITED, FailoverReason.SERVER_ERROR, FailoverReason.TIMEOUT)
