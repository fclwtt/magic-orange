"""MagicOrange — 桌面 agent 后端"""

from __future__ import annotations

import os, sys, json, logging, yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("magic-orange")

# ── 使用本地 base_agent（已复制到本目录） ─────────────────
from base_agent import create_agent


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def cli_loop(agent):
    """CLI 交互模式"""
    print("\nMagicOrange 🍊  — 输入 /quit 退出\n")
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


def ws_loop(agent):
    """WebSocket 模式 — 供 Electron 桌面壳调用"""
    try:
        import asyncio, websockets
    except ImportError:
        logger.error("WebSocket mode requires: pip install websockets")
        sys.exit(1)

    async def handler(websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                query = data.get("query", "")
                if not query:
                    continue
                result = agent.run_conversation(query)
                await websocket.send(json.dumps({
                    "type": "response",
                    "content": result.get("final_response", ""),
                    "completed": result.get("completed", False),
                }))
            except Exception as e:
                await websocket.send(json.dumps({"type": "error", "content": str(e)}))

    port = int(os.getenv("MO_WS_PORT", "8765"))
    logger.info("WebSocket server on ws://127.0.0.1:%d", port)
    asyncio.run(websockets.serve(handler, "127.0.0.1", port))


def main():
    cfg = load_config()
    llm_cfg = cfg.get("llm", {})

    agent = create_agent({
        "model": llm_cfg.get("model", "gpt-4"),
        "api_key": llm_cfg.get("api_key") or os.getenv("OPENAI_API_KEY", ""),
        "base_url": llm_cfg.get("base_url", "https://api.openai.com/v1"),
        "max_turns": cfg.get("session", {}).get("max_history", 30),
    })

    mode = sys.argv[1] if len(sys.argv) > 1 else "cli"
    if mode == "--mode=ws" or mode == "ws":
        ws_loop(agent)
    else:
        cli_loop(agent)


if __name__ == "__main__":
    main()
