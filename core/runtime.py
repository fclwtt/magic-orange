"""AgentRuntime — dialogue loop with Hermes-style budget + guardrails."""

from __future__ import annotations
import json, logging
from typing import Any
from interfaces.iagent import IAgentRuntime
from interfaces.itools import IToolRegistry
from interfaces.iprovider import ILLMProvider
from interfaces.iconfig import IConfigStore
from core.budget import IterationBudget
from core.guardrails import (
    ToolCallGuardrailController, ToolGuardrailDecision,
    toolguard_synthetic_result, append_toolguard_guidance,
)
from core.prompt import build_system_prompt

logger = logging.getLogger(__name__)


class AgentRuntime(IAgentRuntime):
    def __init__(
        self,
        provider: ILLMProvider,
        tools: IToolRegistry,
        config: IConfigStore,
        guardrails: ToolCallGuardrailController | None = None,
        budget: IterationBudget | None = None,
    ):
        self._provider = provider
        self._tools = tools
        self._config = config
        self._guardrails = guardrails or ToolCallGuardrailController()
        self._budget = budget or IterationBudget(60)
        self._messages: list[dict] = []
        self._grace_call_used = False
        self._budget_grace_call = False  # one extra call after budget exhausted

    def _build_prompt(self) -> str:
        """Build system prompt with configurable tool-use enforcement."""
        enforcement = self._config.get("tool_use_enforcement", "auto")
        return build_system_prompt(
            self._provider.model,
            tool_use_enforcement=enforcement,
        )

    # ── Synchronous conversation (CLI mode) ─────────────────
    def run_conversation(self, query: str) -> dict[str, Any]:
        if not self._messages:
            prompt = self._build_prompt()
            self._messages = [{"role": "system", "content": prompt}]
        self._messages.append({"role": "user", "content": query})

        tool_defs = self._tools.get_definitions(set(self._tools.get_all_tool_names()))
        api_calls = 0

        while (self._budget.remaining > 0) or self._budget_grace_call:
            if self._budget_grace_call:
                self._budget_grace_call = False
            elif not self._budget.consume():
                # Budget exhausted → request summary without tools
                return self._handle_max_iterations()

            resp = self._provider.chat_completion(self._messages, tools=tool_defs or None)
            api_calls += 1

            msg = {"role": "assistant", "content": resp.get("content", "")}
            if resp.get("tool_calls"):
                msg["tool_calls"] = resp["tool_calls"]
            self._messages.append(msg)

            if not resp.get("tool_calls"):
                return {"completed": True, "final_response": resp.get("content", ""), "api_calls": api_calls}

            # Process tool calls with guardrail hooks
            should_break = False
            for tc in resp["tool_calls"]:
                fn = tc["function"]
                try:
                    args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
                except json.JSONDecodeError:
                    args = {}

                tool_name = fn["name"]

                # ── before_call guardrail ──
                guard_decision = self._guardrails.before_call(tool_name, args)
                if not guard_decision.allows_execution:
                    logger.warning("Guardrail blocked: %s — %s", tool_name, guard_decision.message)
                    result = toolguard_synthetic_result(guard_decision)
                    failed = True
                else:
                    try:
                        result = self._tools.dispatch(tool_name, args)
                        failed = self._detect_failure(result)
                    except Exception as e:
                        result = json.dumps({"error": str(e)})
                        failed = True

                    # Refund execute_code turns (pure computation, not tool abuse)
                    if tool_name == "execute_code":
                        self._budget.refund()

                self._messages.append({
                    "role": "tool", "tool_call_id": tc["id"], "content": result,
                })

                # ── after_call guardrail ──
                decision = self._guardrails.after_call(
                    tool_name, args, result, failed=failed,
                )
                if decision.action in {"warn", "halt"}:
                    # Append guidance to the tool result for the model to see
                    self._messages[-1]["content"] = append_toolguard_guidance(result, decision)
                    logger.warning("Guardrail %s: %s (count=%d)", decision.action, tool_name, decision.count)

                if decision.should_halt:
                    should_break = True
                    break

            if should_break:
                return {
                    "completed": False,
                    "final_response": "Tool loop halted by guardrail.",
                    "api_calls": api_calls,
                }

        return {"completed": False, "final_response": "Iteration budget exhausted.", "api_calls": api_calls}

    # ── Streaming conversation (WebSocket mode) ─────────────
    def run_conversation_stream(self, query: str):
        """Streaming generator — Hermes-style events with guardrail integration."""
        try:
            if not self._messages:
                prompt = self._build_prompt()
                self._messages = [{"role": "system", "content": prompt}]
            self._messages.append({"role": "user", "content": query})

            tool_defs = self._tools.get_definitions(set(self._tools.get_all_tool_names()))
            api_calls = 0
            content_parts: list[str] = []

            while (self._budget.remaining > 0) or self._budget_grace_call:
                if self._budget_grace_call:
                    self._budget_grace_call = False
                    # Grace call: strip tools, ask model to summarize
                    yield {"type": "guardrail.event", "action": "grace_call", "message": "Budget exhausted — requesting summary"}
                    for event in self._provider.chat_completion_stream(
                        self._messages, tools=None,
                    ):
                        if event["type"] == "delta":
                            content_parts.append(event["text"])
                            yield {"type": "message.delta", "text": event["text"]}
                        elif event["type"] == "done":
                            api_calls += 1

                    final_text = "".join(content_parts)
                    yield {"type": "message.complete", "text": final_text, "api_calls": api_calls}
                    return

                elif not self._budget.consume():
                    # Budget exhausted — trigger grace call next iteration
                    self._budget_grace_call = True
                    continue

                # Stream the API response
                tool_calls_pending: list[dict] = []
                stream_content: list[str] = []

                for event in self._provider.chat_completion_stream(
                    self._messages, tools=tool_defs or None,
                ):
                    if event["type"] == "delta":
                        stream_content.append(event["text"])
                        yield {"type": "message.delta", "text": event["text"]}

                    elif event["type"] == "tool.start":
                        yield {"type": "tool.start", "tool_name": event["tool_name"]}

                    elif event["type"] == "tool.complete":
                        tool_calls_pending.append(event)

                    elif event["type"] == "done":
                        content_parts.append(event["content"])
                        api_calls += 1

                # Build assistant message
                assistant_content = "".join(stream_content)
                assistant_msg = {"role": "assistant", "content": assistant_content}

                if tool_calls_pending:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc["tool_call_id"] or f"call_{api_calls}_{i}",
                            "type": "function",
                            "function": {
                                "name": tc["tool_name"],
                                "arguments": tc["arguments"],
                            },
                        }
                        for i, tc in enumerate(tool_calls_pending)
                    ]
                self._messages.append(assistant_msg)

                # No tool calls → done
                if not tool_calls_pending:
                    final_text = "".join(content_parts)
                    yield {"type": "message.complete", "text": final_text, "api_calls": api_calls}
                    return

                # Execute tool calls with guardrails
                should_break = False
                for tc in tool_calls_pending:
                    tool_name = tc["tool_name"]
                    try:
                        args = json.loads(tc["arguments"]) if tc.get("arguments") else {}
                    except json.JSONDecodeError:
                        args = {}

                    # ── before_call ──
                    guard_decision = self._guardrails.before_call(tool_name, args)
                    if not guard_decision.allows_execution:
                        result = toolguard_synthetic_result(guard_decision)
                        failed = True
                        yield {"type": "guardrail.event", "action": "block", "tool_name": tool_name, "message": guard_decision.message}
                    else:
                        try:
                            result = self._tools.dispatch(tool_name, args)
                            failed = self._detect_failure(result)
                        except Exception as e:
                            result = json.dumps({"error": str(e)})
                            failed = True

                        if tool_name == "execute_code":
                            self._budget.refund()

                    tc_id = tc.get("tool_call_id", f"call_{api_calls}_{0}")
                    self._messages.append({
                        "role": "tool", "tool_call_id": tc_id, "content": result,
                    })
                    yield {
                        "type": "tool.complete",
                        "tool_name": tool_name,
                        "result": result[:500] if result else "(empty)",
                    }

                    # ── after_call ──
                    decision = self._guardrails.after_call(
                        tool_name, args, result, failed=failed,
                    )
                    if decision.action in {"warn", "halt"}:
                        self._messages[-1]["content"] = append_toolguard_guidance(result, decision)
                        yield {
                            "type": "guardrail.event",
                            "action": decision.action,
                            "tool_name": tool_name,
                            "message": decision.message,
                            "count": decision.count,
                        }

                    if decision.should_halt:
                        should_break = True
                        break

                if should_break:
                    final_text = "".join(content_parts)
                    yield {
                        "type": "message.complete",
                        "text": final_text or "Tool loop halted by guardrail.",
                        "api_calls": api_calls,
                    }
                    return

            # Exhausted without grace call
            yield {
                "type": "message.complete",
                "text": "".join(content_parts) or "Iteration budget exhausted.",
                "api_calls": api_calls,
            }

        except Exception as e:
            logger.error("Stream error: %s", e, exc_info=True)
            yield {"type": "error", "message": str(e)}

    # ── Helpers ────────────────────────────────────────────
    def _detect_failure(self, result: str | None) -> bool:
        """Quick failure detection from tool result string."""
        if result is None:
            return False
        lower = result[:300].lower()
        if '"error"' in lower:
            return True
        if result.startswith("Error"):
            return True
        return False

    def _handle_max_iterations(self) -> dict[str, Any]:
        """When budget exhausted, strip tools and ask model to summarize."""
        self._budget_grace_call = True
        summary_request = (
            "You've reached the maximum number of tool-calling iterations. "
            "Please provide a final response summarizing what you've found "
            "and accomplished so far, without calling any more tools."
        )
        self._messages.append({"role": "user", "content": summary_request})
        resp = self._provider.chat_completion(self._messages, tools=None)
        self._messages.append({
            "role": "assistant",
            "content": resp.get("content", ""),
        })
        return {
            "completed": True,
            "final_response": resp.get("content", "Iteration budget exhausted."),
            "api_calls": 0,
            "budget_exhausted": True,
        }

    def reset(self) -> None:
        self._messages = []
        self._guardrails.reset_for_turn()
        self._grace_call_used = False
        self._budget_grace_call = False
