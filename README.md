# MagicOrange 🍊

MagicOrange 是一个模块化的 AI Agent 框架，基于 Hermes 组件库完整嫁接，提供 4 种架构变体以满足不同场景需求。

## 架构变体

| 变体 | 架构类型 | 部署模式 | 适用场景 | 说明 |
|------|---------|---------|---------|------|
| **A1** | 基础架构 | 混合部署 | 开发测试 | 轻量级，快速启动，部分组件本地化 |
| **A2** | 基础架构 | 微服务 | 开发测试 | 完全微服务化，组件独立部署 |
| **B1** | 生产架构 | 混合部署 | 生产环境 | 高可用，部分组件分布式部署 |
| **B2** | 生产架构 | 微服务 | 生产环境 | 完全生产级，所有组件独立服务 |

## 目录结构

```
magic-orange-monorepo/
├── A1/              # 基础架构+混合部署
│   ├── core/        # 核心底座
│   ├── agent/       # 增强层
│   ├── tools/       # 工具层
│   ├── gateway/     # 网关层
│   └── platforms/   # 平台适配
├── A2/              # 基础架构+微服务
├── B1/              # 生产架构+混合部署
├── B2/              # 生产架构+微服务
└── README.md        # 本文件
```

## 快速开始

### A1 - 基础架构+混合部署

适合开发测试环境，快速启动：

```bash
cd A1
pip install -r requirements.txt
python main.py
```

### A2 - 基础架构+微服务

适合开发测试环境，组件独立部署：

```bash
cd A2
# 启动各个微服务
python services/agent_service.py
python services/tool_service.py
python services/gateway_service.py
```

### B1 - 生产架构+混合部署

适合生产环境，高可用部署：

```bash
cd B1
# 配置生产环境参数
cp config/config.prod.yaml.example config/config.yaml
# 启动服务
python main.py --env production
```

### B2 - 生产架构+微服务

适合生产环境，完全微服务化：

```bash
cd B2
# 使用 Docker Compose 启动所有服务
docker-compose up -d
```

## 架构对比

### 基础架构 vs 生产架构

| 特性 | 基础架构 (A1/A2) | 生产架构 (B1/B2) |
|------|----------------|----------------|
| 日志系统 | 本地文件日志 | 集中式日志（ELK/Loki） |
| 监控告警 | 基础监控 | Prometheus + Grafana |
| 容错机制 | 简单重试 | 熔断、限流、降级 |
| 配置管理 | 本地配置文件 | 配置中心（Consul/etcd） |
| 服务发现 | 硬编码地址 | 服务注册与发现 |

### 混合部署 vs 微服务

| 特性 | 混合部署 (A1/B1) | 微服务 (A2/B2) |
|------|----------------|--------------|
| 部署复杂度 | 低 | 高 |
| 启动速度 | 快 | 慢 |
| 资源占用 | 少 | 多 |
| 扩展性 | 一般 | 优秀 |
| 维护成本 | 低 | 高 |

## 组件来源

所有核心组件来自 [fclwtt/agent-component-library](https://github.com/fclwtt/agent-component-library)：

```
agent-component-library/
├── components/
│   ├── agent-engine/      → core/, agent/
│   ├── tool-system/       → tools/
│   ├── gateway/           → gateway/
│   ├── memory-system/     → agent/memory_manager.py
│   └── ...
```

## 开发阶段

### ✅ Phase 1: 核心底座
让 Agent 能"思考"和"调用工具"

### ✅ Phase 2: 增强层
让 Agent 有"记忆"和"容错"

### ✅ Phase 3: 工具层
让 Agent 能"干活"

### ✅ Phase 4: 网关/平台层
让 Agent 能"多渠道接入"

### 🔄 Phase 5: 架构变体
提供 4 种架构选择（当前阶段）

## 环境要求

- Python 3.11+
- Docker & Docker Compose（微服务版本）
- openai >= 1.50.0
- pyyaml >= 6.0

## License

MIT

---

*MagicOrange - 用组件库搭建的万能底座* 🍊
