# -*- coding: utf-8 -*-
"""
config.py - 配置管理（读取 API key 等）

支持两种方式：
1. 项目目录下放一个 .env 文件（推荐，不会把 key 泄露到代码里）
2. 直接设置系统环境变量
"""
import os
from dotenv import load_dotenv

# 加载项目目录下的 .env 文件（如果存在）
load_dotenv()

# DeepSeek API 配置（OpenAI 兼容格式）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Agent 最大思考轮数（防止死循环的兜底）
MAX_STEPS = int(os.getenv("MAX_STEPS", "5"))
