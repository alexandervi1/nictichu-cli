from typing import Any
from .client import MCPClient
from ..utils.logger import get_logger

logger = get_logger()


class MCPManager:
    """Gestor de servidores MCP."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.clients: dict[str, MCPClient] = {}
    
    async def initialize(self) -> None:
        """Inicializar todos los servidores MCP configurados."""
        logger.info("Inicializando MCP Manager")
        
        servers = self.config.get("servers", {})
        enabled = self.config.get("enabled", [])
        
        for server_name in enabled:
            if server_name in servers:
                server_config = servers[server_name]
                
                client = await self._create_client(server_name, server_config)
                
                if client:
                    self.clients[server_name] = client
                    logger.info(f"MCP {server_name} inicializado")
    
    async def _create_client(
        self,
        server_name: str,
        server_config: dict[str, Any]
    ) -> MCPClient | None:
        """Crear cliente MCP apropiado."""
        try:
            server_type = server_config.get("type", "stdio")
            
            if server_type == "fileSystem":
                from .servers.filesystem import FileSystemMCPClient
                return FileSystemMCPClient(server_name, server_config)
            elif server_type == "shell":
                from .servers.shell import ShellMCPClient
                return ShellMCPClient(server_name, server_config)
            elif server_type == "memory":
                from .servers.memory import MemoryMCPClient
                return MemoryMCPClient(server_name, server_config)
            elif server_type == "search":
                from .servers.search import SearchMCPClient
                return SearchMCPClient(server_name, server_config)
            else:
                logger.warning(f"Tipo de servidor MCP no soportado: {server_type}")
                return None
        except Exception as e:
            logger.error(f"Error creando cliente MCP {server_name}: {e}")
            return None
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Any:
        """Llamar herramienta en servidor específico."""
        client = self.clients.get(server_name)
        
        if client is None:
            raise ValueError(f"Servidor MCP no encontrado: {server_name}")
        
        if not await client.is_connected():
            logger.warning(f"Reconectando a {server_name}")
            connected = await client.connect()
            if not connected:
                raise RuntimeError(f"No se pudo conectar a {server_name}")
        
        return await client.call_tool(tool_name, arguments)
    
    async def list_tools(self, server_name: str | None = None) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        if server_name:
            client = self.clients.get(server_name)
            if client:
                return await client.list_tools()
            return []
        
        all_tools = []
        for client in self.clients.values():
            tools = await client.list_tools()
            all_tools.extend(tools)
        
        return all_tools
    
    async def shutdown(self) -> None:
        """Cerrar todos los clientes MCP."""
        logger.info("Cerrando MCP Manager")
        
        for server_name, client in self.clients.items():
            try:
                await client.disconnect()
                logger.info(f"Cliente MCP {server_name} cerrado")
            except Exception as e:
                logger.error(f"Error cerrando cliente {server_name}: {e}")
        
        self.clients.clear()
