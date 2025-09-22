@echo off
cd /d %~dp0
REM 激活名为 automation_env 的虚拟环境
call .\automation_env\Scripts\activate

REM 如果没有参数，默认运行 quick_test.py；否则运行传入的脚本
if "%~1"=="" (
    python quick_test.py
) else (
    python %~1
)

pause
