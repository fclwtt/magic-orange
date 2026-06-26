# MagicOrange A2 - 基础架构+微服务

## 架构特点

- **基础架构**：简化的监控、日志、配置管理
- **微服务**：所有组件独立部署，通过 API 通信

## 适用场景

- ✅ 开发测试环境
- ✅ 需要独立扩展某些组件
- ✅ 团队协作开发
- ✅ 技术验证

## 架构概览

```
┌──────────────────────────────────────────────┐
│              MagicOrange A2                  │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─────────────┐  ┌─────────────┐          │
│  │   Agent     │  │    Tool     │          │
│  │  Service    │←→│  Service    │          │
│  └─────────────┘  └─────────────┘          │
│         ↓                ↓                  │
│  ┌─────────────┐  ┌─────────────┐          │
│  │   Memory    │  │   Gateway   │          │
│  │  Service    │  │  Service    │          │
│  └─────────────┘  └─────────────┘          │
│                                              │
└──────────────────────────────────────────────┘
```

## 微服务列表

| 服务 | 端口 | 职责 |
|------|------|------|
| Agent Service | 8001 | Agent 核心循环 |
| Tool Service | 8002 | 工具执行 |
| Memory Service | 8003 | 记忆管理 |
| Gateway Service | 8004 | 消息网关 |
| API Gateway | 8080 | 统一入口 |

## 快速开始

### 方式1：逐个启动服务

```bash
# 终端1：启动 Agent Service
cd services
python agent_service.py

# 终端2：启动 Tool Service
python tool_service.py

# 终端3：启动 Memory Service
python memory_service.py

# 终端4：启动 Gateway Service
python gateway_service.py

# 终端5：启动 API Gateway
python api_gateway.py
```

### 方式2：使用脚本一键启动

```bash
# Linux/Mac
./start_all.sh

# Windows
start_all.bat
```

## 目录结构

```
A2/
├── services/              # 微服务
│   ├── agent_service.py       # Agent 服务
│   ├── tool_service.py        # 工具服务
│   ├── memory_service.py      # 记忆服务
│   ├── gateway_service.py     # 网关服务
│   └── api_gateway.py         # API 网关
├── core/                  # 核心组件（被服务引用）
├── agent/
├── tools/
├── gateway/
├── config/                # 配置
│   └── services.yaml          # 服务配置
└── start_all.sh           # 启动脚本
```

## 配置示例

```yaml
# config/services.yaml
services:
  agent:
    host: localhost
    port: 8001
    dependencies:
      - tool
      - memory
  
  tool:
    host: localhost
    port: 8002
  
  memory:
    host: localhost
    port: 8003
    storage: local
  
  gateway:
    host: localhost
    port: 8004
  
  api_gateway:
    host: 0.0.0.0
    port: 8080
    routes:
      /agent: http://localhost:8001
      /tools: http://localhost:8002
```

## 服务通信

服务间通过 HTTP REST API 通信：

```python
# Agent Service 调用 Tool Service
import requests

response = requests.post(
    'http://localhost:8002/execute',
    json={
        'tool': 'terminal',
        'command': 'ls -la'
    }
)
```

## 资源占用

- **总内存**: ~1.5GB（5个服务）
- **总CPU**: 2-4 核
- **磁盘**: ~300MB
- **启动时间**: ~15秒

## 优势

- ✅ 组件独立部署和扩展
- ✅ 故障隔离
- ✅ 技术栈灵活
- ✅ 团队并行开发

## 劣势

- ❌ 部署复杂度高
- ❌ 网络开销
- ❌ 调试困难

## License

MIT
