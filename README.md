# NictichuCLI

<div align="center">

**Agente de código multi-modelo con MCPs y Gemma**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Paleta de colores: Cian/Turquesa (#06B6D4)**

</div>

---

## Instalación Rápida

```powershell
# 1. Clonar (ya hecho)
cd C:\Users\Worsktation 2029\Documents\GitHub\nictichu-cli

# 2. Activar entorno virtual
.\venv\Scripts\activate

# 3. Instalar (ya hecho)
pip install -e .

# 4. Ejecutar
python -m src.main interactive
```

## Ejecución Fácil

### Windows

Doble click en `run.bat` o:

```powershell
.\run.bat
```

### Comandos Disponibles

```powershell
# Ver ayuda
python -m src.main --help

# Ver versión
python -m src.main version

# Iniciar CLI interactivo
python -m src.main interactive

# Con modelo específico
python -m src.main interactive --model gemma:7b --provider ollama
```

## Características

- **Multi-modelo**: Ollama, Google AI Studio, Vertex AI
- **MCPs**: Filesystem, Shell, Memory, Web Search
- **CLI Interactivo**: Rich + Prompt Toolkit
- **Paleta de colores**: Cian (#06B6D4)

## Configuración

Edita `.env` con tus API keys:

```bash
# Ollama (local - gratuito)
OLLAMA_BASE_URL=http://localhost:11434

# Google AI Studio
GOOGLE_AI_API_KEY=tu_api_key

# Vertex AI
GOOGLE_CLOUD_PROJECT=tu_proyecto_id
```

## Documentación

- **[QUICKSTART.md](QUICKSTART.md)** - Inicio rápido
- **[DEVGUIDE.md](DEVGUIDE.md)** - Guía de desarrollo
- **[INSTALL.md](INSTALL.md)** - Instalación detallada

## Estructura

```
nictichu-cli/
├── src/          # Código fuente
│   ├── core/     # Núcleo del agente
│   ├── models/   # Proveedores de modelos
│   ├── mcps/     # Servidores MCP
│   ├── tools/    # Herramientas
│   ├── cli/      # Interfaz CLI
│   └── utils/    # Utilidades
├── config/       # Configuración
├── tests/        # Tests
└── examples/     # Ejemplos
```

## Desarrollo

```powershell
# Activar entorno
.\venv\Scripts\activate

# Ejecutar tests
python -m pytest tests/ -v

# Formatear código
# pip install black (si no está instalado)
# black src/

# Type checking
# pip install mypy (si no está instalado)
# mypy src/
```

## Siguientes Pasos

1.	Configurar `.env` con tus API keys
2.	Ejecutar `.\run.bat` o `python -m src.main interactive`
3.	Empezar a desarrollar

## Licencia

MIT License - ver [LICENSE](LICENSE)

---

<div align="center">

**Hecho con `#06B6D4` en todo el mundo**

</div>
