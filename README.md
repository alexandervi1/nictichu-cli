# NictichuCLI

<div align="center">

**Agente de código multi-modelo con MCPs, herramientas de desarrollo y streaming**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 94 passing](https://img.shields.io/badge/tests-94_passing-brightgreen.svg)]()

</div>

---

## Instalación Rápida (1 clic)

### Windows
```
Doble clic en install.bat
```
Instala Python, Git, Ollama, descarga el modelo `gemma4:e2b` y configura todo automáticamente.

### Linux / Mac
```bash
chmod +x install.sh && ./install.sh
```
Hace lo mismo y agrega el comando `nictichu` al shell.

### Ejecutar después de instalar
- **Windows**: Doble clic en `run.bat` o el acceso directo del escritorio
- **Linux/Mac**: Escribe `nictichu` en la terminal

---

## Proveedores de Modelo

NictichuCLI funciona con o sin Ollama. Elige el que prefieras:

### Opción 1: Ollama (local, gratuito, requiere 8GB+ RAM)

El instalador descarga Ollama y el modelo automáticamente. Si lo quieres hacer manual:

```bash
# Instalar Ollama: https://ollama.com/download
ollama pull gemma4:e2b          # 7.2 GB, corre en cualquier PC
ollama pull gemma4:e4b          # 9.6 GB, más preciso
ollama pull gemma4:26b          # 18 GB, requiere GPU buena

# Ejecutar
python -m src.main interactive
```

### Opción 2: Google AI (cloud, gratuito, sin instalar nada)

Funciona en cualquier PC sin Ollama. Solo necesitas una API key gratuita.

```bash
# 1. Obtén tu API key GRATIS en: https://aistudio.google.com/apikey
# 2. Agrega a .env:
echo GOOGLE_AI_API_KEY=tu_api_key >> .env
# 3. Ejecuta:
python -m src.main interactive -p google_ai -m gemini-2.0-flash
```

| Modelo | Tamaño | Precisión | Costo |
|--------|--------|-----------|-------|
| `gemma4:e2b` | 7.2 GB | Buena | Gratuito (local) |
| `gemma4:e4b` | 9.6 GB | Muy buena | Gratuito (local) |
| `gemini-2.0-flash` | Cloud | Muy buena | Gratuito (cloud) |
| `gemini-2.5-flash` | Cloud | Excelente | Gratuito (cloud) |
| `gemini-2.5-pro` | Cloud | Máxima | Gratuito (cloud) |

### Fallback automático

Si Ollama no está disponible y hay `GOOGLE_AI_API_KEY` en `.env`, la app **cambia automáticamente** a `google_ai/gemini-2.0-flash`.

---

## Comandos CLI

```bash
# Ver ayuda
python -m src.main --help

# Ver versión
python -m src.main version

# Iniciar CLI (usa proveedor por defecto)
python -m src.main interactive

# Ollama (local)
python -m src.main interactive -p ollama -m gemma4:e2b

# Google AI (cloud, gratuito)
python -m src.main interactive -p google_ai -m gemini-2.0-flash

# Vertex AI (Google Cloud)
python -m src.main interactive -p vertex_ai -m gemini-pro
```

### Comandos Interactivos

| Comando | Descripción |
|---------|-------------|
| `/help` | Muestra ayuda |
| `/tools` | Lista herramientas disponibles |
| `/mcps` | Lista servidores MCP |
| `/model <proveedor>/<modelo>` | Cambia el modelo actual |
| `/status` | Muestra estado del agente |
| `/clear` | Limpia contexto |
| `/save` | Guarda conversación |
| `/load` | Carga conversación |
| `/exit` | Sale del CLI |

---

## Características Principales

### Multi-Modelo
| Proveedor | Modelos | Costo | Estado |
|-----------|---------|-------|--------|
| **Ollama** | gemma4:e2b, gemma4:e4b, llama3, mistral, codellama | Gratuito (local) | ✅ |
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
- **Fallback automático**: Si Ollama no está, usa Google AI
- **Streaming**: Respuestas en tiempo real
- **Contexto**: Historial de conversación con límite de tokens

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```bash
# ============================================================
# PROVEEDORES DE MODELO (elige uno o varios)
# ============================================================

# --- Opción 1: Ollama (local, gratuito, requiere 8GB+ RAM) ---
# 1. Instala Ollama: https://ollama.com
# 2. Descarga un modelo: ollama pull gemma4:e2b
OLLAMA_BASE_URL=http://localhost:11434

# --- Opción 2: Google AI Studio (cloud, GRATUITO, sin instalar nada) ---
# 1. Obtén tu API key GRATIS en: https://aistudio.google.com/apikey
# 2. Pega tu key abajo
GOOGLE_AI_API_KEY=tu_api_key_aqui

# --- Opción 3: Vertex AI (cloud, requiere Google Cloud) ---
# GOOGLE_CLOUD_PROJECT=tu_proyecto_id
# GOOGLE_CLOUD_LOCATION=us-central1

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
LOG_LEVEL=INFO
```

---

## Estructura del Proyecto

```
nictichu-cli/
├── src/
│   ├── main.py                  # Punto de entrada
│   ├── core/
│   │   ├── context.py           # Gestión de contexto
│   │   └── core.py              # Núcleo del agente + fallback automático
│   ├── models/
│   │   ├── base.py              # Clase base
│   │   ├── registry.py          # Registro de modelos (auto-registra providers)
│   │   ├── ollama.py            # Proveedor Ollama
│   │   ├── google_ai.py         # Proveedor Google AI (HTTP directo, sin SDK)
│   │   └── vertex_ai.py         # Proveedor Vertex AI
│   ├── mcps/
│   │   ├── client.py            # Cliente base
│   │   ├── manager.py           # Gestor MCP (filesystem por defecto)
│   │   └── servers/
│   │       ├── filesystem.py    # MCP Filesystem
│   │       ├── shell.py         # MCP Shell
│   │       ├── memory.py        # MCP Memory
│   │       └── search.py        # MCP Search
│   ├── tools/
│   │   ├── editor.py            # Editor de código
│   │   ├── reviewer.py          # Reviewer de código
│   │   ├── tester.py            # Runner de tests (PytestRunner)
│   │   └── docs.py              # Generador de docs
│   ├── cli/
│   │   ├── interface.py         # CLI principal (banner + provider info)
│   │   ├── conversation.py      # Loop de conversación + tool dispatch
│   │   └── commands.py          # Manejador de comandos
│   └── utils/
│       ├── config.py            # Configuración (.env + YAML)
│       └── logger.py            # Logger
├── config/
│   └── settings.yaml            # Configuración general
├── tests/                        # 94 tests pasando
├── install.bat                   # Instalador Windows (1 clic)
├── install.sh                    # Instalador Linux/Mac (1 clic)
├── run.bat                       # Ejecutar en Windows
├── run.sh                        # Ejecutar en Linux/Mac
├── .env.example                  # Template de configuración
└── pyproject.toml                # Dependencias
```

---

## Ejemplo de Uso

```
[gemma4:e2b] > /help
Comandos disponibles:
  /help     - Muestra esta ayuda
  /tools    - Lista herramientas disponibles
  /mcps     - Lista servidores MCP
  /model    - Cambia el modelo actual
  /status   - Muestra estado del agente
  /clear    - Limpia contexto
  /save     - Guarda conversación
  /load     - Carga conversación
  /exit     - Sale del CLI

[gemma4:e2b] > /tools
Herramientas disponibles:
  - editor: Leer y editar archivos
  - reviewer: Analizar código
  - tester: Ejecutar tests
  - docs: Generar documentación

[gemma4:e2b] > /model google_ai/gemini-2.0-flash
Modelo cambiado a: google_ai/gemini-2.0-flash

[gemini-2.0-flash] > Lee el archivo src/main.py y explícame qué hace
[Streaming response...]
```

---

## Desarrollo

```bash
# Activar entorno
source venv/bin/activate   # Linux/Mac
.\venv\Scripts\activate    # Windows

# Ejecutar tests
python -m pytest tests/ -v

# Ejecutar tests con coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Formatear código
black src/

# Type checking
mypy src/
```

---

## Estado del Proyecto

### Completado ✅
- [x] Estructura del proyecto
- [x] Core del agente (ContextManager, NictichuCore)
- [x] Registro de modelos con auto-registro de providers
- [x] Tres proveedores (Ollama, Google AI, Vertex AI)
- [x] Fallback automático Ollama → Google AI
- [x] Google AI via HTTP directo (sin SDK)
- [x] Cuatro servidores MCP (Filesystem, Shell, Memory, Search)
- [x] Cuatro herramientas de código (Editor, Reviewer, Tester, Docs)
- [x] CLI interactivo con Rich y Prompt Toolkit
- [x] Instalador 1-clic (Ollama + modelo incluido)
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

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Inicio rápido |
| **[DEVGUIDE.md](DEVGUIDE.md)** | Guía de desarrollo |
| **[INSTALL.md](INSTALL.md)** | Instalación detallada |
| **[TEST_REPORT.md](TEST_REPORT.md)** | Reporte de tests |
| **[CHANGELOG.md](CHANGELOG.md)** | Historial de cambios |

---

## Licencia

MIT License - ver [LICENSE](LICENSE)

---

<div align="center">

**Hecho con `#06B6D4` en todo el mundo**

[GitHub](https://github.com/alexandervi1/nictichu-cli) | [Issues](https://github.com/alexandervi1/nictichu-cli/issues)

</div>