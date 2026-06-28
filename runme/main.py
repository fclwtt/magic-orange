#!/usr/bin/env python3
"""
MagicOrange A1 — 万能底座入口

基于 agent-component-library 的 api.py 层运行。
"""
from __future__ import annotations

import os
import sys
import logging
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("magic-orange")

# 如果组件库以本地路径引用，添加搜索路径
_CL_LIB = Path(__file__).parent.parent.parent / "agent-component-library"
if _CL_LIB.exists() and str(_CL_LIB) not in sys.path:
    sys.path.insert(0, str(_CL_LIB))

from components.tool_system.api import create_tool_registry, ToolEntry
from components.llm_client.api import create_openai_client
from components.agent_engine.api import create_agent_runtime, AgentConfig
from components.state_management.api import create_config_manager


def load_config(path: str = "config/config.yaml") -> AgentConfig:
    """加载配置"""
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return AgentConfig(
        model=cfg.get("llm", {}).get("model", "gpt-4o-mini"),
        max_turns=cfg.get("session", {}).get("max_history", 100),
    )


def init_system(config: AgentConfig):
    """初始化所有子系统"""
    logger.info("Initializing subsystems...")

    cfg_mgr = create_config_manager()
    logger.info("  ✅ config manager ready")

    registry = create_tool_registry()
    logger.info("  ✅ tool registry ready")

    client = create_openai_client()
    logger.info("  ✅ LLM client ready")

    runtime = create_agent_runtime(config)
    logger.info("  ✅ agent runtime ready")

    return registry, client, runtime


def cli_loop(runtime):
    """CLI 交互模式"""
    print("\nMagicOrange A1 🍊  — 输入 /quit 退出\n")
    session_id = "default"

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            break

        result = runtime.execute_turn(user_input, session_id)
        print(f"\n{result.message}\n")


def main():
    config = load_config()
    _, _, runtime = init_system(config)
    cli_loop(runtime)


if __name__ == "__main__":
    main()
