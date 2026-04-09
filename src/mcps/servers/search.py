"""MCP Server para búsqueda web."""

import httpx
from typing import Any

from ..client import MCPClient
from ...utils.logger import get_logger
from ...utils.config import get_settings

logger = get_logger()


class SearchMCPClient(MCPClient):
    """Cliente MCP para búsqueda web con Brave Search."""
    
    def __init__(self, server_name: str, config: dict[str, Any] | None = None):
        super().__init__(server_name, config)
        self.api_key = None
        self.client = None
    
    async def connect(self) -> bool:
        """Conectar al servidor de búsqueda."""
        try:
            settings = get_settings()
            self.api_key = self.config.get("api_key") or settings.brave_search_api_key
            
            if not self.api_key:
                logger.warning("No hay API key para Brave Search")
                self.session = False
                return False
            
            self.client = httpx.AsyncClient(
                base_url="https://api.search.brave.com/res/v1",
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.api_key
                },
                timeout=30.0
            )
            
            self.session = True
            logger.info("Search MCP conectado con Brave Search")
            return True
        except Exception as e:
            logger.error(f"Error conectando search MCP: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconectar del servidor de búsqueda."""
        if self.client:
            await self.client.aclose()
        self.session = None
        logger.info("Search MCP desconectado")
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "web_search",
                "description": "Buscar en la web",
                "parameters": {
                    "query": {"type": "string", "description": "Consulta de búsqueda"},
                    "count": {"type": "integer", "description": "Número de resultados", "default": 10}
                }
            },
            {
                "name": "news_search",
                "description": "Buscar noticias",
                "parameters": {
                    "query": {"type": "string", "description": "Consulta de búsqueda"},
                    "count": {"type": "integer", "description": "Número de resultados", "default": 10}
                }
            },
            {
                "name": "code_search",
                "description": "Buscar código",
                "parameters": {
                    "query": {"type": "string", "description": "Consulta de búsqueda"},
                    "language": {"type": "string", "description": "Lenguaje de programación"},
                    "count": {"type": "integer", "description": "Número de resultados", "default": 10}
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Ejecutar herramienta de búsqueda."""
        if not await self.is_connected():
            raise RuntimeError("Cliente de búsqueda no conectado")
        
        handlers = {
            "web_search": self._web_search,
            "news_search": self._news_search,
            "code_search": self._code_search,
        }
        
        handler = handlers.get(tool_name)
        if handler is None:
            raise ValueError(f"Herramienta no soportada: {tool_name}")
        
        return await handler(arguments)
    
    async def _web_search(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        """Búsqueda web."""
        query = args.get("query", "")
        count = args.get("count", 10)
        
        if not query:
            raise ValueError("Query es requerido")
        
        try:
            response = await self.client.get(
                "/search",
                params={
                    "q": query,
                    "count": count
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get("web", {}).get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "source": "brave"
                })
            
            logger.info(f"Búsqueda web: {query} ({len(results)} resultados)")
            return results
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            raise
    
    async def _news_search(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        """Búsqueda de noticias."""
        query = args.get("query", "")
        count = args.get("count", 10)
        
        if not query:
            raise ValueError("Query es requerido")
        
        try:
            response = await self.client.get(
                "/news/search",
                params={
                    "q": query,
                    "count": count
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get("news", {}).get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "date": result.get("date", ""),
                    "source": "brave"
                })
            
            logger.info(f"Búsqueda noticias: {query} ({len(results)} resultados)")
            return results
        except Exception as e:
            logger.error(f"Error en búsqueda de noticias: {e}")
            raise
    
    async def _code_search(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        """Búsqueda de código."""
        query = args.get("query", "")
        language = args.get("language", "")
        count = args.get("count", 10)
        
        search_query = f"{query} {language}" if language else query
        
        return await self._web_search({"query": search_query, "count": count})
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """Listar recursos."""
        return []
    
    async def read_resource(self, uri: str) -> Any:
        """Leer recurso."""
        raise ValueError("Search MCP no soporta recursos")
