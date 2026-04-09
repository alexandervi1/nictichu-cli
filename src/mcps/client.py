from typing import Any


class MCPClient:
    """Cliente base para servidores MCP."""
    
    def __init__(self, server_name: str, config: dict[str, Any] | None = None):
        self.server_name = server_name
        self.config = config or {}
        self.session = None
    
    async def connect(self) -> bool:
        """Conectar al servidor MCP."""
        raise NotImplementedError
    
    async def disconnect(self) -> None:
        """Desconectar del servidor MCP."""
        raise NotImplementedError
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        raise NotImplementedError
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Llamar herramienta del servidor."""
        raise NotImplementedError
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """Listar recursos disponibles."""
        raise NotImplementedError
    
    async def read_resource(self, uri: str) -> Any:
        """Leer recurso del servidor."""
        raise NotImplementedError
    
    async def is_connected(self) -> bool:
        """Verificar si está conectado."""
        return self.session is not None
