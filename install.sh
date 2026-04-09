#!/usr/bin/env bash
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "  ${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "  ${CYAN}║     NictichuCLI - Instalador          ║${NC}"
echo -e "  ${CYAN}║     1 clic = todo listo              ║${NC}"
echo -e "  ${CYAN}╚═══════════════════════════════════════╝${NC}"
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
INSTALL_DIR="$SCRIPT_DIR/nictichu-cli"

if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo -e "${YELLOW}[!]${NC} Se encontro una instalacion previa en $INSTALL_DIR"
    echo "    1) Reinstalar (borrar e instalar de nuevo)"
    echo "    2) Actualizar (git pull + reinstalar deps)"
    echo "    3) Cancelar"
    echo ""
    read -p "Selecciona una opcion [1-3]: " choice
    case $choice in
        3) exit 0 ;;
        2)
            echo -e "${GREEN}[+]${NC} Actualizando..."
            cd "$INSTALL_DIR"
            git pull
            ;;
        1)
            echo -e "${GREEN}[+]${NC} Eliminando instalacion previa..."
            rm -rf "$INSTALL_DIR"
            ;;
    esac
fi

# Clonar repo
if [ ! -d "$INSTALL_DIR" ]; then
    echo ""
    echo -e "${CYAN}[1/5]${NC} Descargando NictichuCLI..."
    git clone https://github.com/alexandervi1/nictichu-cli.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Crear entorno virtual
echo ""
echo -e "${CYAN}[2/5]${NC} Creando entorno virtual..."
if [ -d "venv" ]; then
    echo -e "${GREEN}[OK]${NC} Entorno virtual ya existe"
else
    $PYTHON -m venv venv
    echo -e "${GREEN}[OK]${NC} Entorno virtual creado"
fi

# Activar venv
source venv/bin/activate

# Instalar dependencias
echo ""
echo -e "${CYAN}[3/5]${NC} Instalando dependencias..."
pip install --upgrade pip --quiet
if ! pip install -e . --quiet 2>/dev/null; then
    echo -e "${YELLOW}[!]${NC} Instalacion con pip install -e fallo, intentando con requirements.txt..."
    pip install -r requirements.txt --quiet
fi

# Crear .env si no existe
echo ""
echo -e "${CYAN}[4/5]${NC} Configurando..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Archivo .env creado"
    echo ""
    echo -e "    ${YELLOW}*** IMPORTANTE: Edita el archivo .env con tus API keys ***${NC}"
    echo -e "    Ubicacion: $INSTALL_DIR/.env"
    echo ""
else
    echo -e "${GREEN}[OK]${NC} Archivo .env ya existe"
fi

# Crear alias
echo ""
echo -e "${CYAN}[5/5]${NC} Creando comando de acceso rapido..."

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
echo -e "  ${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "  ${GREEN}║     Instalacion completada! ^_^        ║${NC}"
echo -e "  ${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo "  Para ejecutar NictichuCLI:"
echo "    - Comando rapido (recargar shell primero): nictichu"
echo "    - Manualmente:"
echo "        cd $INSTALL_DIR"
echo "        source venv/bin/activate"
echo "        python -m src.main interactive"
echo ""
echo "  Para configurar API keys, edita: .env"
echo ""