# Inicio Rápido - NictichuCLI

## Instalación en 3 Pasos

```powershell
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Instalar (ya hecho)
pip install -e .

# 3. Ejecutar
python -m src.main interactive
```

## Comandos Útiles

```powershell
# Verificar instalación
python -c "from src import __version__; print(f'NictichuCLI {__version__}')"

# Ejecutar con Ollama
python -m src.main interactive --model gemma4:e2b --provider ollama

# Ejecutar tests
python -m pytest tests/ -v
```

## Estructura del Proyecto

```
nictichu-cli/
├── src/          # Código fuente
│   ├── core/     # Núcleo del agente
│   ├── models/   # Proveedores de modelos
│   ├── mcps/     # Servidores MCP
│   ├── tools/    # Herramientas de código
│   ├── cli/      # Interfaz CLI
│   └── utils/    # Utilidades
├── config/       # Configuración
├── tests/        # Tests
└── examples/     # Ejemplos
```

## Siguiente

- Configurar `.env` con tus API keys
- Leer [INSTALL.md](INSTALL.md) para más detalles
- Ver [README.md](README.md) para documentación completa
