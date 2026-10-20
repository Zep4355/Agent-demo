# -*- coding: utf-8 -*-
"""
agent.py - Agent 核心：ReAct 循环（项目精华，面试重点讲这个文件）

流程：
    用户指令
      ↓
    ① Thought  思考：LLM 判断下一步做什么
      ↓
    ② Action   行动：LLM 决定调哪个工具、传什么参数
      ↓
    ③ 执行工具，拿到 Observation（观察结果）
      ↓
    ④ 把结果喂回去，回到 ① 继续循环
      ↓
    直到 LLM 给出 final_answer（最终答案），结束

原理一句话：让 LLM 在"想"和"做"之间交替，利用工具的真实反馈不断逼近任务目标。
"""
import json
import re
import requests

import config
from tools import TOOLS, run_tool, tools_description

# ---------------------------------------------------------------
# 提示词：告诉 LLM 你是谁、有哪些工具、按什么格式输出
# ---------------------------------------------------------------
SYSTEM_PROMPT = f"""你是一个能调用工具完成任务的智能体（Agent）。你的职责：拆解用户的任务，决定调用哪些工具，最终给出结果。

你可以使用以下工具：
{tools_description()}

【输出格式要求】
你每轮必须只输出一个 JSON 对象，不能输出其他文字。JSON 有两种类型：

1. 需要调用工具时，输出：
{{"thought": "这里写你的思考，说明为什么调用这个工具", "action": "工具名", "action_input": {{"参数名": "参数值"}}}}

2. 任务完成，可以给用户最终答案时，输出：
{{"thought": "这里写你的总结", "action": "final_answer", "action_input": {{"answer": "最终回复用户的内容"}}}}

【规则】
- 一次只调用一个工具，看到结果后再决定下一步。
- 如果用户要求"保存/整理成文件/生成报告"，记得用 write_markdown 工具。
- 工具结果会以"Observation:"开头的消息返回给你，你可以基于它继续思考。
- 最多 {config.MAX_STEPS} 轮内完成任务。
"""


class Agent:
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        # 记录完整对话历史（供 LLM 参考，也是"工作记忆"）
        self.history = []

    # ---------------------------------------------------------------
    # 对外入口
    # ---------------------------------------------------------------
    def run(self, user_input: str) -> str:
        print("\n🤖 Agent 开始工作...")
        if self.api_key:
            answer = self._run_with_llm(user_input)
        else:
            answer = self._run_with_rules(user_input)
        print("\n✅ Agent 完成！\n")
        return answer

    # ---------------------------------------------------------------
    # 模式一：LLM 驱动（完整 ReAct，需配置 DeepSeek API key）
    # ---------------------------------------------------------------
    def _run_with_llm(self, user_input: str) -> str:
        # 初始化对话：system + 用户指令
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        for step in range(1, config.MAX_STEPS + 1):
            print(f"\n—— 第 {step} 轮思考 ——")
            # ① 调用 LLM
            content = self._chat(messages)
            print(f"💭 LLM 输出：{content}")

            # ② 解析 LLM 输出的 JSON（容错：可能带代码块/多余文本）
            decision = self._parse_json(content)
            if decision is None:
                # 解析失败就当作最终答案
                return "（模型输出无法解析，已中止）" + content

            thought = decision.get("thought", "")
            action = decision.get("action", "")
            action_input = decision.get("action_input", {}) or {}

            if action == "final_answer":
                return action_input.get("answer", "任务完成")

            # ③ 执行工具
            if not any(t["name"] == action for t in TOOLS):
                observation = f"工具 {action} 不存在，请从工具清单中选择。"
            else:
                observation = run_tool(action, action_input)
            print(f"🛠  调用 {action}({action_input})\n📥 结果：{observation}")

            # ④ 把本轮行动和观察结果追加进对话，作为下一轮的依据
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Observation: {observation}"})

        return "已达到最大轮数，任务自动结束。你可以把 MAX_STEPS 调大。"

    # ---------------------------------------------------------------
    # 模式二：规则驱动（没配 API key 时也能跑，演示"拆任务+调工具"）
    # ---------------------------------------------------------------
    def _run_with_rules(self, user_input: str) -> str:
        print("⚠️  未配置 DEEPSEEK_API_KEY，当前使用【规则演示模式】。")
        print("    配置 key 后（见 README）将使用真实大模型自主决策。\n")

        s = user_input
        collected = []

        # 常用城市列表（演示用：识别输入里出现的城市名）
        city_list = ["北京", "上海", "广州", "深圳", "杭州", "西安", "成都", "重庆",
                     "武汉", "南京", "天津", "苏州", "长沙", "青岛", "郑州", "大连",
                     "厦门", "福州", "昆明", "哈尔滨", "太原", "大同", "兰州", "乌鲁木齐"]
        city = next((c for c in city_list if c in s), "西安")

        # 规则拆任务：按关键词决定调什么工具（演示用）
        if "天气" in s:
            print(f"🛠  调用 get_weather(city={city})")
            obs = run_tool("get_weather", {"city": city})
            print(f"📥 结果：{obs}")
            collected.append(obs)

        if "时间" in s or "几点" in s or "日期" in s:
            print("🛠  调用 get_time()")
            obs = run_tool("get_time", {})
            print(f"📥 结果：{obs}")
            collected.append(obs)

        if "http" in s:
            url = re.search(r"https?://\S+", s)
            if url:
                print(f"🛠  调用 web_fetch(url={url.group(0)})")
                obs = run_tool("web_fetch", {"url": url.group(0)})
                print(f"📥 结果：{obs[:80]}...")
                collected.append(obs)

        # 如果用户要求保存，就生成报告文件（演示"出成果"）
        if "保存" in s or "文件" in s or "报告" in s or "整理" in s or "记下来" in s or "记录" in s:
            # 只把成功获取到的内容写进报告，失败信息不进文件
            ok = [c for c in collected if "失败" not in c and "执行成功" in c]
            content = "\n\n".join(ok) if ok else f"用户指令：{s}\n（规则演示模式未获取到有效数据）"
            title = re.search(r"《(.+?)》", s)
            filename = title.group(1) if title else "演示报告"
            print(f"🛠  调用 write_markdown(content, filename={filename})")
            obs = run_tool("write_markdown", {"content": content, "filename": filename})
            print(f"📥 结果：{obs}")
            collected.append(obs)

        if collected:
            return "规则演示模式完成。结果如下：\n" + "\n".join(collected)
        return "（规则演示模式）没识别到可执行的动作。试试输入：查一下西安今天的天气，整理成报告保存。"

    # ---------------------------------------------------------------
    # 内部工具方法
    # ---------------------------------------------------------------
    def _chat(self, messages) -> str:
        """调用 DeepSeek Chat Completions 接口"""
        url = f"{config.DEEPSEEK_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.MODEL,
            "messages": messages,
            "temperature": 0.7,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    @staticmethod
    def _parse_json(text: str):
        """从模型输出里提取 JSON（容忍 ```json 代码块和前后杂音）"""
        # 先尝试直接解析
        try:
            return json.loads(text)
        except Exception:
            pass
        # 提取第一个 {...} 块再解析
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None


if __name__ == "__main__":
    # 简单自测
    agent = Agent()
    print(agent.run("查一下西安今天的天气，整理成报告保存"))
