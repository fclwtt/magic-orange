"""Todo — 内存任务列表"""

from __future__ import annotations
import json
from typing import Any

_todos: list[dict] = []

def todo(args: dict[str, Any]) -> str:
    global _todos
    action = args.get("action", "list")
    if action == "add":
        _todos.append({"task": args.get("task", ""), "done": False})
    elif action == "done":
        idx = int(args.get("index", 0))
        if 0 <= idx < len(_todos): _todos[idx]["done"] = True
    elif action == "clear":
        _todos = []
    return json.dumps({"todos": _todos})

SCHEMAS = {
    "todo": {
        "description": "Manage a todo list: list/add/done/clear tasks",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["list", "add", "done", "clear"]},
            "task": {"type": "string"}, "index": {"type": "integer"},
        }, "required": ["action"]},
    },
}
