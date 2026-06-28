 # MagicOrange 🍊
 
 MagicOrange 是一个轻量级 AI Agent，基于 agent-component-library 构建，提供 CLI 和桌面两种交互方式。
 
 ## 目录结构
 
 ```
 magic-orange/
 ├── config.yaml        # 配置文件
 ├── config/
 │   └── config.py      # 网关配置管理
 ├── desktop/           # Electron 桌面应用
 │   ├── main.js        # 主进程
 │   ├── preload.js     # 预加载脚本
 │   ├── package.json
 │   └── renderer/
 │       └── index.html # 聊天 UI
 ├── main.py            # CLI 入口
 └── requirements.txt
 ```
 
 ## 快速开始
 
 ```bash
 pip install -r requirements.txt
 python main.py
 ```
 
 桌面版（需要 Node.js）：
 
 ```bash
 cd desktop
 npm install
 npm start
 ```
 
 ## 组件来源
 
 核心逻辑由 [fclwtt/agent-component-library](https://github.com/fclwtt/agent-component-library) 提供，包括 Agent 引擎、工具系统、LLM 客户端、状态管理等。
 
 ## 配置
 
 编辑 `config.yaml`，通过环境变量注入 API Key：
 
 ```bash
 export OPENAI_API_KEY=sk-xxx
 ```
 
 ## 环境要求
 
 - Python 3.11+
 - Node.js 20+（桌面版）
 
 ## License
 
 MIT
 
 ---
 
 *MagicOrange - 轻量级 AI Agent，CLI & Desktop* 🍊
