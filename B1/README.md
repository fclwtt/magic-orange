# MagicOrange B1 - 生产架构+混合部署

## 架构特点

- **生产架构**：完整的监控、日志、容错、配置管理
- **混合部署**：核心组件本地运行，关键组件可选分布式部署

## 适用场景

- ✅ 生产环境
- ✅ 中小规模部署
- ✅ 需要高可用但不想过度复杂
- ✅ 渐进式微服务化

## 架构概览

```
┌─────────────────────────────────────────────────┐
│              MagicOrange B1                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  本地进程（核心）                                 │
│  ├── Agent Engine (带熔断、限流)                 │
│  ├── Tool System (带重试、降级)                  │
│  └── Gateway (高可用)                            │
│                                                 │
│  可选分布式组件                                    │
│  ├── Memory Cluster (Redis/PostgreSQL)          │
│  └── Config Center (Consul/etcd)                │
│                                                 │
│  基础设施                                         │
│  ├── Prometheus + Grafana (监控)                 │
│  ├── ELK Stack (日志)                            │
│  └── Jaeger (链路追踪)                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 生产级特性

### 1. 高可用

- ✅ 服务健康检查
- ✅ 自动故障转移
- ✅ 优雅降级
- ✅ 熔断机制

### 2. 监控告警

- ✅ Prometheus 指标采集
- ✅ Grafana 可视化
- ✅ 告警规则配置
- ✅ 链路追踪

### 3. 日志管理

- ✅ 结构化日志
- ✅ 集中式日志收集
- ✅ 日志轮转和归档
- ✅ 日志查询分析

### 4. 配置管理

- ✅ 配置中心（Consul/etcd）
- ✅ 动态配置更新
- ✅ 配置版本管理
- ✅ 配置灰度发布

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置基础设施

```bash
# 启动 Prometheus + Grafana
docker-compose -f infra/monitoring.yml up -d

# 启动 ELK Stack
docker-compose -f infra/logging.yml up -d

# 启动 Consul（可选）
docker-compose -f infra/config-center.yml up -d
```

### 3. 配置应用

```bash
# 复制生产配置
cp config/config.prod.yaml.example config/config.yaml

# 编辑配置
vim config/config.yaml
```

### 4. 启动服务

```bash
# 生产模式启动
python main.py --env production

# 或使用 systemd
sudo systemctl start magic-orange
```

## 目录结构

```
B1/
├── core/                  # 核心底座（生产级）
│   ├── agent_loop.py          # 带熔断、限流
│   ├── tool_registry.py       # 带重试、降级
│   └── state_manager.py       # 高可用状态管理
├── agent/                 # 增强层
│   ├── memory_manager.py      # 支持分布式存储
│   └── error_classifier.py    # 错误分类和处理
├── tools/                 # 工具层
│   └── environments/          # 执行环境（带隔离）
├── gateway/               # 网关层（高可用）
│   └── run.py
├── platforms/             # 平台适配
├── config/                # 配置
│   ├── config.prod.yaml       # 生产配置
│   └── logging.yaml           # 日志配置
├── infra/                 # 基础设施
│   ├── monitoring.yml         # Prometheus + Grafana
│   ├── logging.yml            # ELK Stack
│   └── config-center.yml      # Consul
├── monitoring/            # 监控配置
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
└── scripts/               # 运维脚本
    ├── deploy.sh
    ├── backup.sh
    └── health_check.sh
```

## 配置示例

```yaml
# config/config.prod.yaml
app:
  name: MagicOrange-B1
  env: production
  log_level: INFO

llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  timeout: 30
  retry:
    max_attempts: 3
    backoff: exponential

memory:
  type: distributed
  backend: redis
  redis:
    host: redis-cluster
    port: 6379
    password: ${REDIS_PASSWORD}
  fallback:
    type: local
    path: ./data/memory

gateway:
  port: 8080
  ssl:
    enabled: true
    cert: /etc/ssl/certs/magic-orange.crt
    key: /etc/ssl/private/magic-orange.key
  rate_limit:
    requests_per_minute: 100
  circuit_breaker:
    enabled: true
    threshold: 5
    timeout: 60

monitoring:
  prometheus:
    enabled: true
    port: 9090
  jaeger:
    enabled: true
    endpoint: http://jaeger:14268/api/traces

health_check:
  enabled: true
  interval: 30
  endpoint: /health
```

## 监控仪表盘

### 关键指标

- **Agent 循环**：请求数、延迟、错误率
- **工具执行**：执行时间、成功率
- **记忆系统**：读写延迟、缓存命中率
- **网关**：连接数、消息吞吐量

### 告警规则

```yaml
# monitoring/alerts.yml
groups:
  - name: magic-orange
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高延迟"
```

## 资源占用

- **应用内存**: ~1GB
- **基础设施内存**: ~4GB（Prometheus + Grafana + ELK）
- **总CPU**: 4-8 核
- **磁盘**: ~10GB（含日志）
- **启动时间**: ~30秒

## 运维手册

### 日志查看

```bash
# 查看应用日志
tail -f logs/magic-orange.log

# 查询 ELK
curl -X GET "localhost:9200/magic-orange-*/_search"
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 检查依赖服务
python scripts/health_check.py
```

### 备份恢复

```bash
# 备份数据
./scripts/backup.sh

# 恢复数据
./scripts/restore.sh <backup_file>
```

## 升级到 B2

如果需要完全微服务化，参考 [B2 文档](../B2/README.md)

## License

MIT
