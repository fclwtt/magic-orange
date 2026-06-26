"""Retry utilities - compatibility layer"""
import random
import logging

logger = logging.getLogger(__name__)

def jittered_backoff(retry_count: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: float = 0.1) -> float:
    """Calculate jittered exponential backoff delay"""
    delay = min(base_delay * (2 ** retry_count), max_delay)
    jitter_amount = delay * jitter * (2 * random.random() - 1)
    return max(0, delay + jitter_amount)
