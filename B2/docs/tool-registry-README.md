# Tool Registry（工具注册中心）

> Hermes 的工具注册和调度中心，管理所有可用工具

---

## 概述

`tool-registry.py` 是 Hermes 的工具管理系统，负责：

- 工具注册和发现
- 工具定义生成（OpenAI 格式）
- 工具调用分发
- 工具可用性检查

**代码规模**：335 行  
**来源文件**：`tools/registry.py`

---

## 核心类

### ToolEntry

```python
@dataclass
class ToolEntry:
    name: str              # 工具名称
    toolset: str           # 所属工具集
    schema: dict           # OpenAI 格式的工具定义
    handler: Callable      # 处理函数
    check_fn: Callable     # 可用性检查函数
    requires_env: list     # 需要的环境变量
    is_async: bool         # 是否异步
    description: str       # 描述
    emoji: str             # 图标
    max_result_size_chars: int  # 结果最大字符数
```

### ToolRegistry

```python
class ToolRegistry:
    """工具注册表（单例模式）"""
    
    def register(self, tool: ToolEntry) -> None:
        """注册工具"""
        
    def unregister(self, name: str) -> None:
        """注销工具"""
        
    def get(self, name: str) -> Optional[ToolEntry]:
        """获取工具"""
        
    def list_tools(self, toolset: str = None) -> List[ToolEntry]:
        """列出工具"""
        
    def get_openai_schemas(self) -> List[dict]:
        """获取 OpenAI 格式的工具定义"""
        
    def execute(self, name: str, **kwargs) -> Any:
        """执行工具"""
```

---

## 使用示例

### 注册工具

```python
from hermes.core.tool_registry import ToolRegistry, ToolEntry

registry = ToolRegistry()

# 定义工具处理函数
def terminal_handler(command: str, timeout: int = 30) -> str:
    """执行终端命令"""
    import subprocess
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        timeout=timeout
    )
    return result.stdout or result.stderr

# 创建工具定义
tool = ToolEntry(
    name="terminal",
    toolset="terminal",
    schema={
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "执行终端命令",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"},
                    "timeout": {"type": "integer", "description": "超时时间(秒)", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    handler=terminal_handler,
    check_fn=lambda: True,  # 总是可用
    requires_env=[],
    is_async=False,
    description="执行终端命令",
    emoji="💻",
    max_result_size_chars=10000
)

# 注册工具
registry.register(tool)
```

### 执行工具

```python
# 执行工具
result = registry.execute("terminal", command="ls -la")
print(result)
```

### 获取工具定义

```python
# 获取 OpenAI 格式的工具定义（用于 LLM API）
schemas = registry.get_openai_schemas()
print(schemas)
# 输出:
# [
#   {
#     "type": "function",
#     "function": {
#       "name": "terminal",
#       "description": "执行终端命令",
#       "parameters": {...}
#     }
#   }
# ]
```

---

## 工具集（Toolset）

工具可以按功能分组到工具集：

| 工具集 | 包含工具 | 说明 |
|--------|---------|------|
| `terminal` | terminal, process | 终端和进程管理 |
| `file` | read_file, write_file, patch | 文件操作 |
| `web` | web_search, web_extract | 网络搜索 |
| `browser` | browser_* | 浏览器自动化 |
| `memory` | memory | 记忆工具 |
| `skills` | skills_* | Skill 管理 |

### 按工具集过滤

```python
# 获取特定工具集的工具
terminal_tools = registry.list_tools(toolset="terminal")

# 获取所有工具
all_tools = registry.list_tools()
```

---

## 依赖组件

| 组件 | 用途 |
|------|------|
| `agent-loop` | 调用工具执行 |
| `toolset-manager` | 工具集管理 |

---

## 注意事项

1. **单例模式**：ToolRegistry 是单例，全局只有一个实例
2. **工具名称唯一**：同名工具会覆盖
3. **可用性检查**：`check_fn` 用于动态检查工具是否可用（如检查环境变量）
4. **结果大小限制**：`max_result_size_chars` 防止返回过大结果

---

*来源: Hermes v0.8.0 | 文件: tools/registry.py | 行数: 335*
