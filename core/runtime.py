"""AgentRuntime — 对话循环，整合 prompt/guardrails/sanitize"""

from __future__ import annotations
import json, logging
from typing import Any
from interfaces.iagent import IAgentRuntime
from interfaces.itools import IToolRegistry
from interfaces.iprovider import ILLMProvider
from interfaces.iconfig import IConfigStore
from core.prompt import build_system_prompt

logger = logging.getLogger(__name__)

class AgentRuntime(IAgentRuntime):
    def __init__(self, provider: ILLMProvider, tools: IToolRegistry, config: IConfigStore,
                 guardrails=None):
        self._provider = provider
        self._tools = tools
        self._config = config
        self._guardrails = guardrails
        self._messages: list[dict] = []

    def run_conversation(self, query: str) -> dict[str, Any]:
        if not self._messages:
            prompt = build_system_prompt(self._provider.model)
            self._messages = [{"role": "system", "content": prompt}]
        self._messages.append({"role": "user", "content": query})

        tool_defs = self._tools.get_definitions(set(self._tools.get_all_tool_names()))
        api_calls = 0

        for _ in range(int(self._config.get("max_turns", "30"))):
            resp = self._provider.chat_completion(self._messages, tools=tool_defs or None)
            api_calls += 1

            msg = {"role": "assistant", "content": resp.get("content", "")}
            if resp.get("tool_calls"):
                msg["tool_calls"] = resp["tool_calls"]
            self._messages.append(msg)

            if not resp.get("tool_calls"):
                return {"completed": True, "final_response": resp.get("content", ""), "api_calls": api_calls}

            for tc in resp["tool_calls"]:
                fn = tc["function"]
                try:
                    args = json.loads(fn["arguments"]) if fn.get("arguments") else {}
                except json.JSONDecodeError:
                    args = {}

                # Optionally check guardrails
                if self._guardrails:
                    from core.guardrails import GuardrailDecision
                    decision = self._guardrails.check(fn["name"], args)
                    if decision == GuardrailDecision.DENY:
                        logger.warning("Guardrail denied: %s", fn["name"])
                        self._messages.append({
                            "role": "tool", "tool_call_id": tc["id"],
                            "content": json.dumps({"error": f"Guardrail denied: {fn['name']} call blocked"})
                        })
                        continue

                logger.info("Tool call: %s", fn["name"])
                result = self._tools.dispatch(fn["name"], args)
                self._messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

        return {"completed": False, "final_response": "Max turns reached.", "api_calls": api_calls}

    def reset(self) -> None: self._messages = []
