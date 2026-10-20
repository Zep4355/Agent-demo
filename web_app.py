# -*- coding: utf-8 -*-
"""
web_app.py - 一句话 Agent 的网页版界面（Streamlit）

比命令行版好看一百倍：有输入框、按钮、工作日志面板、文件下载。
运行方式：
    streamlit run web_app.py

技术：Streamlit（Python 写网页应用的最简方案，AI 应用开发主流工具）
"""
import io
import os
import contextlib

import streamlit as st

from agent import Agent

# ---------------------------------------------------------------
# 页面基础设置
# ---------------------------------------------------------------
st.set_page_config(page_title="一句话 Agent", page_icon="🤖", layout="centered")

st.title("🤖 一句话 Agent")
st.caption("输入一句话，Agent 自己拆任务、调工具、出成果 —— 你只管提需求")

# ---------------------------------------------------------------
# 访问密码（可选，防止陌生人消耗你的 API key）
# 配置方式：
#   - 本地：在 .env 里加一行 ACCESS_PASSWORD=你的密码
#   - 云端：在 Streamlit Secrets 里加 ACCESS_PASSWORD = "你的密码"
# 留空 = 不设密码，任何人都能用
# ---------------------------------------------------------------
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "")

if ACCESS_PASSWORD:
    pwd = st.text_input("🔒 访问密码", type="password", placeholder="请输入访问密码")
    if not pwd:
        st.info("此应用受密码保护，请输入密码后使用")
        st.stop()
    if pwd != ACCESS_PASSWORD:
        st.error("密码错误，拒绝访问")
        st.stop()


# ---------------------------------------------------------------
# 用户输入区
# ---------------------------------------------------------------
user_input = st.text_input(
    "👉 你的指令",
    placeholder="试试：查一下西安今天的天气，整理成报告保存",
    label_visibility="visible",
)

examples = ["查一下西安今天的天气，整理成报告保存",
            "现在几点了？顺便记下来",
            "抓取 https://example.com 的内容，总结一下保存"]
cols = st.columns(3)
for i, ex in enumerate(examples):
    if cols[i].button(f"📌 {ex[:12]}…"):
        user_input = ex

run_clicked = st.button("🚀 让 Agent 干活", type="primary", use_container_width=True)


# ---------------------------------------------------------------
# 执行 Agent（捕获它的工作日志显示在网页上）
# ---------------------------------------------------------------
if run_clicked and user_input:
    agent = Agent()

    # 用一个缓冲把 Agent 的 print 日志"接住"，再显示到页面上
    log_buffer = io.StringIO()

    with st.status("🤖 Agent 正在干活，别眨眼...", expanded=True) as status:
        with contextlib.redirect_stdout(log_buffer):
            answer = agent.run(user_input)

        # 展示 Agent 的工作日志（思考→调工具→看结果）
        st.markdown("### 📜 Agent 工作日志")
        st.code(log_buffer.getvalue(), language=None)
        status.update(label="✅ Agent 干完活了！", state="complete")

    # 展示最终结果
    st.markdown("### ✅ 最终结果")
    st.success(answer)

    # 展示生成的文件（如果有），并支持下载
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if os.path.isdir(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
        if files:
            st.markdown("### 📁 生成的报告文件")
            for f in files:
                path = os.path.join(output_dir, f)
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                st.download_button(
                    label=f"⬇️ 下载 {f}",
                    data=content,
                    file_name=f,
                    mime="text/markdown",
                )
else:
    st.info("👆 输入一句指令，然后点「让 Agent 干活」")

st.markdown("---")
st.caption("项目文档见《一句话Agent项目方案.md》｜ 由 崽崽 Agent 协助 Zephyr 开发")
