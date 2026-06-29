"""base-agent — 底座入口"""

from core import AgentRuntime, OpenAIProvider, ToolRegistry, ConfigStore, IterationBudget
from core.guardrails import ToolCallGuardrailController, ToolCallGuardrailConfig
from tools import web, file, code, todo, mcp, vision, clarify


def _register_all(tools: ToolRegistry):
    for mod in (web, file, code, todo, mcp, vision, clarify):
        for name, schema in getattr(mod, "SCHEMAS", {}).items():
            handler = getattr(mod, name, None)
            if handler:
                tools.register(name, schema, handler)


def create_agent(config: dict | None = None) -> AgentRuntime:
    store = ConfigStore(config or {})

    provider = OpenAIProvider(store)
    tools = ToolRegistry()
    _register_all(tools)

    # Build guardrail config from tool_loop_guardrails section
    guardrail_cfg = ToolCallGuardrailConfig.from_mapping(
        store.get("tool_loop_guardrails")
    )
    guardrails = ToolCallGuardrailController(guardrail_cfg)

    # Build iteration budget
    max_iterations = int(store.get("max_iterations", 60))
    budget = IterationBudget(max_iterations)

    return AgentRuntime(
        provider=provider,
        tools=tools,
        config=store,
        guardrails=guardrails,
        budget=budget,
    )


__all__ = ["create_agent", "AgentRuntime", "ToolRegistry", "ConfigStore", "OpenAIProvider"]
