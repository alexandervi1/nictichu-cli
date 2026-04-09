from typing import Any
import os

from ..models.base import BaseModel
from ..models.registry import get_registry
from ..mcps.manager import MCPManager
from ..utils.logger import get_logger

logger = get_logger()


class NictichuCore:
    """Núcleo del agente NictichuCLI."""
    
    def __init__(
        self,
        model_name: str = "gemma4:e2b",
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
        
        config = self.model_config.copy()
        
        if self.provider == "google_ai" and not config.get("api_key"):
            api_key = os.environ.get("GOOGLE_AI_API_KEY", "")
            if api_key:
                config["api_key"] = api_key
        
        if self.provider == "vertex_ai" and not config.get("project"):
            project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
            if project:
                config["project"] = project
        
        self.model = registry.create_model(
            provider=self.provider,
            model_id=self.model_name,
            config=config
        )
        
        if self.model is None:
            raise ValueError(f"No se pudo crear modelo {self.provider}/{self.model_name}")
        
        available = await self.model.is_available()
        if not available:
            logger.warning(f"Modelo {self.model_name} no esta disponible")
            
            if self.provider == "ollama":
                google_key = os.environ.get("GOOGLE_AI_API_KEY", "")
                if google_key:
                    logger.info("Intentando fallback a Google AI (Gemini)...")
                    self.provider = "google_ai"
                    self.model_name = "gemini-2.0-flash"
                    self.model = registry.create_model(
                        provider="google_ai",
                        model_id=self.model_name,
                        config={"api_key": google_key}
                    )
                    if self.model and await self.model.is_available():
                        logger.info(f"Fallback exitoso: usando {self.provider}/{self.model_name}")
                    else:
                        logger.info("Para usar Ollama: instala desde https://ollama.com y ejecuta 'ollama pull gemma4:e2b'")
                        logger.info("Para usar Google AI (gratis): agrega GOOGLE_AI_API_KEY a tu archivo .env")
                else:
                    logger.info("Para usar Ollama: instala desde https://ollama.com y ejecuta 'ollama pull gemma4:e2b'")
                    logger.info("Para usar Google AI (gratis): obtiene tu API key en https://aistudio.google.com/apikey")
                    logger.info("  Luego agrega GOOGLE_AI_API_KEY=tu_key al archivo .env")
        
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
        
        for server_name in self.mcp_manager.get_available_servers():
            try:
                result = await self.mcp_manager.call_tool(server_name, tool_name, arguments)
                return result
            except Exception:
                continue
        
        raise ValueError(f"Herramienta no encontrada: {tool_name}")
    
    async def shutdown(self) -> None:
        """Cerrar conexiones y limpiar recursos."""
        logger.info("Cerrando NictichuCLI")
        
        if self.mcp_manager:
            await self.mcp_manager.shutdown()
        
        logger.info("NictichuCLI cerrado correctamente")
    
    async def initialize_mcps(self) -> None:
        """Inicializar MCP servers."""
        if self.mcp_manager:
            await self.mcp_manager.initialize()
            logger.info("MCP servers inicializados")
    
    async def get_available_tools(self) -> list[dict[str, Any]]:
        """Obtener lista de herramientas disponibles."""
        tools = []
        
        from ..tools.editor import CodeEditorTool
        from ..tools.reviewer import CodeReviewerTool
        from ..tools.tester import PytestRunner
        from ..tools.docs import DocGeneratorTool
        
        code_tools = [
            CodeEditorTool(),
            CodeReviewerTool(),
            PytestRunner(),
            DocGeneratorTool(),
        ]
        
        for tool in code_tools:
            for tool_def in tool.list_tools():
                tools.append({
                    "name": f"code_{tool_def['name']}",
                    "description": tool_def["description"],
                    "parameters": tool_def.get("parameters", {})
                })
        
        if self.mcp_manager:
            for server_name in self.mcp_manager.get_available_servers():
                client = self.mcp_manager.get_client(server_name)
                if client:
                    tools_list = await client.list_tools()
                    for tool_def in tools_list:
                        tools.append({
                            "name": f"{server_name}_{tool_def['name']}",
                            "description": tool_def["description"],
                            "parameters": tool_def.get("parameters", {})
                        })
        
        return tools
    
    async def get_active_mcps(self) -> list[dict[str, Any]]:
        """Obtener lista de MCP servers activos."""
        mcps = []
        
        if self.mcp_manager:
            for server_name in self.mcp_manager.get_available_servers():
                client = self.mcp_manager.get_client(server_name)
                if client:
                    tools_list = await client.list_tools()
                    connected = await client.is_connected()
                    mcps.append({
                        "name": server_name,
                        "active": connected,
                        "tools": tools_list
                    })
        
        return mcps
    
    async def change_model(self, provider: str, model_id: str) -> None:
        """Cambiar modelo activo."""
        registry = get_registry()
        
        self.model = registry.create_model(
            provider=provider,
            model_id=model_id,
            config=self.model_config
        )
        
        if self.model is None:
            raise ValueError(f"No se pudo crear modelo {provider}/{model_id}")
        
        self.provider = provider
        self.model_name = model_id
        
        logger.info(f"Modelo cambiado a {provider}/{model_id}")
    
    async def get_status(self) -> dict[str, dict[str, Any]]:
        """Obtener estado del sistema."""
        status = {}
        
        status["model"] = {
            "ok": self.model is not None,
            "details": f"{self.provider}/{self.model_name}" if self.model else "No inicializado"
        }
        
        status["mcp_manager"] = {
            "ok": self.mcp_manager is not None,
            "details": "Inicializado" if self.mcp_manager else "No inicializado"
        }
        
        if self.mcp_manager:
            mcp_count = len(self.mcp_manager.get_available_servers())
            status["mcp_servers"] = {
                "ok": True,
                "details": f"{mcp_count} servers activos"
            }
        
        tools = await self.get_available_tools()
        status["tools"] = {
            "ok": len(tools) > 0,
            "details": f"{len(tools)} herramientas disponibles"
        }
        
        return status
    
    async def cleanup(self) -> None:
        """Limpiar recursos."""
        await self.shutdown()
