# Guía de Desarrollo - NictichuCLI

## Ubicación del Proyecto

```
C:\Users\Worsktation 2029\Documents\GitHub\nictichu-cli
```

## Configuración Actual

- **Python**: 3.14.3
- **Entorno Virtual**: venv/
- **Dependencias**: Instaladas correctamente

## Comandos Diarios

### Activar Entorno Virtual

```powershell
# En Windows PowerShell
cd C:\Users\Worsktation 2029\Documents\GitHub\nictichu-cli
.\venv\Scripts\activate
```

### Ejecutar CLI

```powershell
# Con entorno activado
python -m src.main interactive

# O con parámetros
python -m src.main interactive --model gemma2:2b --provider ollama
```

### Ejecutar Tests

```powershell
python -m pytest tests/ -v
```

### Instalar Dependencias

```powershell
pip install -e .
```

## Estructura de Trabajo

```
nictichu-cli/
├── src/              # Código fuente principal
│   ├── core/         # Núcleo del agente
│   ├── models/       # Proveedores de modelos
│   ├── mcps/         # Servidores MCP
│   ├── tools/        # Herramientas
│   ├── cli/          # Interfaz CLI
│   └── utils/        # Utilidades
├── config/           # Archivos de configuración
│   ├── settings.yaml # Config general
│   └── models.yaml   # Config de modelos
├── tests/             # Tests unitarios
├── examples/          # Ejemplos de uso
├── venv/              # Entorno virtual (no editar)
├── .env               # Variables de entorno (crear desde .env.example)
└── README.md          # Este archivo
```

## Flujo de Trabajo

### 1. Hacer Cambios

```powershell
# Editar archivos en src/
code .  # Abrir VS Code
```

### 2. Probar Cambios

```powershell
python -m src.main interactive
```

### 3. Commit a Git

```powershell
git add .
git commit -m "Descripción del cambio"
git push
```

## Archivos Importantes

### .env

```bash
# Configuración de Ollama (local - gratuito)
OLLAMA_BASE_URL=http://localhost:11434

# Google AI Studio (necesitas API key)
GOOGLE_AI_API_KEY=tu_api_key

# Vertex AI (necesitas proyecto en GCP)
GOOGLE_CLOUD_PROJECT=tu_proyecto_id
GOOGLE_CLOUD_LOCATION=us-central1

# Logging
LOG_LEVEL=INFO
```

### config/settings.yaml

Configuración visual y de modelos (no necesita modificación).

## Siguientes Pasos

1. Configurar `.env` con tus API keys
2. Ejecutar `python -m src.main interactive`
3. Empezar a desarrollar

## URLs Importantes

- **Repositorio**: https://github.com/TU_USUARIO/nictichu-cli
- **Issues**: https://github.com/TU_USUARIO/nictichu-cli/issues

## Ayuda

```powershell
python -m src.main --help
```
