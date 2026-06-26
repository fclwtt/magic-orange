# MagicOrange A1 - 基础架构+混合部署

## 架构特点

- **基础架构**：简化的监控、日志、配置管理
- **混合部署**：核心组件本地运行，部分组件可选分布式部署

## 适用场景

- ✅ 开发测试环境
- ✅ 个人项目
- ✅ 快速原型验证
- ✅ 资源受限环境

## 架构概览

```
┌─────────────────────────────────────┐
│         MagicOrange A1              │
├─────────────────────────────────────┤
│  本地进程                            │
│  ├── Agent Engine (核心循环)         │
│  ├── Tool System (工具执行)          │
│  ├── Memory System (本地存储)        │
│  └── Gateway (单实例)                │
└─────────────────────────────────────┘
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置
cp config/config.yaml.example config/config.yaml
# 编辑 config/config.yaml 设置 API keys

# 启动
python main.py
```

## 目录结构

```
A1/
├── core/              # 核心底座
│   ├── agent_loop.py      # Agent 循环
│   ├── tool_registry.py   # 工具注册
│   └── state_manager.py   # 状态管理
├── agent/             # 增强层
│   ├── memory_manager.py    # 记忆管理
│   └── prompt_builder.py    # 提示词构建
├── tools/             # 工具层
│   ├── terminal_tool.py   # 终端执行
│   ├── file_tools.py      # 文件操作
│   └── web_tools.py       # 网络搜索
├── gateway/           # 网关层
│   └── run.py             # 网关核心
├── platforms/         # 平台适配
│   ├── wecom.py           # 企业微信
│   └── feishu.py          # 飞书
└── config/            # 配置管理
    └── config.yaml        # 配置文件
```

## 配置示例

```yaml
# config/config.yaml
app:
  name: MagicOrange-A1
  env: development

llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}

memory:
  type: local
  path: ./data/memory

gateway:
  port: 8080
  platforms:
    - wecom
    - feishu
```

## 资源占用

- **内存**: ~500MB
- **CPU**: 1-2 核
- **磁盘**: ~200MB
- **启动时间**: < 5秒

## 限制

- ❌ 不支持水平扩展
- ❌ 单点故障风险
- ❌ 不适合高并发场景

## 升级到 A2

如果需要微服务化部署，参考 [A2 文档](../A2/README.md)

## License

MIT
