@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title NictichuCLI - Instalador

echo.
echo  ========================================
echo  ^|    NictichuCLI - Instalador           ^|
echo  ^|    1 clic = todo listo                ^|
echo  ========================================
echo.

:: Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo Descargalo de: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python -c "import sys; print(sys.version_info[:2])"') do set PYVER=%%v
echo [OK] Python detectado: %PYVER%

:: Verificar Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no esta instalado.
    echo Descargalo de: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo [OK] Git detectado

:: Directorio del script (sin barra final)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Detectar si ya estamos dentro del repo (hay pyproject.toml)
if exist "%SCRIPT_DIR%\pyproject.toml" (
    set "INSTALL_DIR=%SCRIPT_DIR%"
    echo [OK] Instalacion dentro del repositorio existente
    goto :install_deps
)

:: Directorio de destino
set "INSTALL_DIR=%SCRIPT_DIR%\nictichu-cli"

:: Si ya existe, actualizar
if exist "%INSTALL_DIR%\.git" (
    echo.
    echo [!] Instalacion previa encontrada. Actualizando...
    cd /d "%INSTALL_DIR%"
    git pull
    goto :install_deps
)

:: Clonar repo
echo.
echo [1/5] Descargando NictichuCLI...
git clone https://github.com/alexandervi1/nictichu-cli.git "%INSTALL_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo clonar el repositorio.
    echo Verifica tu conexion a internet.
    pause
    exit /b 1
)
echo [OK] Repositorio clonado

:install_deps
cd /d "%INSTALL_DIR%"

:: Crear entorno virtual
echo.
echo [2/5] Creando entorno virtual...
if exist venv (
    echo [OK] Entorno virtual ya existe
) else (
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)

:: Activar venv
call venv\Scripts\activate.bat

:: Instalar dependencias
echo.
echo [3/5] Instalando dependencias (puede tardar un minuto)...
python -m pip install --upgrade pip >nul 2>&1
pip install -e . 2>nul
if !errorlevel! neq 0 (
    echo [!] Intentando con requirements.txt...
    pip install -r requirements.txt 2>nul
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudieron instalar las dependencias.
        echo Intenta ejecutar manualmente: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo [OK] Dependencias instaladas

:: Crear .env si no existe
echo.
echo [4/5] Configurando...
if not exist .env (
    copy .env.example .env >nul
    echo [OK] Archivo .env creado
    echo.
    echo     *** IMPORTANTE: Edita .env con tus API keys ***
    echo     Archivo: %INSTALL_DIR%\.env
    echo.
) else (
    echo [OK] Archivo .env ya existe
)

:: Crear acceso directo en escritorio
echo.
echo [5/5] Creando acceso directo...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\NictichuCLI.lnk"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\run.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'NictichuCLI'; $s.Save()" >nul 2>&1
echo [OK] Listo

echo.
echo  ========================================
echo  ^|    Instalacion completada!            ^|
echo  ========================================
echo.
echo  Para ejecutar:
echo    - Doble clic en: run.bat
echo    - O desde el escritorio: NictichuCLI.lnk
echo    - O manualmente:
echo        cd /d "%INSTALL_DIR%"
echo        venv\Scripts\activate
echo        python -m src.main interactive
echo.
pause