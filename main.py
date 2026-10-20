# -*- coding: utf-8 -*-
"""
main.py - 入口：和 Agent 对话

运行：python main.py
输入一句指令，比如：
  - 查一下西安今天的天气，整理成报告保存
  - 现在几点了？顺便记下来
  - 抓取 https://www.baidu.com 的内容，总结一下保存
"""
from agent import Agent


def main():
    print("=" * 50)
    print("  一句话 Agent —— 输入一句话，它自己干活")
    print("=" * 50)
    print("示例：查一下西安今天的天气，整理成报告保存")
    print("输入 exit / quit 退出\n")

    agent = Agent()

    while True:
        try:
            user_input = input("👉 你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "退出"):
            print("再见！")
            break

        answer = agent.run(user_input)
        print(f"🤖 Agent：{answer}\n")


if __name__ == "__main__":
    main()
