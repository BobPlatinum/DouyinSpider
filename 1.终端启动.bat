@echo off
cd /d "%~dp0"

:: 1. 尝试使用 Conda 环境
where conda >nul 2>&1
if %errorlevel% == 0 (
    call conda activate Spider 2>nul
    if %errorlevel% == 0 (
        python src\main.py
        goto end
    )
)

:: 2. 尝试使用便携式 Python
if exist python\python.exe (
    python\python.exe src\main.py
    goto end
)

:: 3. 尝试使用系统 Python
python src\main.py

:end
pause
