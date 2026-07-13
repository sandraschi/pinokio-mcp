@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "D:\Dev\repos\pinokio-mcp\web_sota\start.ps1"
echo.
echo === exited %ERRORLEVEL% ===
pause