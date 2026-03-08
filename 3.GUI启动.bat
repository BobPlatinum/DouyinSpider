@echo off
chcp 65001 >nul
title 抖音爬虫 GUI
cd /d "%~dp0"
echo 正在启动 GUI 界面...

:: 优先使用 Conda Spider 环境
where conda >nul 2>&1
if %errorlevel% == 0 (
    call conda activate Spider 2>nul
    python src\gui.py
    goto end
)

:: 备用：使用项目自带 Python
if exist python\python.exe (
    python\python.exe src\gui.py
    goto end
)

:: 最后备用：系统 Python
python src\gui.py

:end
pause

