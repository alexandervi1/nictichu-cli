# Guía de Instalación - NictichuCLI

## Instalación con 1 clic (Recomendado)

### Windows
```
Doble clic en install.bat
```
Se descarga, instala todo, configura el .env y crea un acceso directo en el escritorio.

### Linux / Mac
```bash
chmod +x install.sh && ./install.sh
```
Se descarga, instala todo y agrega el comando `nictichu` al shell.

### Ejecutar después de instalar
- **Windows**: Doble clic en `run.bat` o el acceso directo del escritorio
- **Linux/Mac**: Escribe `nictichu` en la terminal

---

## Instalación Manual

### Windows

#### Requisitos
- Python 3.10+
- Git

#### Pasos
```powershell
git clone https://github.com/alexandervi1/nictichu-cli.git
cd nictichu-cli

python -m venv venv
venv\Scripts\activate

pip install -e .

copy .env.example .env
notepad .env

python -m src.main interactive
```

### Linux / Mac

#### Pasos
```bash
git clone https://github.com/alexandervi1/nictichu-cli.git
cd nictichu-cli

python3 -m venv venv
source venv/bin/activate

pip install -e .

cp .env.example .env
nano .env

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