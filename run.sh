#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Buscar venv
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -f "$SCRIPT_DIR/nictichu-cli/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/nictichu-cli/venv/bin/activate"
else
    echo "[ERROR] No se encontro el entorno virtual."
    echo "Ejecuta install.sh primero."
    exit 1
fi

echo ""
echo "  NictichuCLI v0.1.0"
echo "  Escriba /help para ver los comandos disponibles."
echo "  Escriba /quit para salir."
echo ""

python -m src.main interactive