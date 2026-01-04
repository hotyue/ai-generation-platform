@echo off
setlocal

REM ================================
REM ComfyUI 事实事件推送配置
REM ================================

set PLATFORM_EVENT_ENDPOINT=http://192.168.164.23:9001/internal/comfy/event
set COMPUTE_NODE=win-comfyui-01

REM ===== 调试用（可保留）=====
echo PLATFORM_EVENT_ENDPOINT=%PLATFORM_EVENT_ENDPOINT%
echo COMPUTE_NODE=%COMPUTE_NODE%
echo.

REM ================================
REM 启动 ComfyUI
REM ================================

.\python_embeded\python.exe -s ComfyUI\main.py --port 8188 --windows-standalone-build

echo.
echo If you see this and ComfyUI did not start try updating your Nvidia Drivers to the latest.
pause
