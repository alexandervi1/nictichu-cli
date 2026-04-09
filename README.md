# NictichuCLI

<div align="center">

**Agente de código multi-modelo con MCPs, herramientas de desarrollo y streaming**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 94 passing](https://img.shields.io/badge/tests-94_passing-brightgreen.svg)]()

**Paleta de colores: Cian/Turquesa (#06B6D4)**

</div>

---

## Instalación Rápida (1 clic)

### Windows
```
Doble clic en install.bat
```
Esto descarga, instala todo, configura el .env y crea un acceso directo en el escritorio.

### Linux / Mac
```bash
chmod +x install.sh && ./install.sh
```
Esto descarga, instala todo y agrega el comando `nictichu` al shell.

### Ejecutar después de instalar
- **Windows**: Doble clic en `run.bat` (o el acceso directo del escritorio)
- **Linux/Mac**: Escribe `nictichu` en la terminal

### Opción A: Google AI (gratis, sin instalación)

```bash
# 1. Obtén tu API key GRATIS en: https://aistudio.google.com/apikey
# 2. Configura tu .env
echo GOOGLE_AI_API_KEY=tu_api_key_aqui > .env

# 3. Ejecuta
python -m src.main interactive -p google_ai -m gemini-2.0-flash
```

### Opción B: Ollama (local, gratuito, requiere PC con 8GB+ RAM)

```bash
# 1. Instala Ollama desde https://ollama.com
# 2. Descarga un modelo
ollama pull gemma4:e2b

# 3. Ejecuta
python -m src.main interactive
```

### Ejecución con modelo específico
```bash
# Google AI (recomendado, gratis y sin instalación)
python -m src.main interactive -p google_ai -m gemini-2.0-flash

# Ollama (local)
python -m src.main interactive -p ollama -m gemma4:e2b

# Vertex AI (Google Cloud)
python -m src.main interactive -p vertex_ai -m gemini-pro
```

## Características Principales

### Multi-Modelo
| Proveedor | Modelos | Costo | Estado |
|-----------|---------|-------|--------|
| **Ollama** | gemma4:e2b, llama3, mistral, codellama | Gratuito (local) | ✅ |
| **Google AI** | gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro | Gratuito (cloud) | ✅ |
| **Vertex AI** | Gemini en Google Cloud | De pago | ✅ |

### MCPs (Model Context Protocol)
| Servidor | Funcionalidades |
|----------|----------------|
| **Filesystem** | Leer/escribir archivos, listar directorios, buscar |
| **Shell** | Ejecutar comandos de terminal |
| **Memory** | Memoria conversacional persistente |
| **Search** | Búsqueda web y en código |

### Herramientas de Código
| Herramienta | Funcionalidades |
|-------------|----------------|
| **Editor** | Leer/editar archivos, búsqueda y reemplazo |
| **Reviewer** | Análisis de código, detección de bugs, seguridad |
| **Tester** | Ejecutar tests, coverage, linting |
| **Docs** | Generar documentación automática |

### CLI Interactivo
- **Rich UI**: Tablas, paneles, syntax highlighting
- **Prompt Toolkit**: Auto-completado, historial, edición multilínea
- **Comandos especiales**: `/help`, `/tools`, `/mcps`, `/model`, `/status`, `/clear`, `/exit`
- **Streaming**: Respuestas en tiempo real
- **Contexto**: Historial de conversación con límite de tokens

## Comandos CLI

```powershell
# Ver ayuda
python -m src.main --help

# Ver versión
python -m src.main version

# Iniciar CLI interactivo
python -m src.main interactive

# Con modelo específico
python -m src.main interactive --model gemma4:e2b --provider ollama

# Con Google AI Studio
python -m src.main interactive --model gemini-pro --provider google

# Con Vertex AI
python -m src.main interactive --model gemini --provider vertex
```

### Comandos Interactivos

| Comando | Descripción |
|---------|-------------|
| `/help` | Muestra ayuda |
| `/tools` | Lista herramientas disponibles |
| `/mcps` | Lista servidores MCP |
| `/model <nombre>` | Cambia el modelo actual |
| `/status` | Muestra estado del agente |
| `/clear` | Limpia contexto |
| `/exit` | Sale del CLI |

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Ollama (local - gratuito)
OLLAMA_BASE_URL=http://localhost:11434

# Google AI Studio
GOOGLE_AI_API_KEY=tu_api_key_aqui

# Vertex AI
GOOGLE_CLOUD_PROJECT=tu_proyecto_id
GOOGLE_CLOUD_LOCATION=us-central1
```

## Estructura del Proyecto

```
nictichu-cli/
├── src/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada
│   ├── core/
│   │   ├── __init__.py
│   │   ├── context.py           # Gestión de contexto
│   │   └── core.py              # Núcleo del agente
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Clase base
│   │   ├── registry.py          # Registro de modelos
│   │   ├── ollama.py            # Proveedor Ollama
│   │   ├── google_ai.py         # Proveedor Google AI
│   │   └── vertex_ai.py         # Proveedor Vertex AI
│   ├── mcps/
│   │   ├── __init__.py
│   │   ├── client.py            # Cliente base
│   │   ├── manager.py           # Gestor MCP
│   │   └── servers/
│   │       ├── __init__.py
│   │       ├── filesystem.py    # MCP Filesystem
│   │       ├── shell.py         # MCP Shell
│   │       ├── memory.py        # MCP Memory
│   │       └── search.py        # MCP Search
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── editor.py            # Editor de código
│   │   ├── reviewer.py          # Reviewer de código
│   │   ├── tester.py            # Runner de tests
│   │   └── docs.py              # Generador de docs
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── interface.py          # CLI principal
│   │   ├── conversation.py      # Loop de conversación
│   │   └── commands.py          # Manejador de comandos
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuración
│   │   └── logger.py            # Logger
│   ├── plugins/                  # TODO: Sistema de plugins
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── registry.py
│   └── storage/                  # TODO: Persistencia SQLite
│       ├── __init__.py
│       ├── database.py
│       └── models.py
├── config/
│   ├── settings.yaml            # Configuración general
│   └── models.yaml              # Configuración de modelos
├── tests/                       # Suite de tests
├── pyproject.toml               # Configuración del proyecto
├── requirements.txt             # Dependencias
├── pytest.ini                  # Configuración de pytest
├── Makefile                     # Comandos make
└── run.bat                      # Script de ejecución
```

## Desarrollo

```powershell
# Activar entorno
.\venv\Scripts\activate

# Ejecutar tests
python -m pytest tests/ -v

# Ejecutar tests con coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Formatear código
black src/

# Type checking
mypy src/
```

## Dependencias Principales

```
pydantic>=2.0          # Validación de datos
rich>=13.0             # UI enriquecida
prompt_toolkit>=3.0    # CLI interactivo
typer>=0.9             # Framework CLI
httpx>=0.25            # Cliente HTTP asíncrono
aiosqlite>=0.19        # SQLite asíncrono
loguru>=0.7            # Logging
pytest>=7.0            # Testing
```

## Documentación

| Documento | Descripción |
|-----------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Inicio rápido |
| **[DEVGUIDE.md](DEVGUIDE.md)** | Guía de desarrollo |
| **[INSTALL.md](INSTALL.md)** | Instalación detallada |
| **[TEST_REPORT.md](TEST_REPORT.md)** | Reporte de tests |
| **[CHANGELOG.md](CHANGELOG.md)** | Historial de cambios |

## Estado del Proyecto

### Completado ✅
- [x] Estructura del proyecto
- [x] Core del agente (ContextManager, NictichuCore)
- [x] Registro de modelos (ModelRegistry)
- [x] Tres proveedores de modelos (Ollama, Google AI, Vertex AI)
- [x] Cuatro servidores MCP (Filesystem, Shell, Memory, Search)
- [x] Cuatro herramientas de código (Editor, Reviewer, Tester, Docs)
- [x] CLI interactivo con Rich y Prompt Toolkit
- [x] Sistema de comandos especiales
- [x] Integración de tool calling
- [x] Streaming de respuestas
- [x] Suite de tests (94 tests pasando)

### En Progreso 🚧
- [ ] Sistema de plugins extensible
- [ ] Persistencia con SQLite
- [ ] Mejoras en visualizaciones Rich

### Planeado 📋
- [ ] Interfaz web (FastAPI)
- [ ] Soporte para más modelos (Claude, GPT-4)
- [ ] Integración con IDEs
- [ ] Async/await completo

## Ejecución Rápida

### Windows
```powershell
.\run.bat
```

O manualmente:
```powershell
.\venv\Scripts\activate
python -m src.main interactive
```

## Ejemplo de Uso

```
nichtichu> /help
Comandos disponibles:
  /help     - Muestra esta ayuda
  /tools    - Lista herramientas disponibles
  /mcps     - Lista servidores MCP
  /model    - Cambia el modelo actual
  /status   - Muestra estado del agente
  /clear    - Limpia contexto
  /exit     - Sale del CLI

nichtichu> /tools
Herramientas disponibles:
  - editor: Leer y editar archivos
  - reviewer: Analizar código
  - tester: Ejecutar tests
  - docs: Generar documentación

nichtichu> /model gemini-pro
Modelo cambiado a: gemini-pro

nichtichu> Lee el archivo src/main.py y explícame qué hace
[Streaming response...]
```

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:

- Reportar bugs
- Solicitar features
- Enviar pull requests
- Guía de estilo de código

## Licencia

MIT License - ver [LICENSE](LICENSE)

---

<div align="center">

**Hecho con `#06B6D4` en todo el mundo**

[GitHub](https://github.com/alexandervi1/nictichu-cli) | [Issues](https://github.com/alexandervi1/nictichu-cli/issues)

</div>