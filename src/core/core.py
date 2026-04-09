from typing import Any

from ..models.base import BaseModel
from ..models.registry import get_registry
from ..mcps.manager import MCPManager
from ..utils.logger import get_logger

logger = get_logger()


class NictichuCore:
    """Núcleo del agente NictichuCLI."""
    
    def __init__(
        self,
        model_name: str = "gemma:7b",
        provider: str = "ollama",
        model_config: dict[str, Any] | None = None,
        mcp_config: dict[str, Any] | None = None
    ):
        self.model_name = model_name
        self.provider = provider
        self.model_config = model_config or {}
        self.mcp_config = mcp_config or {}
        
        self.model: BaseModel | None = None
        self.mcp_manager: MCPManager | None = None
    
    async def initialize(self) -> None:
        """Inicializar el agente."""
        logger.info(f"Inicializando NictichuCLI con {self.provider}/{self.model_name}")
        
        registry = get_registry()
        
        self.model = registry.create_model(
            provider=self.provider,
            model_id=self.model_name,
            config=self.model_config
        )
        
        if self.model is None:
            raise ValueError(f"No se pudo crear modelo {self.provider}/{self.model_name}")
        
        available = await self.model.is_available()
        if not available:
            logger.warning(f"Modelo {self.model_name} no está disponible")
        
        self.mcp_manager = MCPManager(self.mcp_config)
        await self.mcp_manager.initialize()
        
        logger.info("NictichuCLI inicializado correctamente")
    
    async def process_message(
        self,
        message: str,
        context: list[dict[str, str]] | None = None,
        tools: list[str] | None = None,
        **kwargs: Any
    ) -> str:
        """Procesar mensaje del usuario."""
        if self.model is None:
            raise RuntimeError("Agente no inicializado")
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        logger.debug(f"Procesando mensaje: {message[:50]}...")
        
        response = await self.model.chat(
            messages=messages,
            **kwargs
        )
        
        return response
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Any:
        """Ejecutar herramienta MCP."""
        if self.mcp_manager is None:
            raise RuntimeError("MCP Manager no inicializado")
        
        logger.info(f"Ejecutando herramienta: {tool_name}")
        
        result = await self.mcp_manager.call_tool(tool_name, arguments)
        
        return result
    
    async def shutdown(self) -> None:
        """Cerrar conexiones y limpiar recursos."""
        logger.info("Cerrando NictichuCLI")
        
        if self.mcp_manager:
            await self.mcp_manager.shutdown()
        
        logger.info("NictichuCLI cerrado correctamente")
