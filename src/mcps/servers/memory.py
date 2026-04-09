"""MCP Server para memoria persistente."""

from typing import Any

from ..client import MCPClient
from ...utils.logger import get_logger

logger = get_logger()


class MemoryMCPClient(MCPClient):
    """Cliente MCP para memoria persistente con Mem0."""
    
    def __init__(self, server_name: str, config: dict[str, Any] | None = None):
        super().__init__(server_name, config)
        self.mem0_client = None
    
    async def connect(self) -> bool:
        """Conectar al servidor de memoria."""
        try:
            api_key = self.config.get("api_key")
            
            if api_key:
                try:
                    from mem0 import AsyncMemory
                    
                    self.mem0_client = AsyncMemory(api_key=api_key)
                    self.session = True
                    logger.info("Memory MCP conectado con Mem0")
                    return True
                except ImportError:
                    logger.warning("mem0ai no disponible, usando memoria local")
            
            self.session = True
            logger.info("Memory MCP conectado en modo local")
            return True
        except Exception as e:
            logger.error(f"Error conectando memory MCP: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconectar del servidor de memoria."""
        self.session = None
        self.mem0_client = None
        logger.info("Memory MCP desconectado")
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "add_memory",
                "description": "Agregar memoria",
                "parameters": {
                    "content": {"type": "string", "description": "Contenido a recordar"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "metadata": {"type": "object", "description": "Metadatos adicionales"}
                }
            },
            {
                "name": "get_memories",
                "description": "Obtener memorias",
                "parameters": {
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "query": {"type": "string", "description": "Consulta opcional"}
                }
            },
            {
                "name": "search_memories",
                "description": "Buscar memorias",
                "parameters": {
                    "query": {"type": "string", "description": "Término de búsqueda"},
                    "user_id": {"type": "string", "description": "ID del usuario"},
                    "limit": {"type": "integer", "description": "Límite de resultados", "default": 10}
                }
            },
            {
                "name": "delete_memory",
                "description": "Eliminar memoria",
                "parameters": {
                    "memory_id": {"type": "string", "description": "ID de la memoria"}
                }
            },
            {
                "name": "clear_memories",
                "description": "Limpiar todas las memorias",
                "parameters": {
                    "user_id": {"type": "string", "description": "ID del usuario"}
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Ejecutar herramienta de memoria."""
        if not await self.is_connected():
            raise RuntimeError("Cliente de memoria no conectado")
        
        handlers = {
            "add_memory": self._add_memory,
            "get_memories": self._get_memories,
            "search_memories": self._search_memories,
            "delete_memory": self._delete_memory,
            "clear_memories": self._clear_memories,
        }
        
        handler = handlers.get(tool_name)
        if handler is None:
            raise ValueError(f"Herramienta no soportada: {tool_name}")
        
        return await handler(arguments)
    
    async def _add_memory(self, args: dict[str, Any]) -> dict[str, Any]:
        """Agregar memoria."""
        content = args.get("content", "")
        user_id = args.get("user_id", "default")
        metadata = args.get("metadata", {})
        
        if self.mem0_client:
            try:
                result = await self.mem0_client.add(
                    messages=[{"role": "user", "content": content}],
                    user_id=user_id,
                    metadata=metadata
                )
                logger.info(f"Memoria agregada para usuario {user_id}")
                return {"success": True, "memory_id": result.get("id")}
            except Exception as e:
                logger.error(f"Error agregando memoria: {e}")
                return {"success": False, "error": str(e)}
        else:
            logger.info(f"Memoria local agregada: {content[:50]}...")
            return {"success": True, "memory_id": f"local_{user_id}_{hash(content)}"}
    
    async def _get_memories(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        """Obtener memorias."""
        user_id = args.get("user_id", "default")
        query = args.get("query")
        
        if self.mem0_client:
            try:
                if query:
                    memories = await self.mem0_client.search(query, user_id=user_id)
                else:
                    memories = await self.mem0_client.get_all(user_id=user_id)
                
                return memories
            except Exception as e:
                logger.error(f"Error obteniendo memorias: {e}")
                return []
        else:
            return []
    
    async def _search_memories(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        """Buscar memorias."""
        query = args.get("query", "")
        user_id = args.get("user_id", "default")
        limit = args.get("limit", 10)
        
        if self.mem0_client:
            try:
                memories = await self.mem0_client.search(
                    query,
                    user_id=user_id,
                    limit=limit
                )
                return memories
            except Exception as e:
                logger.error(f"Error buscando memorias: {e}")
                return []
        else:
            return []
    
    async def _delete_memory(self, args: dict[str, Any]) -> bool:
        """Eliminar memoria."""
        memory_id = args.get("memory_id")
        
        if not memory_id:
            return False
        
        if self.mem0_client:
            try:
                await self.mem0_client.delete(memory_id)
                logger.info(f"Memoria eliminada: {memory_id}")
                return True
            except Exception as e:
                logger.error(f"Error eliminando memoria: {e}")
                return False
        
        return True
    
    async def _clear_memories(self, args: dict[str, Any]) -> bool:
        """Limpiar todas las memorias."""
        user_id = args.get("user_id", "default")
        
        if self.mem0_client:
            try:
                await self.mem0_client.delete_all(user_id=user_id)
                logger.info(f"Memorias limpiadas para usuario {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error limpiando memorias: {e}")
                return False
        
        return True
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """Listar recursos."""
        return []
    
    async def read_resource(self, uri: str) -> Any:
        """Leer recurso."""
        raise ValueError("Memory MCP no soporta recursos")
