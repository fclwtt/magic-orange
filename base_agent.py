"""base-agent — 底座入口"""

from core import AgentRuntime, OpenAIProvider, ToolRegistry, ConfigStore
from core.guardrails import ToolCallGuardrailController
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
    return AgentRuntime(
        provider=provider, tools=tools, config=store,
        guardrails=ToolCallGuardrailController(strict=True),
    )

__all__ = ["create_agent", "AgentRuntime", "ToolRegistry", "ConfigStore", "OpenAIProvider"]
