# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adherence a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-04-08

### Agregado
- Estructura inicial del proyecto
- Multi-modelo: Soporte para Ollama, Google AI Studi , Vertex AI
- MCPs integrados: Filesystem, Shell, Memory, Search
- CLI interactivo con Rich y Prompt Toolkit
- Sistema de configuración con Pydantic Settings
- Logging con Loguru
- Paleta de colores Cian (#06B6D4)
- Documentación completa (README, DEVGUIDE, QUICKSTART, INSTALL)
- Tests unitarios básicos
- Ejemplos de uso
- Guía de contribución (CONTRIBUTING)
- Código de conducta (CODE_OF_CONDUCT)
- Licencia MIT
- CI/CD con GitHub Actions
- Makefile para tareas comunes
- Scripts de setup para Windows y Linux

### Modelos Soportados
- Gemma 2B (Ollama)
- Gemma 7B (Ollama)
- Gemma 7B Instruct (Ollama, Google AI)
- Gemma 7B (Vertex AI)

### MCPs Disponibles
- **Filesystem**: Manipulación de archivos
- **Shell**: Ejecución de comandos
- **Memory**: Memoria persistente con Mem0
- **Search**: Búsqueda web con Brave Search

### Herramientas de Código
- Editor de código (crear, editar, refactorizar)
- Revisor de código (análisis estático)
- Ejecutor de tests (pytest, unittest)
- Generador de documentación

## [0.0.1] - 2024-04-08

### Agregado
- Inicialización del proyecto
- Configuración básica de Git
- Estructura de directorios

---

## Tipos de Cambios

- **Agregado**: Nuevas funcionalidades
- **Cambiado**: Cambios en funcionalidades existentes
- **Deprecated**: Funcionalidades que serán removidas
- **Removido**: Funcionalidades removidas
- **Fixed**: Corrección de bugs
- **Security**: Correcciones de vulnerabilidades

[0.1.0]: https://github.com/alexandervi1/nictichu-cli/releases/tag/v0.1.0
[0.0.1]: https://github.com/alexandervi1/nictichu-cli/tree/c0e5e97
