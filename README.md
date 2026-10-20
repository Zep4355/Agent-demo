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
| `tools.py` | 工具注册表：天气/时间/写文件/抓网页 |
| `config.py` | 配置读取 |
| `output/` | Agent 生成的文件都在这 |

## 没配 API key 也能跑？

能。没 key 时自动进入「规则演示模式」，用规则模拟 Agent 决策，体验完整的"拆任务→调工具→出成果"流程；配了 key 就是真实大模型自主决策。

## 给 Agent 加新工具（5 分钟，面试加分）

1. 在 `tools.py` 写一个函数
2. 在 `TOOLS` 列表里加一条描述
3. 完事。LLM 会自动学会用它。

详见《一句话Agent项目方案.md》
