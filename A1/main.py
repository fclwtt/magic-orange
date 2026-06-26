#!/usr/bin/env python3
"""
MagicOrange 万能底座 - 主入口

Phase 1 验收标准：CLI 模式下能对话，能调用一个 dummy 工具
"""
import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# 设置兼容层路径（必须在导入核心组件之前）
PROJECT_ROOT = Path(__file__).parent
COMPAT_DIR = PROJECT_ROOT / "_compat"
sys.path.insert(0, str(COMPAT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("magic-orange")

# 导入核心组件
from core.tool_registry import ToolRegistry, ToolEntry
from core.model_tools import get_tool_definitions
from openai import OpenAI


class MagicOrangeAgent:
    """
    MagicOrange 最小 Agent 实现
    
    演示核心组件协同工作：
    1. ToolRegistry - 工具注册和管理
    2. model_tools - 生成 LLM 工具定义
    3. OpenAI Client - 调用 LLM API
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        system_prompt: str = "你是一个有帮助的 AI 助手。"
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, Any]] = []
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 初始化工具注册表
        self.registry = ToolRegistry()
        self._register_default_tools()
        
        logger.info(f"MagicOrange Agent 初始化完成 (model={model})")
    
    def _build_tool_schema(self, name: str, description: str, properties: dict, required: list) -> dict:
        """构建工具 schema（OpenAI 格式）"""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def _register_default_tools(self):
        """注册默认工具"""
        
        # Dummy 工具 - 用于验收测试
        def dummy_tool(message: str) -> str:
            """一个简单的 dummy 工具，返回输入的消息"""
            return f"[Dummy Tool] 收到: {message}"
        
        def get_time() -> str:
            """获取当前时间"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 注册 dummy_tool
        self.registry.register(
            name="dummy_tool",
            toolset="basic",
            schema=self._build_tool_schema("dummy_tool", "一个简单的 dummy 工具", {"message": {"type": "string", "description": "输入消息"}}, ["message"]),
            handler=dummy_tool,
            check_fn=lambda: True,
            requires_env=[],
            is_async=False,
            description="一个简单的 dummy 工具",
            emoji="🧪",
            max_result_size_chars=10000
        )
        
        # 注册 get_time
        self.registry.register(
            name="get_time",
            toolset="basic",
            schema=self._build_tool_schema("get_time", "获取当前时间", {}, []),
            handler=get_time,
            check_fn=lambda: True,
            requires_env=[],
            is_async=False,
            description="获取当前时间",
            emoji="🕐",
            max_result_size_chars=100
        )
        
        logger.info(f"已注册 {len(self.registry.get_all_tool_names())} 个工具")
    
    def _get_tool_schemas(self) -> List[Dict]:
        """获取工具定义（OpenAI 格式）"""
        tools = []
        for name in self.registry.get_all_tool_names():
            tool = self.registry._tools[name]
            if tool.check_fn is None or tool.check_fn():
                tools.append(tool.schema)
        return tools
    
    def _execute_tool(self, name: str, arguments: str) -> str:
        """执行工具调用"""
        try:
            args = json.loads(arguments)
            result = self.registry.dispatch(name, args)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {e}"
    
    def chat(self, user_message: str) -> str:
        """
        处理用户消息并返回回复
        
        流程：
        1. 添加用户消息到历史
        2. 调用 LLM API（带工具定义）
        3. 如果有工具调用，执行并继续对话
        4. 返回最终回复
        """
        # 添加用户消息
        self.messages.append({"role": "user", "content": user_message})
        
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}] + self.messages
        
        # 获取工具定义
        tools = self._get_tool_schemas()
        
        # 调用 LLM
        max_iterations = 10  # 防止无限循环
        for iteration in range(max_iterations):
            logger.debug(f"Iteration {iteration + 1}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
            )
            
            choice = response.choices[0]
            assistant_message = choice.message
            
            # 添加助手消息到历史
            self.messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })
            
            # 如果没有工具调用，返回回复
            if not assistant_message.tool_calls:
                return assistant_message.content or ""
            
            # 处理工具调用
            for tool_call in assistant_message.tool_calls:
                logger.info(f"🔧 调用工具: {tool_call.function.name}")
                result = self._execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments
                )
                logger.info(f"📤 工具结果: {result[:100]}...")
                
                # 添加工具结果到消息
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": assistant_message.tool_calls
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return "达到最大迭代次数，停止执行。"
    
    def reset(self):
        """重置对话历史"""
        self.messages = []
        logger.info("对话历史已重置")


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MagicOrange 万能底座")
    parser.add_argument("--api-key", help="API Key (或设置 OPENAI_API_KEY 环境变量)")
    parser.add_argument("--base-url", default="https://api.openai.com/v1", help="API Base URL")
    parser.add_argument("--model", default="gpt-4o-mini", help="模型名称")
    parser.add_argument("--query", help="直接执行查询（非交互模式）")
    args = parser.parse_args()
    
    # 获取 API Key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请提供 API Key (--api-key 或 OPENAI_API_KEY 环境变量)")
        sys.exit(1)
    
    # 创建 Agent
    print("🍊 MagicOrange 万能底座")
    print("=" * 40)
    
    agent = MagicOrangeAgent(
        api_key=api_key,
        base_url=args.base_url,
        model=args.model
    )
    
    # 显示可用工具
    print("\n📦 可用工具:")
    for name in agent.registry.get_all_tool_names():
        tool = agent.registry._tools[name]
        print(f"  {tool.emoji} {tool.name}: {tool.description}")
    print()
    
    # 非交互模式
    if args.query:
        print(f"👤 {args.query}")
        response = agent.chat(args.query)
        print(f"\n🤖 {response}")
        return
    
    # 交互模式
    print("输入 'quit' 退出，'reset' 重置对话\n")
    
    while True:
        try:
            user_input = input("👤 ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("👋 再见！")
                break
            
            if user_input.lower() == "reset":
                agent.reset()
                print("🔄 对话已重置\n")
                continue
            
            response = agent.chat(user_input)
            print(f"\n🤖 {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


if __name__ == "__main__":
    main()
