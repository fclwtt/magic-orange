"""MagicOrange — 桌面 agent 后端 (Hermes-style JSON-RPC 2.0 + session management)"""

from __future__ import annotations

import os, sys, json, logging, uuid, yaml
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("magic-orange")

from base_agent import create_agent


# ── Config ─────────────────────────────────────────────────
def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return _expand_env(cfg)


def _expand_env(obj):
    """Recursively expand `${VAR}` in strings."""
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(v) for v in obj]
    return obj


# ── CLI ────────────────────────────────────────────────────
def cli_loop(agent):
    """CLI 交互模式"""
    print("\nMagicOrange  — 输入 /quit 退出\n")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not query or query == "/quit":
            break
        result = agent.run_conversation(query)
        print(f"\n{result.get('final_response', '')}\n")


# ── WebSocket (JSON-RPC 2.0 + Streaming Events) ────────────
def _make_error(request_id: Any, code: int, message: str) -> str:
    return json.dumps({
        "jsonrpc": "2.0", "id": request_id,
        "error": {"code": code, "message": message},
    })


def _make_response(request_id: Any, result: Any) -> str:
    return json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})


def _event(event_type: str, payload: dict, session_id: str | None = None) -> str:
    """Build a JSON-RPC 2.0 server notification event."""
    msg: dict = {
        "method": "event",
        "params": {"type": event_type, "payload": payload},
    }
    if session_id:
        msg["params"]["session_id"] = session_id
    return json.dumps(msg)


def ws_loop(agent_factory):
    """WebSocket 模式 — JSON-RPC 2.0 with session management."""
    try:
        import asyncio, websockets
    except ImportError:
        logger.error("WebSocket mode requires: pip install websockets")
        sys.exit(1)

    sessions: dict[str, Any] = {}  # session_id -> AgentRuntime
    raw_cfg = load_config()
    session_config = raw_cfg.get("session", {})
    llm_cfg = raw_cfg.get("llm", {})
    guardrail_cfg = raw_cfg.get("tool_loop_guardrails", {})

    def _make_agent():
        return create_agent({
            "model": llm_cfg.get("model", "gpt-4"),
            "api_key": llm_cfg.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", ""),
            "base_url": llm_cfg.get("base_url", "https://api.openai.com/v1"),
            "max_iterations": session_config.get("max_iterations", 60),
            "tool_loop_guardrails": guardrail_cfg,
        })

    async def handler(websocket):
        logger.info("Client connected: %s", websocket.remote_address)

        async def send_event(event_type: str, payload: dict, sid: str | None = None):
            await websocket.send(_event(event_type, payload, sid))

        async for raw in websocket:
            try:
                request = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send(_make_error(None, -32700, "Parse error"))
                continue

            req_id = request.get("id")
            method = request.get("method", "")
            params = request.get("params", {})

            try:
                # ── session.create ──
                if method == "session.create":
                    sid = str(uuid.uuid4())[:12]
                    agent = _make_agent()
                    sessions[sid] = agent
                    logger.info("Session created: %s", sid)
                    await websocket.send(_make_response(req_id, {"session_id": sid}))

                # ── session.resume ──
                elif method == "session.resume":
                    sid = params.get("session_id", "")
                    if sid not in sessions:
                        await websocket.send(_make_error(req_id, -32000, f"Session not found: {sid}"))
                    else:
                        await websocket.send(_make_response(req_id, {"session_id": sid}))

                # ── prompt.submit ──
                elif method == "prompt.submit":
                    sid = params.get("session_id", "")
                    text = params.get("text", "").strip()
                    if not text:
                        await websocket.send(_make_error(req_id, -32602, "Missing 'text' param"))
                        continue

                    if sid not in sessions:
                        sid = str(uuid.uuid4())[:12]
                        sessions[sid] = _make_agent()
                        await send_event("session.created", {"session_id": sid}, sid)

                    agent = sessions[sid]

                    # ACK the request
                    await websocket.send(_make_response(req_id, {"status": "processing"}))

                    # Stream events
                    for event in agent.run_conversation_stream(text):
                        await send_event(event["type"], event, sid)

                # ── session.reset ──
                elif method == "session.reset":
                    sid = params.get("session_id", "")
                    if sid in sessions:
                        sessions[sid].reset()
                        await websocket.send(_make_response(req_id, {"session_id": sid, "reset": True}))
                    else:
                        await websocket.send(_make_error(req_id, -32000, f"Session not found: {sid}"))

                # ── ping ──
                elif method == "ping":
                    await websocket.send(_make_response(req_id, {"pong": True, "sessions": len(sessions)}))

                else:
                    await websocket.send(_make_error(req_id, -32601, f"Method not found: {method}"))

            except Exception as e:
                logger.error("Handler error for method %s: %s", method, e, exc_info=True)
                await websocket.send(_make_error(req_id, -32603, str(e)))

    port = int(os.getenv("MO_WS_PORT", "8765"))
    token = os.getenv("MO_WS_TOKEN", "")
    logger.info("WebSocket server on ws://127.0.0.1:%d%s", port, f"?token={token}" if token else "")

    async def serve():
        async with websockets.serve(handler, "127.0.0.1", port):
            await asyncio.Future()

    asyncio.run(serve())


# ── Entry Point ────────────────────────────────────────────
def main():
    cfg = load_config()
    llm_cfg = cfg.get("llm", {})
    session_cfg = cfg.get("session", {})

    agent = create_agent({
        "model": llm_cfg.get("model", "gpt-4"),
        "api_key": llm_cfg.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", ""),
        "base_url": llm_cfg.get("base_url", "https://api.openai.com/v1"),
        "max_iterations": session_cfg.get("max_iterations", 60),
        "tool_loop_guardrails": cfg.get("tool_loop_guardrails", {}),
    })

    mode = sys.argv[1] if len(sys.argv) > 1 else "cli"
    if mode == "--mode=ws" or mode == "ws":
        ws_loop(lambda: create_agent({
            "model": llm_cfg.get("model", "gpt-4"),
            "api_key": llm_cfg.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", ""),
            "base_url": llm_cfg.get("base_url", "https://api.openai.com/v1"),
            "max_iterations": session_cfg.get("max_iterations", 60),
            "tool_loop_guardrails": cfg.get("tool_loop_guardrails", {}),
        }))
    else:
        cli_loop(agent)


if __name__ == "__main__":
    main()
