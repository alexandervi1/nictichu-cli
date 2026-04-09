@echo off
chcp 65001 >nul 2>&1
title NictichuCLI

:: Buscar venv local, si no existe buscar globalmente
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
) else if exist "%~dp0nictichu-cli\venv\Scripts\activate.bat" (
    call "%~dp0nictichu-cli\venv\Scripts\activate.bat"
) else (
    echo [ERROR] No se encontro el entorno virtual.
    echo Ejecuta install.bat primero.
    pause
    exit /b 1
)

echo.
echo  NictichuCLI v0.1.0
echo  Escriba /help para ver los comandos disponibles.
echo  Escriba /quit para salir.
echo.

python -m src.main interactive
pause