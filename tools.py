# -*- coding: utf-8 -*-
"""
tools.py - 工具注册表（Agent 的"手脚"）

每个工具 = 一个普通 Python 函数 + 一段给 LLM 看的描述。
Agent 会根据任务自己决定调哪个工具、传什么参数。
"""
import os
import re
import datetime
import requests
from urllib.parse import quote

# ---------------------------------------------------------------
# 工具实现（每个函数一个真实能力）
# ---------------------------------------------------------------

def get_time() -> str:
    """返回当前日期和时间"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_weather(city: str = "西安") -> str:
    """
    查询指定城市的实时天气（使用免费的 wttr.in 接口，无需 API key）
    """
    try:
        # wttr.in 免费天气接口，?format=j1 返回 JSON，lang=zh 优先中文描述
        url = f"https://wttr.in/{quote(city)}?format=j1&lang=zh"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "curl/8.0"})
        data = resp.json()

        current = data["current_condition"][0]
        weather_desc = current["lang_zh"][0]["value"] if "lang_zh" in current else current["weatherDesc"][0]["value"]
        temp = current["temp_C"]
        feels = current["FeelsLikeC"]
        humidity = current["humidity"]
        wind = current["windspeedKmph"]

        return (f"{city}当前天气：{weather_desc}，气温 {temp}°C（体感 {feels}°C），"
                f"湿度 {humidity}%，风速 {wind} km/h")
    except Exception as e:
        return f"天气查询失败：{e}（请检查网络或城市名）"


def write_markdown(content: str, filename: str) -> str:
    """
    把内容写入 output 目录下的 Markdown 文件
    """
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    # 文件名安全化：只保留字母数字下划线横线，自动补 .md
    filename = re.sub(r"[^\w\-]", "_", filename)
    if not filename.endswith(".md"):
        filename += ".md"

    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"文件已保存：{path}"


def web_fetch(url: str) -> str:
    """
    抓取指定网页的正文文本（简单去除 HTML 标签）
    """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.encoding = resp.apparent_encoding
        text = resp.text
        # 极简去标签：去掉 script/style 内容和 HTML 标签
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:1500] if text else "页面内容为空"
    except Exception as e:
        return f"网页抓取失败：{e}"


# ---------------------------------------------------------------
# 注册表：把工具"介绍"给 LLM
# ---------------------------------------------------------------

TOOLS = [
    {
        "name": "get_time",
        "description": "获取当前的日期和时间，无参数。",
        "parameters": {},  # 无参数
        "func": get_time,
    },
    {
        "name": "get_weather",
        "description": "查询指定城市的实时天气。参数：city（城市名，如 '西安'、'北京'，可省略默认西安）。",
        "parameters": {"city": "城市名，例如 西安"},
        "func": get_weather,
    },
    {
        "name": "write_markdown",
        "description": "把内容保存为 Markdown 文件（存到 output 目录）。参数：content（要保存的内容）、filename（文件名，不含 .md 也可）。",
        "parameters": {"content": "要写入文件的内容", "filename": "文件名，例如 今日报告"},
        "func": write_markdown,
    },
    {
        "name": "web_fetch",
        "description": "抓取一个网页并返回正文文本。参数：url（网页链接，必须以 http/https 开头）。",
        "parameters": {"url": "完整的网页链接"},
        "func": web_fetch,
    },
]


def run_tool(name: str, args: dict) -> str:
    """根据工具名执行对应的函数，返回观察结果（给 Agent 看的）"""
    for tool in TOOLS:
        if tool["name"] == name:
            try:
                result = tool["func"](**args)
                return f"工具 {name} 执行成功：{result}"
            except TypeError as e:
                return f"工具 {name} 参数错误：{e}，请检查参数名"
            except Exception as e:
                return f"工具 {name} 执行失败：{e}"
    return f"没有找到工具 {name}"


def tools_description() -> str:
    """生成一段给 LLM 看的工具清单文本"""
    lines = []
    for t in TOOLS:
        params = ", ".join(f"{k}={v}" for k, v in t["parameters"].items()) or "无参数"
        lines.append(f"- {t['name']}({params})：{t['description']}")
    return "\n".join(lines)
