"""Clarifying questions — ask user for more information."""

from __future__ import annotations
import json
from typing import Any


def clarify(args: dict[str, Any]) -> str:
    """Ask the user a clarifying question.

    In CLI mode, reads from stdin. In gateway mode, returns a structured
    response that the caller can forward to the user.
    """
    question = args.get("question", "")
    choices = args.get("choices", [])
    if not question:
        return json.dumps({"error": "question required"})

    return json.dumps({
        "type": "clarify",
        "question": question,
        "choices": choices,
        "instruction": f"[CLARIFY] {question}",
    })


SCHEMAS = {
    "clarify": {
        "description": "Ask the user a clarifying question to get more information. Use when the user's request is ambiguous.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string", "description": "The question to ask the user"},
            "choices": {"type": "array", "items": {"type": "string"}, "description": "Optional multiple choice options"},
        }, "required": ["question"]},
    },
}
