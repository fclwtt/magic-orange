"""Tool call guardrails — simple rule-based safety checks."""

from __future__ import annotations
from enum import Enum
from typing import Any


class GuardrailDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


class ToolCallGuardrailController:
    """Simple rule-based guardrail controller.

    Checks tool calls against a list of deny rules before dispatching.
    """

    DENY_PATHS = {
        "/etc/shadow", "/etc/passwd", "/etc/sudoers",
        "~/.ssh", "~/.aws", "~/.gnupg",
    }

    DENY_COMMANDS = {"rm -rf /", "mkfs", "dd if=/dev/zero", ":(){ :|:& };:"}

    def __init__(self, strict: bool = True):
        self.strict = strict

    def check(self, tool_name: str, args: dict[str, Any]) -> GuardrailDecision:
        if tool_name in ("read_file", "write_file", "search_files"):
            return self._check_file(args)
        if tool_name == "execute_code":
            return self._check_code(args)
        return GuardrailDecision.ALLOW

    def _check_file(self, args: dict) -> GuardrailDecision:
        path = str(args.get("path", ""))
        for deny in self.DENY_PATHS:
            if deny in path.replace("\\", "/"):
                return GuardrailDecision.DENY
        return GuardrailDecision.ALLOW

    def _check_code(self, args: dict) -> GuardrailDecision:
        code = args.get("code", "")
        for deny in self.DENY_COMMANDS:
            if deny in code:
                return GuardrailDecision.DENY
        return GuardrailDecision.ALLOW


# Convenience instance
default_guardrails = ToolCallGuardrailController()
