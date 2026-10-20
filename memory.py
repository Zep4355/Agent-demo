# -*- coding: utf-8 -*-
"""
memory.py - 持久记忆模块（让 Agent 跨对话记住重要信息）

原理：
    Agent 把用户透露的重要信息（名字、偏好、常用地点等）存进 memory.json
    下次启动时自动读取，作为"长期记忆"的背景，让 Agent 越来越懂用户。

提供功能：
    load_memory()    读取全部记忆          -> 返回列表
    add_memory()     新增一条记忆
    clear_memory()   清空记忆
    memory_context() 把记忆拼成一段给 Agent 看的背景文字
"""
import json
import os
import datetime

# 记忆文件保存在项目目录下
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
# 记忆条数上限（防止无限增长）
MAX_MEMORY = 50


def load_memory() -> list:
    """读取记忆文件，返回记忆列表。文件不存在或损坏时返回空列表。"""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_memory(items: list) -> None:
    """把记忆列表写回文件"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_memory(content: str) -> list:
    """新增一条记忆（自动去重、自动加时间戳、限制条数）"""
    items = load_memory()

    # 去重：同样内容不重复存
    for it in items:
        if it.get("content") == content:
            return items

    items.append({
        "id": len(items) + 1,
        "content": content,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    # 超出上限就只保留最新的 MAX_MEMORY 条
    if len(items) > MAX_MEMORY:
        items = items[-MAX_MEMORY:]

    save_memory(items)
    return items


def clear_memory() -> None:
    """清空所有记忆"""
    save_memory([])


def memory_context() -> str:
    """把记忆拼成一段给 Agent 看的背景文字（没有记忆时返回空串）"""
    items = load_memory()
    if not items:
        return ""
    lines = [f"- 记住#{it['id']}: {it['content']}（记录于 {it['time']}）" for it in items]
    return "你长期记住的用户信息：\n" + "\n".join(lines)