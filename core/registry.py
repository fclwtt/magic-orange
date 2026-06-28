"""ToolRegistry — 注册/调度/schema 生成"""

from __future__ import annotations
import json
from typing import Any, Callable
from interfaces.itools import IToolRegistry


class ToolEntry:
    __slots__ = ("name", "schema", "handler", "check_fn")
    def __init__(self, name: str, schema: dict, handler: Callable, check_fn=None):
        self.name = name; self.schema = schema; self.handler = handler; self.check_fn = check_fn


class ToolRegistry(IToolRegistry):
    def __init__(self):
        self._tools: dict[str, ToolEntry] = {}

    def register(self, name: str, schema: dict, handler: Callable, check_fn=None, **kw):
        self._tools[name] = ToolEntry(name, schema, handler, check_fn)

    def get_definitions(self, names: set[str]) -> list[dict]:
        result = []
        for n in sorted(names):
            e = self._tools.get(n)
            if not e: continue
            if e.check_fn:
                try:
                    if not bool(e.check_fn()): continue
                except Exception:
                    continue
            result.append({"type": "function", "function": {**e.schema, "name": e.name}})
        return result

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        e = self._tools.get(name)
        if not e: return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            return e.handler(args)
        except Exception as ex:
            return json.dumps({"error": f"{type(ex).__name__}: {ex}"})

    def get_all_tool_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def get_entry(self, name: str) -> ToolEntry | None:
        return self._tools.get(name)
