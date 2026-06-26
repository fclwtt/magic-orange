# Model Tools（模型工具定义）

> 生成 OpenAI 格式的工具定义，供 LLM API 使用

---

## 概述

`model-tools.py` 负责将注册的工具转换为 OpenAI API 需要的格式。

**代码规模**：577 行  
**来源文件**：`model_tools.py`

---

## 核心功能

### 1. 工具定义生成

将 Python 函数转换为 OpenAI 的 function calling 格式：

```python
# Python 函数
def terminal(command: str, timeout: int = 30) -> str:
    """执行终端命令"""
    pass

# 转换为 OpenAI 格式
{
    "type": "function",
    "function": {
        "name": "terminal",
        "description": "执行终端命令",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer"}
            },
            "required": ["command"]
        }
    }
}
```

### 2. 参数类型推断

自动从 Python 类型注解推断 JSON Schema 类型：

| Python 类型 | JSON Schema 类型 |
|------------|-----------------|
| `str` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `list` | `array` |
| `dict` | `object` |

### 3. 必填参数识别

没有默认值的参数自动标记为必填。

---

## 核心函数

### build_tool_definition

```python
def build_tool_definition(func: Callable) -> dict:
    """
    从 Python 函数构建工具定义
    
    Args:
        func: 工具处理函数
    
    Returns:
        OpenAI 格式的工具定义
    """
```

### get_tools_for_model

```python
def get_tools_for_model(
    registry: ToolRegistry,
    enabled_toolsets: List[str] = None,
    disabled_toolsets: List[str] = None
) -> List[dict]:
    """
    获取模型可用的工具定义
    
    Args:
        registry: 工具注册表
        enabled_toolsets: 启用的工具集
        disabled_toolsets: 禁用的工具集
    
    Returns:
        工具定义列表
    """
```

---

## 使用示例

```python
from hermes.core.model_tools import build_tool_definition, get_tools_for_model
from hermes.core.tool_registry import ToolRegistry

registry = ToolRegistry()

# 注册工具
registry.register(terminal_tool)
registry.register(file_tool)

# 获取工具定义
tools = get_tools_for_model(
    registry,
    enabled_toolsets=["terminal", "file"]
)

# 传递给 LLM API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    tools=tools
)
```

---

## 依赖组件

| 组件 | 用途 |
|------|------|
| `tool-registry` | 获取注册的工具 |

---

*来源: Hermes v0.8.0 | 文件: model_tools.py | 行数: 577*
