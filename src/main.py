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
    model: str = typer.Option("gemma2:2b", "--model", "-m", help="Modelo a usar"),
    provider: str = typer.Option("ollama", "--provider", "-p", help="Proveedor"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Archivo de configuración")
):
    """Iniciar CLI interactivo."""
    setup_logger()
    
    try:
        from .cli.interface import NictichuCLI
        
        cli = NictichuCLI(
            model_name=model,
            provider=provider,
            config_path=config
        )
        
        asyncio.run(cli.run())
    
    except KeyboardInterrupt:
        logger.info("Interumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Error: {e}")
        typer.echo(f"\n[ERROR] {e}", err=True)
        sys.exit(1)


@app.command()
def version():
    """Mostrar versión."""
    typer.echo("NictichuCLI v0.1.0")


if __name__ == "__main__":
    app()
