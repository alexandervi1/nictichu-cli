"""CLI Interactivo de NictichuCLI con Rich y Prompt Toolkit."""

from typing import Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style as PromptStyle

from ..core.core import NictichuCore
from ..utils.logger import get_logger
from ..utils.config import load_config, get_settings
from .conversation import ConversationLoop
from .commands import CommandHandler

logger = get_logger()

class NictichuCLI:
    """CLI Interactivo con integración de herramientas y MCPs."""
    
    THEME = {
        "primary": "#06B6D4",
        "secondary": "#0891B2",
        "success": "#10B981",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6",
        "text": "#E5E7EB",
        "muted": "#6B7280",
    }
    
    def __init__(
        self,
        model_name: str = "gemma4:e2b",
        provider: str = "ollama",
        config_path: str | None = None
    ):
        self.model_name = model_name
        self.provider = provider
        self.config = load_config(config_path)
        
        self.console = Console(
            theme=Theme(self._create_rich_theme()),
            force_terminal=True
        )
        
        self.session: PromptSession | None = None
        self.core: NictichuCore | None = None
        self.conversation: ConversationLoop | None = None
        self.command_handler: CommandHandler | None = None
        
        self.history_file = Path.home() / ".nictichu_history"
        self.running = False
    
    def _create_rich_theme(self) -> dict[str, str]:
        """Crear tema para Rich."""
        return {
            "primary": self.THEME["primary"],
            "secondary": self.THEME["secondary"],
            "success": self.THEME["success"],
            "error": self.THEME["error"],
            "warning": self.THEME["warning"],
            "info": self.THEME["info"],
        }
    
    def _create_prompt_style(self) -> PromptStyle:
        """Crear estilo para Prompt Toolkit."""
        return PromptStyle.from_dict({
            "prompt": f"fg:{self.THEME['primary']} bold",
            "": f"fg:{self.THEME['text']}",
        })
    
    async def initialize(self) -> None:
        """Inicializar CLI."""
        self._show_banner()
        
        self.console.print("\n[dim]Inicializando...[/dim]")
        
        with self.console.status("[bold cyan]Cargando modelo y herramientas...[/bold cyan]") as status:
            settings = get_settings()
            model_config = {}
            
            if self.provider == "google_ai" and settings.google_ai_api_key:
                model_config["api_key"] = settings.google_ai_api_key
            elif self.provider == "ollama" and settings.ollama_base_url:
                model_config["base_url"] = settings.ollama_base_url
            elif self.provider == "vertex_ai" and settings.google_cloud_project:
                model_config["project"] = settings.google_cloud_project
                model_config["location"] = settings.google_cloud_location
            
            self.core = NictichuCore(
                model_name=self.model_name,
                provider=self.provider,
                model_config=model_config
            )
            await self.core.initialize()
            
            status.update("[bold cyan]Preparando herramientas...[/bold cyan]")
            self.conversation = ConversationLoop(self.core)
            self.command_handler = CommandHandler(self.core, self.conversation)
            
            await self.conversation.initialize()
            
            status.update("[bold cyan]Listo[/bold cyan]")
        
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=self._create_prompt_style(),
            message=self._get_prompt()
        )
        
        self.running = True
        
        provider_info = f"{self.core.provider}/{self.core.model_name}"
        self.console.print(f"\n[bold green]✓[/bold green] Sistema listo [dim]({provider_info})[/dim]")
        self._show_help()
    
    def _get_prompt(self) -> str:
        """Obtener prompt del usuario."""
        return f"[{self.model_name}] > "
    
    def _show_banner(self) -> None:
        """Mostrar banner de bienvenida."""
        banner = f"""
[bold {self.THEME['primary']}]NictichuCLI[/bold {self.THEME['primary']}] - Agente de Código Multi-Modelo

[dim]Modelo: {self.model_name}[/dim]
[dim]Proveedor: {self.provider}[/dim]
"""
        self.console.print(Panel(banner, border_style=self.THEME["primary"]))
    
    def _show_help(self) -> None:
        """Mostrar ayuda."""
        help_text = """
[bold]Comandos disponibles:[/bold]
  [cyan]/help[/cyan]     - Mostrar esta ayuda
  [cyan]/tools[/cyan]    - Listar herramientas disponibles
  [cyan]/mcps[/cyan]     - Listar MCP servers activos
  [cyan]/model[/cyan]    - Cambiar modelo
  [cyan]/clear[/cyan]    - Limpiar contexto
  [cyan]/save[/cyan]     - Guardar conversación
  [cyan]/load[/cyan]     - Cargar conversación
  [cyan]/status[/cyan]   - Ver estado del sistema
  [cyan]/quit[/cyan]     - Salir

[dim]Escribe tu pregunta o código y presiona Enter para enviar.[/dim]
[dim]Usa Ctrl+C para cancelar una operación.[/dim]
"""
        self.console.print(help_text)
    
    async def run(self) -> None:
        """Ejecutar loop principal del CLI."""
        await self.initialize()
        
        while self.running:
            try:
                user_input = await self.session.prompt_async()
                
                if not user_input.strip():
                    continue
                
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    await self._handle_message(user_input)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operación cancelada[/yellow]")
                continue
            except EOFError:
                await self._quit()
                break
            except Exception as e:
                logger.exception("Error en loop principal")
                self.console.print(f"\n[error]Error: {e}[/error]")
    
    async def _handle_command(self, command: str) -> None:
        """Manejar comando especial."""
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/quit" or cmd == "/exit":
            await self._quit()
        elif cmd == "/help":
            self._show_help()
        elif cmd == "/tools":
            await self._show_tools()
        elif cmd == "/mcps":
            await self._show_mcps()
        elif cmd == "/model":
            await self._change_model(args)
        elif cmd == "/clear":
            await self._clear_context()
        elif cmd == "/save":
            await self._save_conversation(args)
        elif cmd == "/load":
            await self._load_conversation(args)
        elif cmd == "/status":
            await self._show_status()
        else:
            self.console.print(f"[warning]Comando desconocido: {cmd}[/warning]")
            self.console.print("[dim]Usa /help para ver comandos disponibles[/dim]")
    
    async def _handle_message(self, message: str) -> None:
        """Manejar mensaje del usuario."""
        if not self.conversation:
            self.console.print("[error]Conversación no inicializada[/error]")
            return
        
        self.console.print()
        
        with self.console.status("[bold cyan]Pensando...[/bold cyan]"):
            try:
                response = await self.conversation.send_message(message)
                self._display_response(response)
            except Exception as e:
                logger.exception("Error procesando mensaje")
                self.console.print(f"[error]Error: {e}[/error]")
    
    def _display_response(self, response: dict[str, Any]) -> None:
        """Mostrar respuesta del modelo."""
        if "text" in response:
            self.console.print(Panel(
                Markdown(response["text"]),
                title="[bold]Respuesta[/bold]",
                border_style=self.THEME["primary"]
            ))
        
        if "code" in response:
            self._display_code(response["code"])
        
        if "tool_calls" in response and response["tool_calls"]:
            self._display_tool_calls(response["tool_calls"])
        
        if "context" in response:
            self.console.print(f"\n[dim]Tokens: {response['context']['tokens']}[/dim]")
    
    def _display_code(self, code_info: dict[str, Any]) -> None:
        """Mostrar código."""
        language = code_info.get("language", "python")
        code = code_info.get("content", "")
        
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(Panel(
            syntax,
            title=f"[bold]Código ({language})[/bold]",
            border_style=self.THEME["secondary"]
        ))
    
    def _display_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
        """Mostrar llamadas a herramientas."""
        table = Table(title="[bold]Herramientas Ejecutadas[/bold]", border_style=self.THEME["primary"])
        table.add_column("Herramienta", style="cyan")
        table.add_column("Estado", style="bold")
        table.add_column("Resultado")
        
        for call in tool_calls:
            status = "[green]✓[/green]" if call.get("success") else "[red]✗[/red]"
            result = call.get("result", "")[:50] + "..." if len(call.get("result", "")) > 50 else call.get("result", "")
            table.add_row(call.get("tool", ""), status, result)
        
        self.console.print(table)
    
    async def _show_tools(self) -> None:
        """Mostrar herramientas disponibles."""
        if not self.core:
            return
        
        table = Table(title="[bold]Herramientas Disponibles[/bold]", border_style=self.THEME["primary"])
        table.add_column("Herramienta", style="cyan")
        table.add_column("Descripción")
        
        tools = await self.core.get_available_tools()
        for tool in tools:
            table.add_row(tool["name"], tool["description"])
        
        self.console.print(table)
    
    async def _show_mcps(self) -> None:
        """Mostrar MCP servers activos."""
        if not self.core:
            return
        
        table = Table(title="[bold]MCP Servers Activos[/bold]", border_style=self.THEME["primary"])
        table.add_column("Server", style="cyan")
        table.add_column("Estado", style="bold")
        table.add_column("Herramientas")
        
        mcps = await self.core.get_active_mcps()
        for mcp in mcps:
            status = "[green]Activo[/green]" if mcp["active"] else "[red]Inactivo[/red]"
            tools_count = str(len(mcp.get("tools", [])))
            table.add_row(mcp["name"], status, tools_count)
        
        self.console.print(table)
    
    async def _change_model(self, model_spec: str) -> None:
        """Cambiar modelo."""
        if not model_spec:
            self.console.print("[warning]Uso: /model <proveedor>/<modelo>[/warning]")
            self.console.print("[dim]Ejemplo: /model ollama/gemma4:e2b[/dim]")
            return
        
        if "/" not in model_spec:
            self.console.print("[warning]Formato: <proveedor>/<modelo>[/warning]")
            return
        
        provider, model = model_spec.split("/", 1)
        
        self.console.print(f"[dim]Cambiando a {provider}/{model}...[/dim]")
        
        try:
            await self.core.change_model(provider, model)
            self.model_name = model
            self.provider = provider
            self.console.print(f"[success]✓ Modelo cambiado a {provider}/{model}[/success]")
        except Exception as e:
            self.console.print(f"[error]Error cambiando modelo: {e}[/error]")
    
    async def _clear_context(self) -> None:
        """Limpiar contexto de conversación."""
        if self.conversation:
            await self.conversation.clear()
            self.console.print("[success]✓ Contexto limpiado[/success]")
    
    async def _save_conversation(self, filename: str) -> None:
        """Guardar conversación."""
        if not filename:
            filename = f"conversation_{self.model_name}.json"
        
        if self.conversation:
            await self.conversation.save(filename)
            self.console.print(f"[success]✓ Conversación guardada en {filename}[/success]")
    
    async def _load_conversation(self, filename: str) -> None:
        """Cargar conversación."""
        if not filename:
            self.console.print("[warning]Uso: /load <archivo>[/warning]")
            return
        
        if self.conversation:
            await self.conversation.load(filename)
            self.console.print(f"[success]✓ Conversación cargada de {filename}[/success]")
    
    async def _show_status(self) -> None:
        """Mostrar estado del sistema."""
        if not self.core:
            return
        
        status_info = await self.core.get_status()
        
        table = Table(title="[bold]Estado del Sistema[/bold]", border_style=self.THEME["primary"])
        table.add_column("Componente", style="cyan")
        table.add_column("Estado", style="bold")
        table.add_column("Detalles")
        
        for component, info in status_info.items():
            status = "[green]✓[/green]" if info.get("ok") else "[red]✗[/red]"
            details = info.get("details", "")
            table.add_row(component, status, details)
        
        self.console.print(table)
    
    async def _quit(self) -> None:
        """Salir del CLI."""
        self.console.print("\n[dim]Guardando estado...[/dim]")
        
        if self.conversation:
            await self.conversation.cleanup()
        
        if self.core:
            await self.core.cleanup()
        
        self.running = False
        
        self.console.print(f"\n[bold {self.THEME['primary']}]¡Gracias por usar NictichuCLI![/bold {self.THEME['primary']}]\n")