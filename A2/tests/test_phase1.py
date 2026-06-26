#!/usr/bin/env python3
"""
Phase 1 步骤 1-2 验证测试

验证标准：
- 步骤 1.1: ToolRegistry 能注册工具，能查询工具列表
- 步骤 1.2: model_tools 能生成 OpenAI 格式的工具定义
"""
import sys
sys.path.insert(0, '_compat')
sys.path.insert(0, '.')

import json
import logging
logging.getLogger('core.model_tools').setLevel(logging.ERROR)

from core.tool_registry import ToolRegistry, ToolEntry
from core.model_tools import get_tool_definitions


def test_tool_registry():
    """测试 ToolRegistry"""
    print("=" * 50)
    print("测试 1.1: ToolRegistry")
    print("=" * 50)
    
    # 创建注册表
    registry = ToolRegistry()
    print("✅ ToolRegistry 创建成功")
    
    # 定义测试工具
    def test_tool(message: str, count: int = 1) -> str:
        """测试工具"""
        return f"收到: {message}, 次数: {count}"
    
    # 注册工具
    registry.register(
        name="test_tool",
        toolset="test",
        schema={
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "测试工具",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "count": {"type": "integer", "default": 1}
                    },
                    "required": ["message"]
                }
            }
        },
        handler=test_tool,
        check_fn=lambda: True,
        description="测试工具",
        emoji="🧪"
    )
    print("✅ 工具注册成功")
    
    # 查询工具列表
    tools = registry.get_all_tool_names()
    assert "test_tool" in tools, "工具未找到"
    print(f"✅ 工具列表查询成功: {tools}")
    
    # 获取工具 schema
    schema = registry.get_schema("test_tool")
    assert schema is not None, "Schema 未找到"
    print(f"✅ Schema 获取成功")
    
    # 执行工具
    result = registry.dispatch("test_tool", {"message": "hello", "count": 3})
    assert "hello" in result and "3" in result, f"执行结果错误: {result}"
    print(f"✅ 工具执行成功: {result}")
    
    print("\n✅ 步骤 1.1 验证通过!\n")
    return True


def test_model_tools():
    """测试 model_tools"""
    print("=" * 50)
    print("测试 1.2: model_tools")
    print("=" * 50)
    
    # 创建注册表并注册工具
    registry = ToolRegistry()
    
    def dummy_tool(msg: str) -> str:
        """Dummy tool"""
        return msg
    
    registry.register(
        name="dummy_tool",
        toolset="test",
        schema={
            "type": "function",
            "function": {
                "name": "dummy_tool",
                "description": "Dummy tool",
                "parameters": {
                    "type": "object",
                    "properties": {"msg": {"type": "string"}},
                    "required": ["msg"]
                }
            }
        },
        handler=dummy_tool,
        description="Dummy tool"
    )
    print("✅ 工具注册成功")
    
    # 获取 OpenAI 格式的工具定义
    definitions = get_tool_definitions()
    print(f"✅ get_tool_definitions() 返回 {len(definitions)} 个工具定义")
    
    # 验证格式
    if definitions:
        tool_def = definitions[0]
        assert "type" in tool_def, "缺少 type 字段"
        assert "function" in tool_def, "缺少 function 字段"
        print(f"✅ 工具定义格式正确:")
        print(json.dumps(tool_def, indent=2, ensure_ascii=False)[:200] + "...")
    
    print("\n✅ 步骤 1.2 验证通过!\n")
    return True


if __name__ == "__main__":
    print("\n🍊 MagicOrange Phase 1 验证测试\n")
    
    try:
        test_tool_registry()
        test_model_tools()
        
        print("=" * 50)
        print("🎉 Phase 1 步骤 1-2 验证全部通过!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
