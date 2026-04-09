"""Loop de conversación con integración de herramientas."""

import json
from pathlib import Path
from typing import Any

from ..core.context import ContextManager
from ..models.base import BaseModel
from ..utils.logger import get_logger

logger = get_logger()


class ConversationLoop:
    """Maneja el loop de conversación con el modelo de IA."""
    
    def __init__(self, core: Any):
        self.core = core
        self.context = ContextManager(max_tokens=4096)
        self.tools: dict[str, Any] = {}
        self.mcp_tools: dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Inicializar conversación y registrar herramientas."""
        self._register_tools()
        self._register_mcp_tools()
        logger.info("Conversación inicializada")
    
    def _register_tools(self) -> None:
        """Registrar herramientas disponibles."""
        from ..tools.editor import CodeEditorTool
        from ..tools.reviewer import CodeReviewerTool
        from ..tools.tester import PytestRunner
        from ..tools.docs import DocGeneratorTool
        
        self._tool_classes = [
            CodeEditorTool(),
            CodeReviewerTool(),
            PytestRunner(),
            DocGeneratorTool(),
        ]
        
        for tool_cls in self._tool_classes:
            self.tools[tool_cls.name] = tool_cls
        
        logger.info(f"Registradas {len(self.tools)} herramientas")
    
    def _register_mcp_tools(self) -> None:
        """Registrar herramientas de MCP servers."""
        if not self.core.mcp_manager:
            return
        
        available_mcps = self.core.mcp_manager.get_available_servers()
        
        for mcp_name in available_mcps:
            mcp_client = self.core.mcp_manager.get_client(mcp_name)
            if mcp_client:
                tools = mcp_client.list_tools()
                for tool in tools:
                    tool_id = f"{mcp_name}:{tool['name']}"
                    self.mcp_tools[tool_id] = {
                        "mcp": mcp_name,
                        "tool": tool,
                        "client": mcp_client
                    }
        
        logger.info(f"Registradas {len(self.mcp_tools)} herramientas MCP")
    
    async def send_message(self, message: str) -> dict[str, Any]:
        """Enviar mensaje al modelo y procesar respuesta."""
        logger.info(f"Mensaje recibido: {message[:100]}...")
        
        self.context.add_message("user", message)
        
        messages = self.context.get_messages()
        
        response = await self.core.model.generate(messages, tools=self._get_tool_definitions())
        
        result = {
            "text": "",
            "tool_calls": [],
            "context": {
                "tokens": self.context.get_token_count()
            }
        }
        
        if response.get("tool_calls"):
            tool_results = await self._execute_tool_calls(response["tool_calls"])
            result["tool_calls"] = tool_results
            
            if response.get("text"):
                result["text"] = response["text"]
            else:
                self.context.add_message("assistant", f"Herramientas ejecutadas: {len(tool_results)}")
                
                messages = self.context.get_messages()
                final_response = await self.core.model.generate(messages)
                result["text"] = final_response.get("text", "")
        else:
            result["text"] = response.get("text", "")
        
        if result["text"]:
            self.context.add_message("assistant", result["text"])
        
        return result
    
    def _get_tool_definitions(self) -> list[dict[str, Any]]:
        """Obtener definiciones de herramientas para el modelo."""
        definitions = []
        
        for tool_name, tool in self.tools.items():
            for tool_def in tool.list_tools():
                definitions.append({
                    "type": "function",
                    "function": {
                        "name": f"code_{tool_name}_{tool_def['name']}",
                        "description": tool_def.get("description", ""),
                        "parameters": {
                            "type": "object",
                            "properties": tool_def.get("parameters", {}),
                            "required": []
                        }
                    }
                })
        
        for tool_id, mcp_tool in self.mcp_tools.items():
            tool = mcp_tool["tool"]
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool_id.replace(":", "__"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            })
        
        return definitions
    
    async def _execute_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ejecutar llamadas a herramientas."""
        results = []
        
        for call in tool_calls:
            tool_name = call.get("name", "")
            arguments = call.get("arguments", {})
            
            try:
                if tool_name.startswith("code_"):
                    result = await self._execute_internal_tool(
                        tool_name,
                        arguments
                    )
                elif tool_name.startswith("mcp__"):
                    mcp_id = tool_name.replace("mcp__", "", 1).replace("__", ":", 1)
                    result = await self._execute_mcp_tool(mcp_id, arguments)
                else:
                    result = {"error": f"Herramienta desconocida: {tool_name}"}
                
                results.append({
                    "tool": tool_name,
                    "success": "error" not in result,
                    "result": result
                })
                
                self.context.add_message("system", json.dumps(result))
                
            except Exception as e:
                logger.exception(f"Error ejecutando herramienta {tool_name}")
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "result": {"error": str(e)}
                })
        
        return results
    
    async def _execute_internal_tool(self, tool_call_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Ejecutar herramienta interna."""
        if not tool_call_name.startswith("code_"):
            return {"error": f"Formato de herramienta interna inválido: {tool_call_name}"}
        
        remainder = tool_call_name[len("code_"):]
        
        matched_tool = None
        matched_method_name = None
        for tool_key, tool_obj in self.tools.items():
            if remainder.startswith(tool_key + "_"):
                method_name = remainder[len(tool_key) + 1:]
                if hasattr(tool_obj, method_name):
                    matched_tool = tool_obj
                    matched_method_name = method_name
                    break
        
        if matched_tool is None or matched_method_name is None:
            return {"error": f"Herramienta no encontrada: {tool_call_name}"}
        
        try:
            method = getattr(matched_tool, matched_method_name)
            if arguments:
                result = await method(**arguments)
            else:
                result = await method()
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_mcp_tool(self, tool_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Ejecutar herramienta de MCP."""
        if tool_id not in self.mcp_tools:
            return {"error": f"Herramienta MCP no encontrada: {tool_id}"}
        
        mcp_tool = self.mcp_tools[tool_id]
        client = mcp_tool["client"]
        tool_name = mcp_tool["tool"]["name"]
        
        try:
            result = await client.call_tool(tool_name, arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def clear(self) -> None:
        """Limpiar contexto de conversación."""
        self.context.clear()
        logger.info("Contexto limpiado")
    
    async def save(self, filename: str) -> None:
        """Guardar conversación."""
        filepath = Path(filename)
        data = {
            "context": self.context.export_context(),
            "model": self.core.model_name,
            "provider": self.core.provider
        }
        
        filepath.write_text(json.dumps(data, indent=2))
        logger.info(f"Conversación guardada en {filepath}")
    
    async def load(self, filename: str) -> None:
        """Cargar conversación."""
        filepath = Path(filename)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filename}")
        
        data = json.loads(filepath.read_text())
        
        if data["context"]:
            self.context.import_context(data["context"])
        
        logger.info(f"Conversación cargada de {filepath}")
    
    async def cleanup(self) -> None:
        """Limpiar recursos."""
        self.context.clear()
        logger.info("Recursos de conversación liberados")