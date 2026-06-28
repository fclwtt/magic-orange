"""System prompt builder — compose prompt parts with model-specific enforcement."""

from __future__ import annotations
from typing import Any

# ── Enforcement guidance ─────────────────────────────────────────
TOOL_USE_ENFORCEMENT = (
    "# Tool-use enforcement\n"
    "You MUST use your tools to take action — do not describe what you would do "
    "or plan to do without actually doing it. When you say you will perform an "
    "action, you MUST immediately make the corresponding tool call in the same "
    "response. Never end your turn with a promise of future action — execute it now.\n"
    "Keep working until the task is actually complete."
)

TOOL_USE_ENFORCEMENT_MODELS = ("gpt", "codex", "gemini", "gemma", "grok", "glm", "qwen", "deepseek")

TASK_COMPLETION = (
    "# Finishing the job\n"
    "When the user asks you to build, run, or verify something, the deliverable is "
    "a working artifact backed by real tool output — not a description of one. "
    "Do not stop after writing a stub, a plan, or a single command. Keep working "
    "until you have actually exercised the code or produced the requested result."
)

_STABLE = "stable"
_CONTEXT = "context"
_VOLATILE = "volatile"


def build_system_prompt(
    model: str,
    *,
    base_prompt: str = "You are MagicOrange, an AI assistant powered by DeepSeek. You have access to tools (search, code, files, MCP, vision, etc). Use them proactively to complete tasks.",
    extra_parts: list[tuple[str, str]] | None = None,
    has_skills: bool = False,
) -> str:
    """Build a system prompt by composing parts in tier order.

    Args:
        model: model name (used for enforcement matching)
        base_prompt: the fixed identity prompt
        extra_parts: list of (tier, text) pairs for vertical agent injection.
                     tiers: "stable" (fixed), "context" (per-turn), "volatile" (last)
        has_skills: whether the agent has skills (triggers skills guidance)

    Returns:
        composed system prompt string
    """
    ml = model.lower()

    # Build tiers
    stable = [base_prompt]
    context: list[str] = []
    volatile: list[str] = []

    if any(p in ml for p in TOOL_USE_ENFORCEMENT_MODELS):
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
        base_prompt=base_prompt or "You are MagicOrange, an AI assistant powered by DeepSeek.",
    )
