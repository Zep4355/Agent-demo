# 一句话 Agent

一个"输入一句话 → Agent 自己拆任务、调工具、出成果"的迷你智能体 Demo。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API key（DeepSeek 注册送额度：https://platform.deepseek.com）
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 3. 运行
python main.py
```

## 试试这些指令

- 查一下西安今天的天气，整理成报告保存
- 现在几点了？顺便记下来
- 抓取 https://example.com 的内容，总结一下保存

## 项目结构

| 文件 | 作用 |
|---|---|
| `main.py` | 入口，命令行对话 |
| `web_app.py` | **网页版界面**（Streamlit，更好看） |
| `agent.py` | **Agent 核心：ReAct 循环**（面试重点） |
| `memory.py` | **持久记忆模块**（跨对话记住信息） |
| `tools.py` | 工具注册表：天气/时间/写文件/抓网页 |
| `config.py` | 配置读取 |
| `start.bat` | Windows 一键启动 |
| `output/` | Agent 生成的文件都在这 |

## 🧠 持久记忆（进阶版，已内置）

Agent 现在能**跨对话记住信息**，越用越懂你。

- **LLM 模式自动记**：对话中你透露重要信息（名字、偏好、常用地点等），Agent 自动存进 `memory.json`
- **网页版记忆面板**：左侧/上方有个"🧠 长期记忆"面板，可查看、手动添加、清空记忆
- **下次自动用上**：再次启动 Agent 时，会把这些记忆作为背景讲给它听

**手动添加一条记忆试试**：
> 添加一条要让 Agent 记住的信息 → 输入"用户常用城市西安" → 点➕添加

> ⚠️ 提醒：`memory.json` 存的是你个人偏好信息，已被 `.gitignore` 排除，**不会推送到 GitHub**，放心。
> 注：云端 Streamlit 部署的记忆存在运行时临时目录，应用冷启动可能重置；**本地跑记忆体验最完整**。若要云端真正持久化，需要接数据库（进阶任务）。

## 没配 API key 也能跑？

能。没 key 时自动进入「规则演示模式」，用规则模拟 Agent 决策，体验完整的"拆任务→调工具→出成果"流程；配了 key 就是真实大模型自主决策。

## 给 Agent 加新工具（5 分钟，面试加分）

1. 在 `tools.py` 写一个函数
2. 在 `TOOLS` 列表里加一条描述
3. 完事。LLM 会自动学会用它。

详见《一句话Agent项目方案.md》
