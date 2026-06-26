"""Tool result storage - compatibility layer"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

def maybe_persist_tool_result(tool_call_id: str, result: Any, **kwargs) -> None:
    logger.debug(f"maybe_persist_tool_result: {tool_call_id}")

def enforce_turn_budget(messages: list, max_turns: int = 50) -> list:
    return messages
