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
echo [1/7] Descargando NictichuCLI...
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
echo [2/7] Creando entorno virtual...
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
echo [3/7] Instalando dependencias (puede tardar un minuto)...
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
echo [4/7] Configurando...
if not exist .env (
    copy .env.example .env >nul
    echo [OK] Archivo .env creado
) else (
    echo [OK] Archivo .env ya existe
)

:: Instalar Ollama
echo.
echo [5/7] Instalando Ollama...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama ya esta instalado
) else (
    echo     Descargando Ollama...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'" 2>nul
    if exist "%TEMP%\OllamaSetup.exe" (
        echo     Instalando Ollama (puede pedir permisos)...
        start /wait "" "%TEMP%\OllamaSetup.exe" /S
        del "%TEMP%\OllamaSetup.exe" >nul 2>&1
        
        :: Agregar Ollama al PATH para esta sesion
        set "OLLAMA_PATH=%LOCALAPPDATA%\Programs\Ollama"
        if exist "%OLLAMA_PATH%" (
            set "PATH=%PATH%;%OLLAMA_PATH%"
        )
        if exist "C:\Program Files\Ollama" (
            set "PATH=%PATH%;C:\Program Files\Ollama"
        )
        
        where ollama >nul 2>&1
        if !errorlevel! equ 0 (
            echo [OK] Ollama instalado correctamente
        ) else (
            echo [!] Ollama instalado pero no esta en PATH.
            echo     Reinicia la terminal y ejecuta install.bat de nuevo.
            echo     O descargalo manualmente de: https://ollama.com/download
        )
    ) else (
        echo [!] No se pudo descargar Ollama automaticamente.
        echo     Descargalo manualmente de: https://ollama.com/download
        echo     Luego ejecuta: ollama pull gemma4:e2b
    )
)

:: Descargar modelo gemma4:e2b
echo.
echo [6/7] Descargando modelo gemma4:e2b (7.2 GB, puede tardar)...

:: Asegurarse de que Ollama este corriendo
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    :: Iniciar Ollama en background si no esta corriendo
    ollama list >nul 2>&1
    if !errorlevel! neq 0 (
        echo     Iniciando Ollama...
        start "" /B ollama serve >nul 2>&1
        timeout /t 5 /nobreak >nul
    )
    
    :: Verificar si el modelo ya existe
    ollama list 2>nul | findstr /i "gemma4" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Modelo gemma4:e2b ya esta descargado
    ) else (
        echo     Descargando... (esto puede tardar varios minutos)
        ollama pull gemma4:e2b
        if !errorlevel! equ 0 (
            echo [OK] Modelo gemma4:e2b descargado correctamente
        ) else (
            echo [!] No se pudo descargar el modelo automaticamente.
            echo     Ejecuta manualmente: ollama pull gemma4:e2b
            echo     O usa Google AI sin instalar nada:
            echo       1. Obtén tu API key GRATIS en: https://aistudio.google.com/apikey
            echo       2. Edita el archivo .env y agrega: GOOGLE_AI_API_KEY=tu_key
            echo       3. Ejecuta: python -m src.main interactive -p google_ai -m gemini-2.0-flash
        )
    )
) else (
    echo [!] Ollama no disponible. Descargalo de https://ollama.com/download
    echo     Luego ejecuta: ollama pull gemma4:e2b
    echo.
    echo     Alternativa sin instalar nada (GRATIS):
    echo       1. Obtén tu API key en: https://aistudio.google.com/apikey
    echo       2. Edita el archivo .env y agrega: GOOGLE_AI_API_KEY=tu_key
    echo       3. Ejecuta: python -m src.main interactive -p google_ai -m gemini-2.0-flash
)

:: Crear acceso directo en escritorio
echo.
echo [7/7] Creando acceso directo...
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
echo  Configuracion del modelo:
echo    - Local (Ollama):     ya descargado gemma4:e2b
echo    - Cloud (GRATIS):     editar .env con GOOGLE_AI_API_KEY
echo                          y usar -p google_ai -m gemini-2.0-flash
echo.
pause