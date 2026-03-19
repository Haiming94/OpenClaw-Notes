# 🔬 WestOdyssey：一个面向科研攻关的智能协作系统


> 基于 OpenClaw + Vue3 的多智能体科研协作平台

## 📋 项目概述

本项目构建了一个面向 AI/ML 研究人员的**多智能体科研协作系统**，集成 5 个专业智能体，覆盖从文献调研到论文审稿的完整科研工作流。

![](./images/poster2.jpg)

### 核心特性

- 🤖 **5 个专业 Agent**：唐僧、孙悟空、猪八戒、沙僧、白龙马
- 🤖 **唐 僧**：科研战略与方向规划 Agent
- 🤖 **孙悟空**：算法开发与编程实现 Agent
- 🤖 **猪八戒**：学术写作与项目申报 Agent
- 🤖 **沙 僧**：文献管理与知识整合 Agent
- 🤖 **白龙马**：数据工程与流程自动化 Agent
- 🌊 **会话分页**：可以根据不同的任务需求与同一个 Agent 建立分页对话
- 📝 **动态输入**：在与 Agent 对话过程中，可以随时停止当前任务
- 💬 **独立会话**：每个 Agent 维护独立的对话历史
- 🎨 **现代 UI**：深色主题科研工作室界面

![](./images/ui.png)

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│          Streamlit 前端 (:8001)          │
│  📚唐僧  📊白龙马  🧪孙悟空  ✍️猪八戒  🔍沙僧 │
│         ↓ @mention 路由                  │
│    POST /v1/chat/completions            │
│    Header: X-OpenClaw-Agent-Id          │
│    Header: X-OpenClaw-Session-Key       │
└──────────────┬──────────────────────────┘
               │ HTTP (OpenAI 兼容协议)
┌──────────────┴──────────────────────────┐
│      OpenClaw Gateway (:18789)           │
│  ┌─────────────────────────────────┐     │
│  │ sanzang │ wukong │ wuneng       │     │
│  │ wujing     │ horse              │     │
│  └─────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

## 📁 项目结构

```
dev_a/
├── .env.example              # 环境变量模板
├── requirements.txt          # Python 依赖
├── setup.sh                  # 一键安装
├── start.sh                  # 一键启动
├── openclaw_config/
│   └── openclaw.json         # OpenClaw 5 Agent 配置
├── agents/
│   ├── base.py               # Agent 基类 (API 调用封装)
│   ├── sanzang.py            # 📚 唐僧 system prompt
│   ├── horse.py              # 📊 白龙马 system prompt
│   ├── wukong.py             # 🧪 孙悟空 system prompt
│   ├── wuneng.py             # ✍️ 猪八戒 system prompt
│   └── wujing.py             # 🔍 沙僧 system prompt
├── core/
│   ├── config.py             # 项目配置管理
│   ├── session_manager.py    # 会话管理 (创建/切换/持久化)
│   ├── message_router.py     # @mention 解析与路由
│   └── stream_handler.py     # SSE 流式响应解析
├── ui/
│   ├── index.html            # 主页
│   ├── dist/
│   ├── node_modules/
│   ├── public/
│   └── src/
└── tests/
    ├── test_agent_base.py
    ├── test_message_router.py
    └── test_session_manager.py
```

## 🚀 快速开始

### 1. 安装

```bash
cd dev_a
chmod +x setup.sh start.sh
./setup.sh
```

### 2. 配置

编辑 `.env` 文件：

```bash
# OpenClaw Gateway 地址
OPENCLAW_GATEWAY_URL=http://localhost:18789

# Gateway 认证 Token
OPENCLAW_AUTH_TOKEN=your-token-here
```

### 3. 配置 OpenClaw Agents

将 `openclaw_config/openclaw.json` 中的 agents 配置合并到你的 `~/.openclaw/openclaw.json`：

```bash
# 查看配置
cat openclaw_config/openclaw.json

# 编辑你的 OpenClaw 配置
vim ~/.openclaw/openclaw.json
```

确保：
- `gateway.http.chatCompletions.enabled: true`
- `gateway.auth.token` 已设置
- 5 个 agent (唐僧、孙悟空、猪八戒、沙僧、白龙马) 已配置

### 4. 启动

```bash
# 先确保 OpenClaw Gateway 运行中
openclaw gateway start

# 启动前端
./start.sh
```

访问 `http://localhost:8001`

## 🤖 5 个智能体

| Agent | 名称 | 功能 | @提及 |
|-------|------|------|-------|
| 📚 | 唐僧 | 定义研究问题与科学目标、制定阶段性计划 | `@讨论` `@discussion` `@dis` |
| 🧪 | 孙悟空 | 实验设计、模型训练、超参调优 | `@实验` `@experiment` `@exp` |
| ✍️ | 猪八戒 | 论文撰写、LaTeX、学术润色 | `@写作` `@writer` `@wrt` |
| 🔍 | 沙僧 | 检索文献、领域综述、定时总结 | `@文献` `@literature` `@lit` |
| 📊 | 白龙马 | 数据清洗、特征工程、可视化 | `@数据` `@data` `@dat` |

## 🔧 技术栈

- **前端**: Vue3
- **后端**: OpenClaw Gateway (OpenAI 兼容 HTTP API)
- **协议**: HTTP + SSE (Server-Sent Events)
- **语言**: Python 3.9+

## 📡 API 对接原理

前端通过 OpenClaw Gateway 的 **OpenAI 兼容 HTTP API** 与后端通信：

```
POST http://gateway:18789/v1/chat/completions
Headers:
  Authorization: Bearer <token>
  X-OpenClaw-Agent-Id: wukong          # 路由到指定 Agent
  X-OpenClaw-Session-Key: agent:...    # 会话隔离
  X-OpenClaw-Message-Channel: webchat  # 标识来源
Body:
  { "model": "openclaw/wukong", "messages": [...], "stream": true }
```

