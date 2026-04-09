#!/usr/bin/env bash
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "  ${CYAN}========================================${NC}"
echo -e "  ${CYAN}|    NictichuCLI - Instalador           |${NC}"
echo -e "  ${CYAN}|    1 clic = todo listo                |${NC}"
echo -e "  ${CYAN}========================================${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}[ERROR] Python no esta instalado.${NC}"
        echo "Instalalo con: sudo apt install python3 python3-venv python3-pip"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

PYVER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}[OK]${NC} Python detectado: $PYVER"

# Verificar Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}[ERROR] Git no esta instalado.${NC}"
    echo "Instalalo con: sudo apt install git"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Git detectado"

# Directorio de instalacion
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detectar si ya estamos dentro del repo
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    INSTALL_DIR="$SCRIPT_DIR"
    echo -e "${GREEN}[OK]${NC} Instalacion dentro del repositorio existente"
else
    INSTALL_DIR="$SCRIPT_DIR/nictichu-cli"

    if [ -d "$INSTALL_DIR" ]; then
        echo ""
        echo -e "${YELLOW}[!]${NC} Instalacion previa encontrada. Actualizando..."
        cd "$INSTALL_DIR"
        git pull
    else
        echo ""
        echo -e "${CYAN}[1/7]${NC} Descargando NictichuCLI..."
        git clone https://github.com/alexandervi1/nictichu-cli.git "$INSTALL_DIR"
    fi
fi

cd "$INSTALL_DIR"

# Crear entorno virtual
echo ""
echo -e "${CYAN}[2/7]${NC} Creando entorno virtual..."
if [ -d "venv" ]; then
    echo -e "${GREEN}[OK]${NC} Entorno virtual ya existe"
else
    $PYTHON -m venv venv
    echo -e "${GREEN}[OK]${NC} Entorno virtual creado"
fi

source venv/bin/activate

# Instalar dependencias
echo ""
echo -e "${CYAN}[3/7]${NC} Instalando dependencias..."
pip install --upgrade pip --quiet
if ! pip install -e . --quiet 2>/dev/null; then
    echo -e "${YELLOW}[!]${NC} Intentando con requirements.txt..."
    pip install -r requirements.txt --quiet
fi
echo -e "${GREEN}[OK]${NC} Dependencias instaladas"

# Crear .env si no existe
echo ""
echo -e "${CYAN}[4/7]${NC} Configurando..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Archivo .env creado"
else
    echo -e "${GREEN}[OK]${NC} Archivo .env ya existe"
fi

# Instalar Ollama
echo ""
echo -e "${CYAN}[5/7]${NC} Instalando Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Ollama ya esta instalado"
else
    echo "    Descargando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh 2>/dev/null
    
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} Ollama instalado correctamente"
    else
        echo -e "${YELLOW}[!]${NC} No se pudo instalar Ollama automaticamente."
        echo "    Instalalo manualmente desde: https://ollama.com/download"
        echo "    Luego ejecuta: ollama pull gemma4:e2b"
    fi
fi

# Descargar modelo
echo ""
echo -e "${CYAN}[6/7]${NC} Descargando modelo gemma4:e2b (7.2 GB)..."
if command -v ollama &> /dev/null; then
    # Iniciar Ollama si no esta corriendo
    if ! ollama list &> /dev/null; then
        echo "    Iniciando Ollama..."
        ollama serve &> /dev/null &
        sleep 3
    fi
    
    if ollama list 2>/dev/null | grep -q "gemma4"; then
        echo -e "${GREEN}[OK]${NC} Modelo gemma4:e2b ya esta descargado"
    else
        echo "    Descargando... (esto puede tardar varios minutos)"
        if ollama pull gemma4:e2b; then
            echo -e "${GREEN}[OK]${NC} Modelo gemma4:e2b descargado correctamente"
        else
            echo -e "${YELLOW}[!]${NC} No se pudo descargar el modelo."
            echo "    Ejecuta manualmente: ollama pull gemma4:e2b"
        fi
    fi
else
    echo -e "${YELLOW}[!]${NC} Ollama no disponible."
    echo "    Alternativa GRATIS sin instalar nada:"
    echo "      1. API key en: https://aistudio.google.com/apikey"
    echo "      2. Editar .env: GOOGLE_AI_API_KEY=tu_key"
    echo "      3. Ejecutar: nictichu (usa gemini-2.0-flash)"
fi

# Crear alias
echo ""
echo -e "${CYAN}[7/7]${NC} Creando comando de acceso rapido..."

SHELL_RC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

ALIAS_CMD="alias nictichu='cd $INSTALL_DIR && source venv/bin/activate && python -m src.main'"

if grep -q "alias nictichu=" "$SHELL_RC" 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Alias 'nictichu' ya existe en $SHELL_RC"
else
    echo "" >> "$SHELL_RC"
    echo "# NictichuCLI" >> "$SHELL_RC"
    echo "$ALIAS_CMD" >> "$SHELL_RC"
    echo -e "${GREEN}[OK]${NC} Alias 'nictichu' agregado a $SHELL_RC"
fi

echo ""
echo -e "  ${GREEN}========================================${NC}"
echo -e "  ${GREEN}|    Instalacion completada!            |${NC}"
echo -e "  ${GREEN}========================================${NC}"
echo ""
echo "  Para ejecutar:"
echo "    - Comando rapido (recargar shell primero): nictichu"
echo "    - Manualmente:"
echo "        cd $INSTALL_DIR"
echo "        source venv/bin/activate"
echo "        python -m src.main interactive"
echo ""
echo "  Configuracion del modelo:"
echo "    - Local (Ollama):     ya descargado gemma4:e2b"
echo "    - Cloud (GRATIS):     editar .env con GOOGLE_AI_API_KEY"
echo "                          y usar -p google_ai -m gemini-2.0-flash"
echo ""