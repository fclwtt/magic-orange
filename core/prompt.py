"""System prompt builder — Hermes-style tiered composition with configurable enforcement."""

from __future__ import annotations
from typing import Any

# ── Enforcement guidance ─────────────────────────────────────────
# Hermes-style: injected as stable system instruction, not as dialogue.
# Wording avoids self-referential loops that models like DeepSeek/Gemini echo back.
TOOL_USE_ENFORCEMENT = (
    "## Tool use\n"
    "Call tools immediately when you intend to act. Do not describe what you would do "
    "without actually doing it. Every turn must either make progress via a tool call "
    "or deliver a final result."
)

TASK_COMPLETION = (
    "## Completing tasks\n"
    "Keep working until the task is actually done — do not stop with a plan or summary "
    "of intentions. If a tool, install, or network call fails, report the blocker "
    "honestly and try an alternative. Never fabricate output you could not produce."
)

# Models that benefit from explicit tool-use enforcement
TOOL_USE_ENFORCEMENT_MODELS = ("gpt", "codex", "gemini", "gemma", "grok", "glm", "qwen", "deepseek")

_STABLE = "stable"
_CONTEXT = "context"
_VOLATILE = "volatile"


def build_system_prompt(
    model: str,
    *,
    base_prompt: str = "You are MagicOrange, an AI assistant with access to tools (search, code execution, file operations, web browsing). Use them proactively to complete user tasks.",
    extra_parts: list[tuple[str, str]] | None = None,
    has_skills: bool = False,
    tool_use_enforcement: bool | str = "auto",
) -> str:
    """Build a system prompt by composing parts in tier order.

    Args:
        model: model name (used for enforcement matching)
        base_prompt: the fixed identity prompt
        extra_parts: list of (tier, text) pairs for vertical agent injection.
        tool_use_enforcement: "auto" (match model list), True (always), False (never)
    """
    ml = model.lower()

    stable = [base_prompt]
    context: list[str] = []
    volatile: list[str] = []

    # Tool-use enforcement (configurable, Hermes-style)
    inject_tool_enforcement = False
    if tool_use_enforcement is True or str(tool_use_enforcement).lower() in ("true", "always", "yes", "on"):
        inject_tool_enforcement = True
    elif tool_use_enforcement is False or str(tool_use_enforcement).lower() in ("false", "never", "no", "off"):
        inject_tool_enforcement = False
    else:
        # "auto": match against known model families
        inject_tool_enforcement = any(p in ml for p in TOOL_USE_ENFORCEMENT_MODELS)

    if inject_tool_enforcement:
        stable.append(TOOL_USE_ENFORCEMENT)
        stable.append(TASK_COMPLETION)

    # Extra parts from vertical agents
    if extra_parts:
        for tier, text in extra_parts:
            if tier == "stable":
                stable.append(text)
            elif tier == "context":
                context.append(text)
            elif tier == "volatile":
                volatile.append(text)

    parts = []
    if stable:
        parts.append("\n\n".join(stable))
    if context:
        parts.append("\n\n".join(context))
    if volatile:
        parts.append("\n\n".join(volatile))

    return "\n\n".join(parts)


def compose_prompt_from_model(model: str, base_prompt: str | None = None) -> str:
    """Convenience: build a minimal prompt with just enforcement."""
    return build_system_prompt(
        model,
        base_prompt=base_prompt or "You are MagicOrange, an AI assistant with access to tools.",
    )
