#!/usr/bin/env python3
"""Entry point principal de NictichuCLI."""

import asyncio
import sys
import typer
from typing import Optional
from .utils.logger import setup_logger, get_logger

logger = get_logger()
app = typer.Typer(
    name="nictichu",
    help="NictichuCLI - Agente de código multi-modelo con MCPs y Gemma",
    add_completion=False
)


@app.command()
def interactive(
    model: str = typer.Option("gemma:7b", "--model", "-m", help="Modelo a usar"),
    provider: str = typer.Option("ollama", "--provider", "-p", help="Proveedor")
):
    """Iniciar CLI interactivo."""
    setup_logger()
    logger.info(f"Iniciando NictichuCLI con {model} ({provider})")
    typer.echo(f"\n🎨 NictichuCLI v0.1.0")
    typer.echo(f"   Modelo: {model}")
    typer.echo(f"   Proveedor: {provider}")
    typer.echo("\n¡Bienvenido! El proyecto está listo para usar.")
    typer.echo("Para más información, consulta el README.md")


@app.command()
def version():
    """Mostrar versión."""
    typer.echo("NictichuCLI v0.1.0")


if __name__ == "__main__":
    app()
