@echo off
echo Activando entorno virtual...
call venv\Scripts\activate
echo.
echo Ejecutando NictichuCLI...
python -m src.main interactive
pause
