# Guía de Instalación - NictichuCLI

## Windows

### Requisitos
- Python 3.10+
- Git

### Instalación
```powershell
# Clonar
git clone https://github.com/TU_USUARIO/nictichu-cli.git
cd nictichu-cli

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar
pip install -e .

# Configurar
copy .env.example .env
notepad .env

# Ejecutar
python -m src.main interactive
```

## Ubuntu/Linux

### Instalación
```bash
# Clonar
git clone https://github.com/TU_USUARIO/nictichu-cli.git
cd nictichu-cli

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar
pip install -e .

# Configurar
cp .env.example .env
nano .env

# Ejecutar
python -m src.main interactive
```

## Ollama (Opcional)

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma:7b

# Windows - Descargar desde ollama.com
```

## Verificar

```bash
python -c "from src import __version__; print(f'NictichuCLI {__version__}')"
```
