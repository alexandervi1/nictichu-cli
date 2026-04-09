"""Handler de comandos especiales."""

from typing import Any

from ..utils.logger import get_logger

logger = get_logger()


class CommandHandler:
    """Maneja comandos especiales del CLI."""
    
    def __init__(self, core: Any, conversation: Any):
        self.core = core
        self.conversation = conversation
    
    async def handle(self, command: str, args: str) -> dict[str, Any]:
        """Manejar comando."""
        handlers = {
            "help": self._cmd_help,
            "tools": self._cmd_tools,
            "mcps": self._cmd_mcps,
            "model": self._cmd_model,
            "clear": self._cmd_clear,
            "save": self._cmd_save,
            "load": self._cmd_load,
            "status": self._cmd_status,
            "create": self._cmd_create,
            "edit": self._cmd_edit,
            "analyze": self._cmd_analyze,
            "test": self._cmd_test,
            "doc": self._cmd_doc,
        }
        
        handler = handlers.get(command)
        
        if handler:
            return await handler(args)
        else:
            return {"error": f"Comando desconocido: {command}"}
    
    async def _cmd_help(self, args: str) -> dict[str, Any]:
        """Mostrar ayuda."""
        return {
            "text": """
Comandos disponibles:

  /help              - Mostrar esta ayuda
  /tools             - Listar herramientas disponibles
  /mcps              - Listar MCP servers activos
  /model <p/m>       - Cambiar modelo
  /clear             - Limpiar contexto
  /save <file>       - Guardar conversación
  /load <file>       - Cargar conversación
  /status            - Ver estado del sistema
  /create <file>     - Crear archivo
  /edit <file>       - Editar archivo
  /analyze <file>    - Analizar archivo
  /test <path>       - Ejecutar tests
  /doc <file>        - Generar documentación
            """
        }
    
    async def _cmd_tools(self, args: str) -> dict[str, Any]:
        """Mostrar herramientas."""
        tools = []
        for name, tool in self.conversation.tools.items():
            tools.append(f"  - {name}: {tool.description}")
        
        return {
            "text": f"Herramientas disponibles:\n" + "\n".join(tools)
        }
    
    async def _cmd_mcps(self, args: str) -> dict[str, Any]:
        """Mostrar MCP servers."""
        if not self.core.mcp_manager:
            return {"text": "No hay MCP servers configurados"}
        
        mcps = []
        for server in self.core.mcp_manager.get_available_servers():
            client = self.core.mcp_manager.get_client(server)
            if client:
                status = "activo" if await client.is_connected() else "inactivo"
                tools = await client.list_tools()
                mcps.append(f"  - {server} ({status}, {len(tools)} herramientas)")
        
        return {
            "text": f"MCP Servers:\n" + "\n".join(mcps)
        }
    
    async def _cmd_model(self, args: str) -> dict[str, Any]:
        """Cambiar modelo."""
        if not args:
            return {"text": f"Modelo actual: {self.core.provider}/{self.core.model_name}"}
        
        if "/" not in args:
            return {"error": "Formato: <proveedor>/<modelo>"}
        
        provider, model = args.split("/", 1)
        
        try:
            await self.core.change_model(provider, model)
            return {"text": f"Modelo cambiado a {provider}/{model}"}
        except Exception as e:
            return {"error": f"Error cambiando modelo: {e}"}
    
    async def _cmd_clear(self, args: str) -> dict[str, Any]:
        """Limpiar contexto."""
        await self.conversation.clear()
        return {"text": "Contexto limpiado"}
    
    async def _cmd_save(self, args: str) -> dict[str, Any]:
        """Guardar conversación."""
        filename = args or f"conversation_{self.core.model_name}.json"
        await self.conversation.save(filename)
        return {"text": f"Conversación guardada en {filename}"}
    
    async def _cmd_load(self, args: str) -> dict[str, Any]:
        """Cargar conversación."""
        if not args:
            return {"error": "Uso: /load <archivo>"}
        
        await self.conversation.load(args)
        return {"text": f"Conversación cargada de {args}"}
    
    async def _cmd_status(self, args: str) -> dict[str, Any]:
        """Mostrar estado."""
        status = await self.core.get_status()
        
        lines = ["Estado del sistema:"]
        for component, info in status.items():
            state = "✓" if info.get("ok") else "✗"
            details = info.get("details", "")
            lines.append(f"  {state} {component}: {details}")
        
        return {"text": "\n".join(lines)}
    
    async def _cmd_create(self, args: str) -> dict[str, Any]:
        """Crear archivo."""
        if not args:
            return {"error": "Uso: /create <archivo>"}
        
        return {"text": f"Para crear {args}, escribe tu mensaje al modelo y él usará la herramienta create_file"}
    
    async def _cmd_edit(self, args: str) -> dict[str, Any]:
        """Editar archivo."""
        if not args:
            return {"error": "Uso: /edit <archivo>"}
        
        return {"text": f"Para editar {args}, escribe tu mensaje al modelo y él usará la herramienta edit_file"}
    
    async def _cmd_analyze(self, args: str) -> dict[str, Any]:
        """Analizar archivo."""
        if not args:
            return {"error": "Uso: /analyze <archivo>"}
        
        return {"text": f"Para analizar {args}, escribe tu mensaje al modelo y él usará la herramienta analyze_file"}
    
    async def _cmd_test(self, args: str) -> dict[str, Any]:
        """Ejecutar tests."""
        if not args:
            return {"error": "Uso: /test <path>"}
        
        return {"text": f"Para ejecutar tests en {args}, escribe tu mensaje al modelo y él usará la herramienta run_tests"}
    
    async def _cmd_doc(self, args: str) -> dict[str, Any]:
        """Generar documentación."""
        if not args:
            return {"error": "Uso: /doc <archivo>"}
        
        return {"text": f"Para generar documentación de {args}, escribe tu mensaje al modelo y él usará la herramienta generate_module_doc"}