"""Per-agent iteration budget — thread-safe consume/refund counter.

Adapted from Hermes Agent's ``agent/iteration_budget.py``.
Holds an :class:`IterationBudget`; the cap comes from
``max_iterations`` in config.yaml.

``execute_code`` (programmatic tool calling) iterations are refunded via
:meth:`refund` so they don't eat into the budget.
"""

from __future__ import annotations

import threading


class IterationBudget:
    """Thread-safe iteration counter for an agent."""

    def __init__(self, max_total: int):
        self.max_total = max_total
        self._used = 0
        self._lock = threading.Lock()

    def consume(self) -> bool:
        """Try to consume one iteration.  Returns True if allowed."""
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True

    def refund(self) -> None:
        """Give back one iteration (e.g. for execute_code turns)."""
        with self._lock:
            if self._used > 0:
                self._used -= 1

    def refund_n(self, n: int) -> None:
        """Give back multiple iterations at once."""
        with self._lock:
            self._used = max(0, self._used - n)

    @property
    def used(self) -> int:
        with self._lock:
            return self._used

    @property
    def remaining(self) -> int:
        with self._lock:
            return max(0, self.max_total - self._used)


__all__ = ["IterationBudget"]
