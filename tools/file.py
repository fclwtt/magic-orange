"""File operations — 读/写/搜索"""

from __future__ import annotations
import json, os, glob as glob_mod
from pathlib import Path
from typing import Any


def read_file(args: dict[str, Any]) -> str:
    path = args.get("path", "")
    try:
        p = Path(path).resolve()
        if not p.exists():
            return json.dumps({"error": f"File not found: {path}"})
        content = p.read_text(encoding="utf-8", errors="replace")
        offset = int(args.get("offset", 0))
        limit = int(args.get("limit", 0))
        if limit:
            lines = content.splitlines()[offset:offset + limit]
            content = "\n".join(lines)
        return json.dumps({"path": str(p), "content": content[:100000]})
    except Exception as e:
        return json.dumps({"error": str(e)})


def write_file(args: dict[str, Any]) -> str:
    path = args.get("path", "")
    content = args.get("content", "")
    try:
        p = Path(path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return json.dumps({"path": str(p), "size": len(content)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_files(args: dict[str, Any]) -> str:
    pattern = args.get("pattern", "")
    path = args.get("path", ".")
    try:
        matches = list(Path(path).rglob(pattern)) if "*" in pattern else list(Path(path).rglob(f"*{pattern}*"))
        return json.dumps({"results": [str(m) for m in matches[:50]]})
    except Exception as e:
        return json.dumps({"error": str(e)})


SCHEMAS = {
    "read_file": {
        "description": "Read a file's contents",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "offset": {"type": "integer"}, "limit": {"type": "integer"},
        }, "required": ["path"]},
    },
    "write_file": {
        "description": "Write content to a file",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"},
        }, "required": ["path", "content"]},
    },
    "search_files": {
        "description": "Search for files matching a pattern",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"}, "path": {"type": "string"},
        }, "required": ["pattern"]},
    },
}
