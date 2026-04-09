# Contributing to NictichuCLI

¡Gracias por tu interés en contribuir a NictichuCLI! 🎉

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo puedo contribuir?](#¿cómo-puedo-contribuir)
- [Desarrollo](#desarrollo)
- [Pull Requests](#pull-requests)
- [Estilo de Código](#estilo-de-código)
- [Tests](#tests)
- [Documentación](#documentación)

---

## Código de Conducta

Este proyecto y todos sus participantes se rigen por el [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, se espera que respetes este código.

---

## ¿Cómo puedo contribuir?

### Reportar Bugs

**Antes de reportar un bug:**
1. Verifica que estés usando la última versión
2. Busca en los issues existentes para evitar duplicados
3. Recopila información sobre el bug

**Al reportar un bug, incluye:**
- Título claro y descriptivo
- Pasos para reproducir el bug
- Comportamiento esperado vs actual
- Capturas de pantalla (si aplica)
- Tu entorno (OS, Python version, etc.)

### Sugerir Mejoras

**Al sugerir una mejora, incluye:**
- Título claro y descriptivo
- Descripción detallada de la mejora
- Casos de uso y ejemplos
- Por qué sería útil para otros usuarios

---

## Desarrollo

### Setup Inicial

```powershell
# Clonar el repositorio
git clone https://github.com/alexandervi1/nictichu-cli.git
cd nictichu-cli

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Configurar .env
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

### Branches

- `main`: Versión estable
- `develop`: Desarrollo activo
- `feature/*`: Nuevas funcionalidades
- `bugfix/*`: Corrección de bugs

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: agregar nuevo proveedor de modelo
fix: corregir error en filesystem MCP
docs: actualizar documentación de API
test: agregar tests para ContextManager
refactor: simplificar lógica del orquestador
style: formatear código con ruff
```

---

## Pull Requests

### Antes de hacer PR

1. **Actualiza tu branch:**
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout your-branch
   git rebase develop
   ```

2. **Ejecuta tests:**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Verifica linting:**
   ```bash
   ruff check src/
   ```

### Proceso de PR

1. Crea un branch desde `develop`
2. Haz tus cambios siguiendo el estilo de código
3. Agrega tests para nuevos cambios
4. Actualiza documentación si es necesario
5. Asegura que todos los tests pasen
6. Crea Pull Request a `develop`

---

## Estilo de Código

### Python

Seguimos [PEP 8](https://peps.python.org/pep-0008/):

-**Longitud de línea**: 100 caracteres
- **Formateador**: Ruff
- **Type hints**: Obligatorios
- **Docstrings**: Google style

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Ejemplo de función con docstring.
    
    Args:
        param1: Descripción del parámetro.
        param2: Descripción del parámetro opcional.
    
    Returns:
        Descripción del valor de retorno.
    
    Raises:
        ValueError: Si param1 está vacío.
    """
    if not param1:
        raise ValueError("param1 no puede estar vacío")
    
    return len(param1) > param2
```

---

## Tests

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=src --cov-report=html

# Un archivo específico
python -m pytest tests/test_models/ -v
```

### Escribir Tests

```python
import pytest
from src.models.base import BaseModel


class MockModel(BaseModel):
    async def generate(self, prompt: str) -> str:
        return f"Generated: {prompt}"
    
    async def is_available(self) -> bool:
        return True


def test_mock_model():
    model = MockModel(model_id="test")
    assert model.model_id == "test"
```

---

## Documentación

### Docstrings

Usa Google style docstrings:

```python
def function_example(arg1: str) -> dict:
    """Descripción breve de la función.
    
    Descripción más detallada si es necesario.
    
    Args:
        arg1: Descripción del argumento 1.
    
    Returns:
        Descripción del valor de retorno.
    
    Raises:
        ValueError: Descripción de cuando se lanza.
    
    Example:
        >>> result = function_example("test")
        >>> print(result)
        {'status': 'success'}
    """
    return {"status": "success"}
```

### Actualizar README

Actualiza el README cuando:
- Agregues nueva funcionalidad
- Cambies la API
- Modifiques dependencias
- Actualices pasos de instalación

---

## Preguntas Frecuentes

### ¿Cómo ejecuto los tests localmente?

```bash
python -m pytest tests/ -v
```

### ¿Cómo formateo mi código?

```bash
ruff format src/
```

### ¿Cómo verifico tipos?

```bash
mypy src/
```

---

## Recursos

- [Documentación de Python](https://docs.python.org/3/)
- [Guía de PEP 8](https://peps.python.org/pep-0008/)
- [Documentación de Rich](https://rich.readthedocs.io/)
- [Documentación de Typer](https://typer.tiangolo.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la MIT License.

---

<div align="center">

¡Gracias por contribuir! 🚀

</div>
