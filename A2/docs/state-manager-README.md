# State Manager（状态管理器）

> Hermes 全局状态管理，维护会话、配置、运行时状态

---

## 概述

`state-manager.py` 是 Hermes 的全局状态管理中心，负责：

- 会话状态持久化
- 配置管理
- 运行时状态追踪
- 跨模块状态共享

**代码规模**：1304 行  
**来源文件**：`hermes_state.py`

---

## 核心类

### HermesState

```python
class HermesState:
    """全局状态管理器"""
    
    def __init__(self, state_dir: str = "~/.hermes"):
        """
        初始化状态管理器
        
        Args:
            state_dir: 状态存储目录
        """
        
    # 会话管理
    def get_session(self, session_id: str) -> Session:
        """获取会话"""
        
    def save_session(self, session: Session) -> None:
        """保存会话"""
        
    def delete_session(self, session_id: str) -> None:
        """删除会话"""
        
    def list_sessions(self) -> List[Session]:
        """列出所有会话"""
    
    # 配置管理
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        
    def set_config(self, key: str, value: Any) -> None:
        """设置配置"""
    
    # 运行时状态
    def get_runtime(self, key: str) -> Any:
        """获取运行时状态"""
        
    def set_runtime(self, key: str, value: Any) -> None:
        """设置运行时状态"""
```

### Session

```python
@dataclass
class Session:
    """会话数据"""
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[dict]
    metadata: dict
    platform: str
    user_id: str
```

---

## 存储结构

```
~/.hermes/
├── sessions/              # 会话存储
│   ├── session-001.json
│   ├── session-002.json
│   └── ...
├── config.json            # 全局配置
├── credentials.json       # 凭证存储
└── cache/                 # 缓存
```

---

## 使用示例

```python
from hermes.core.state_manager import HermesState, Session

# 创建状态管理器
state = HermesState(state_dir="~/.hermes")

# 创建会话
session = Session(
    id="session-001",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    messages=[],
    metadata={"platform": "cli"},
    platform="cli",
    user_id="user-001"
)

# 保存会话
state.save_session(session)

# 获取会话
session = state.get_session("session-001")

# 添加消息
session.messages.append({
    "role": "user",
    "content": "Hello"
})

# 更新会话
state.save_session(session)

# 列出所有会话
sessions = state.list_sessions()
for s in sessions:
    print(f"Session {s.id}: {len(s.messages)} messages")
```

---

## 配置管理

```python
# 获取配置
api_key = state.get_config("api_key")
model = state.get_config("model", default="gpt-4")

# 设置配置
state.set_config("api_key", "***")
state.set_config("model", "deepseek-chat")
```

---

## 运行时状态

运行时状态用于跨模块共享临时数据：

```python
# 设置运行时状态
state.set_runtime("current_model", "deepseek-chat")
state.set_runtime("tool_calls_count", 0)

# 获取运行时状态
model = state.get_runtime("current_model")
```

---

## 依赖组件

| 组件 | 用途 |
|------|------|
| `agent-loop` | 使用状态管理器 |
| `session-manager` | 会话管理 |

---

## 注意事项

1. **线程安全**：状态管理器使用文件锁保证线程安全
2. **持久化**：会话和配置持久化到磁盘
3. **缓存**：频繁访问的数据会缓存到内存

---

*来源: Hermes v0.8.0 | 文件: hermes_state.py | 行数: 1304*
