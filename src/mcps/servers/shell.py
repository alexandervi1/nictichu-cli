"""MCP Server para ejecución de comandos shell."""

import asyncio
from typing import Any

from ..client import MCPClient
from ...utils.logger import get_logger

logger = get_logger()


class ShellMCPClient(MCPClient):
    """Cliente MCP para ejecución de comandos shell."""
    
    def __init__(self, server_name: str, config: dict[str, Any] | None = None):
        super().__init__(server_name, config)
        self.allowed_commands: list[str] = []
        self.blocked_commands: list[str] = []
    
    async def connect(self) -> bool:
        """Conectar al servidor shell."""
        try:
            self.allowed_commands = self.config.get("allowed_commands", [])
            self.blocked_commands = self.config.get("blocked_commands", [
                "rm -rf",
                "sudo",
                "chmod",
                "chown",
                "mkfs",
                "dd",
                ">",
                "shutdown",
                "reboot"
            ])
            
            self.session = True
            logger.info("Shell MCP conectado")
            return True
        except Exception as e:
            logger.error(f"Error conectando shell MCP: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconectar del servidor shell."""
        self.session = None
        logger.info("Shell MCP desconectado")
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "execute",
                "description": "Ejecutar comando shell",
                "parameters": {
                    "command": {"type": "string", "description": "Comando a ejecutar"},
                    "timeout": {"type": "integer", "description": "Timeout en segundos", "default": 30}
                }
            },
            {
                "name": "execute_script",
                "description": "Ejecutar script desde archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del script"},
                    "interpreter": {"type": "string", "description": "Intérprete a usar", "default": "bash"}
                }
            }
        ]
    
    def _is_command_allowed(self, command: str) -> tuple[bool, str]:
        """Verificar si el comando está permitido."""
        cmd_lower = command.lower().strip()
        
        for blocked in self.blocked_commands:
            if blocked.lower() in cmd_lower:
                return False, f"Comando bloqueado: {blocked}"
        
        if self.allowed_commands:
            for allowed in self.allowed_commands:
                if cmd_lower.startswith(allowed.lower()):
                    return True, ""
            return False, "Comando no está en la lista permitida"
        
        return True, ""
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Ejecutar herramienta shell."""
        if not await self.is_connected():
            raise RuntimeError("Cliente shell no conectado")
        
        handlers = {
            "execute": self._execute,
            "execute_script": self._execute_script,
        }
        
        handler = handlers.get(tool_name)
        if handler is None:
            raise ValueError(f"Herramienta no soportada: {tool_name}")
        
        return await handler(arguments)
    
    async def _execute(self, args: dict[str, Any]) -> dict[str, Any]:
        """Ejecutar comando shell."""
        command = args.get("command", "")
        timeout = args.get("timeout", 30)
        
        allowed, reason = self._is_command_allowed(command)
        if not allowed:
            raise PermissionError(f"Comando no permitido: {reason}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise TimeoutError(f"Comando excedió timeout de {timeout}s")
            
            result = {
                "return_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "success": process.returncode == 0
            }
            
            logger.info(f"Comando ejecutado: {command[:50]}...")
            
            return result
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            raise
    
    async def _execute_script(self, args: dict[str, Any]) -> dict[str, Any]:
        """Ejecutar script desde archivo."""
        path = args.get("path", "")
        interpreter = args.get("interpreter", "bash")
        
        command = f"{interpreter} {path}"
        
        return await self._execute({"command": command, "timeout": args.get("timeout", 60)})
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """Listar recursos."""
        return []
    
    async def read_resource(self, uri: str) -> Any:
        """Leer recurso."""
        raise ValueError("Shell MCP no soporta recursos")
