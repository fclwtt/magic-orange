# MagicOrange B2 - 生产架构+微服务

## 架构特点

- **生产架构**：完整的监控、日志、容错、配置管理
- **微服务**：所有组件独立部署，完全分布式

## 适用场景

- ✅ 大规模生产环境
- ✅ 高并发场景
- ✅ 需要独立扩展各组件
- ✅ 多团队协作
- ✅ 复杂业务逻辑

## 架构概览

```
┌──────────────────────────────────────────────────────────┐
│                    MagicOrange B2                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Agent     │  │    Tool     │  │   Memory    │    │
│  │  Service    │←→│  Service    │←→│  Service    │    │
│  │  (多实例)    │  │  (多实例)    │  │  (集群)      │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│         ↓                ↓                ↓              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Service Mesh (Istio)                │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Gateway   │  │    Auth     │  │   Config    │    │
│  │  Service    │  │  Service    │  │  Service    │    │
│  │  (多实例)    │  │  (高可用)    │  │  (Consul)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                          │
│  基础设施                                                 │
│  ├── Kubernetes (容器编排)                                │
│  ├── Prometheus + Grafana (监控)                          │
│  ├── ELK Stack (日志)                                     │
│  ├── Jaeger (链路追踪)                                    │
│  └── Redis Cluster (缓存)                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 微服务列表

| 服务 | 实例数 | 职责 | 技术栈 |
|------|--------|------|--------|
| Agent Service | 3+ | Agent 核心循环 | Python + gRPC |
| Tool Service | 5+ | 工具执行 | Python + gRPC |
| Memory Service | 3+ | 记忆管理 | Python + Redis |
| Gateway Service | 3+ | 消息网关 | Python + WebSocket |
| Auth Service | 2+ | 认证授权 | Python + JWT |
| Config Service | 3 | 配置中心 | Consul |
| API Gateway | 2+ | 统一入口 | Kong/Nginx |

## 快速开始

### 1. 环境准备

```bash
# 安装 kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# 安装 Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 安装 Istio
curl -L https://istio.io/downloadIstio | sh -
```

### 2. 部署基础设施

```bash
# 部署 Kubernetes 集群（以 Minikube 为例）
minikube start --memory=8192 --cpus=4

# 部署 Istio
istioctl install --set profile=demo

# 部署监控栈
helm install prometheus prometheus-community/kube-prometheus-stack

# 部署日志栈
helm install elasticsearch elastic/elasticsearch
helm install kibana elastic/kibana
```

### 3. 部署应用

```bash
# 构建 Docker 镜像
docker build -t magic-orange/agent-service:latest -f docker/Dockerfile.agent .
docker build -t magic-orange/tool-service:latest -f docker/Dockerfile.tool .
docker build -t magic-orange/memory-service:latest -f docker/Dockerfile.memory .
docker build -t magic-orange/gateway-service:latest -f docker/Dockerfile.gateway .

# 推送到镜像仓库
docker push magic-orange/agent-service:latest
docker push magic-orange/tool-service:latest
docker push magic-orange/memory-service:latest
docker push magic-orange/gateway-service:latest

# 部署到 Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/agent-service.yaml
kubectl apply -f k8s/tool-service.yaml
kubectl apply -f k8s/memory-service.yaml
kubectl apply -f k8s/gateway-service.yaml
```

### 4. 验证部署

```bash
# 查看 Pod 状态
kubectl get pods -n magic-orange

# 查看服务
kubectl get svc -n magic-orange

# 查看日志
kubectl logs -f deployment/agent-service -n magic-orange

# 访问 API
kubectl port-forward svc/api-gateway 8080:80 -n magic-orange
curl http://localhost:8080/health
```

## 目录结构

```
B2/
├── services/              # 微服务代码
│   ├── agent-service/
│   │   ├── main.py
│   │   ├── grpc_server.py
│   │   └── Dockerfile
│   ├── tool-service/
│   ├── memory-service/
│   ├── gateway-service/
│   ├── auth-service/
│   └── api-gateway/
├── core/                  # 核心组件（被服务引用）
├── agent/
├── tools/
├── gateway/
├── k8s/                   # Kubernetes 配置
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── agent-service.yaml
│   ├── tool-service.yaml
│   ├── memory-service.yaml
│   ├── gateway-service.yaml
│   └── ingress.yaml
├── docker/                # Docker 配置
│   ├── Dockerfile.agent
│   ├── Dockerfile.tool
│   ├── Dockerfile.memory
│   ├── Dockerfile.gateway
│   └── docker-compose.yml
├── helm/                  # Helm Charts
│   ├── magic-orange/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── infrastructure/
├── istio/                 # Istio 配置
│   ├── virtual-services.yaml
│   ├── destination-rules.yaml
│   └── gateway.yaml
├── monitoring/            # 监控配置
│   ├── prometheus/
│   ├── grafana/
│   └── alerts/
├── scripts/               # 运维脚本
│   ├── deploy.sh
│   ├── rollback.sh
│   └── scale.sh
└── docs/                  # 文档
    ├── architecture.md
    ├── deployment.md
    └── troubleshooting.md
```

## 服务通信

### gRPC 通信

```protobuf
// proto/agent.proto
syntax = "proto3";

service AgentService {
  rpc ExecuteTask(TaskRequest) returns (TaskResponse);
  rpc StreamLogs(LogRequest) returns (stream LogEntry);
}

message TaskRequest {
  string task_id = 1;
  string input = 2;
  map<string, string> metadata = 3;
}

message TaskResponse {
  string task_id = 1;
  string output = 2;
  Status status = 3;
}
```

### 消息队列

```python
# 使用 RabbitMQ 进行异步通信
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq')
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body='Hello World!',
    properties=pika.BasicProperties(
        delivery_mode=2,  # 持久化
    )
)
```

## 配置管理

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: magic-orange-config
  namespace: magic-orange
data:
  config.yaml: |
    app:
      name: MagicOrange-B2
      env: production
    
    services:
      agent:
        replicas: 3
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
      
      tool:
        replicas: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
      
      memory:
        replicas: 3
        backend: redis-cluster
        redis:
          hosts:
            - redis-0.redis
            - redis-1.redis
            - redis-2.redis
```

## 自动扩缩容

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-service-hpa
  namespace: magic-orange
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: 100
```

## 资源占用

- **应用内存**: ~8GB（所有服务）
- **基础设施内存**: ~16GB（K8s + Istio + 监控）
- **总CPU**: 16-32 核
- **磁盘**: ~50GB
- **启动时间**: ~5分钟

## 优势

- ✅ 完全独立部署和扩展
- ✅ 故障完全隔离
- ✅ 技术栈灵活
- ✅ 团队完全并行
- ✅ 支持大规模并发

## 劣势

- ❌ 部署复杂度极高
- ❌ 运维成本高
- ❌ 网络开销大
- ❌ 调试困难
- ❌ 需要专业团队

## 运维手册

### 查看服务状态

```bash
# 查看所有 Pod
kubectl get pods -n magic-orange -o wide

# 查看服务详情
kubectl describe deployment agent-service -n magic-orange

# 查看日志
kubectl logs -f deployment/agent-service -n magic-orange --tail=100
```

### 扩缩容

```bash
# 手动扩容
kubectl scale deployment agent-service --replicas=5 -n magic-orange

# 查看 HPA
kubectl get hpa -n magic-orange
```

### 滚动更新

```bash
# 更新镜像
kubectl set image deployment/agent-service agent= magic-orange/agent-service:v2 -n magic-orange

# 查看更新状态
kubectl rollout status deployment/agent-service -n magic-orange

# 回滚
kubectl rollout undo deployment/agent-service -n magic-orange
```

### 故障排查

```bash
# 进入 Pod
kubectl exec -it <pod-name> -n magic-orange -- /bin/bash

# 查看事件
kubectl get events -n magic-orange --sort-by='.metadata.creationTimestamp'

# 查看网络策略
kubectl get networkpolicy -n magic-orange
```

## License

MIT
