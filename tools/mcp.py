"""MCP tool bridge — connect to external MCP tool servers."""

from __future__ import annotations
import json, logging, subprocess, asyncio
from typing import Any

logger = logging.getLogger(__name__)

_MCP_CLIENTS: dict[str, dict] = {}


def discover_mcp_servers(config: dict[str, Any] | None) -> list[dict]:
    """Read MCP server config. Expected format:
    {
        "servers": [
            {"name": "fs", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]},
        ]
    }
    """
    if not config:
        return []
    servers = []
    if isinstance(config, dict):
        servers = config.get("mcp_servers", config.get("servers", []))
    elif isinstance(config, list):
        servers = config
    return servers


def _get_client(server: dict) -> dict | None:
    """Connect to an MCP server via stdio and return the client handle."""
    name = server["name"]
    if name in _MCP_CLIENTS:
        return _MCP_CLIENTS[name]

    try:
        proc = subprocess.Popen(
            [server["command"]] + server.get("args", []),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True,
        )
        _MCP_CLIENTS[name] = {
            "proc": proc,
            "server": server,
            "tools": [],
        }
        # Send initialize request (JSON-RPC 2.0)
        req = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "base-agent", "version": "0.1.0"}},
        })
        proc.stdin.write(req + "\n")
        proc.stdin.flush()
        resp = proc.stdout.readline()
        # Send initialized notification
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
        # List tools
        req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        proc.stdin.write(req + "\n")
        proc.stdin.flush()
        resp = proc.stdout.readline()
        data = json.loads(resp)
        if "result" in data and "tools" in data["result"]:
            _MCP_CLIENTS[name]["tools"] = data["result"]["tools"]
        return _MCP_CLIENTS[name]
    except Exception as e:
        logger.warning("MCP connect failed for %s: %s", name, e)
        return None


def get_mcp_tools(config: dict | None) -> list[dict]:
    """Return MCP tools from all configured servers as tool schemas."""
    tools = []
    for server in discover_mcp_servers(config):
        client = _get_client(server)
        if client:
            for t in client.get("tools", []):
                tools.append({
                    "type": "function",
                    "function": {
                        "name": f"mcp_{server['name']}_{t['name']}",
                        "description": t.get("description", ""),
                        "parameters": t.get("inputSchema", {"type": "object", "properties": {}}),
                    },
                })
    return tools


def execute_mcp_tool(server_name: str, tool_name: str, args: dict[str, Any]) -> str:
    """Execute a tool on a remote MCP server."""
    client = _MCP_CLIENTS.get(server_name)
    if not client:
        return json.dumps({"error": f"MCP server '{server_name}' not connected"})

    try:
        req = json.dumps({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": tool_name, "arguments": args},
        })
        client["proc"].stdin.write(req + "\n")
        client["proc"].stdin.flush()
        resp = client["proc"].stdout.readline()
        data = json.loads(resp)
        if "result" in data and "content" in data["result"]:
            return json.dumps(data["result"]["content"])
        return json.dumps(data.get("error", {"error": "unknown error"}))
    except Exception as e:
        return json.dumps({"error": str(e)})


SCHEMAS = {}  # MCP tools are added dynamically based on config
