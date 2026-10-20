@echo off
rem 一键启动「一句话 Agent」网页版
rem 双击本文件即可，无需手动输入命令
cd /d %~dp0
python -m streamlit run web_app.py
pause
