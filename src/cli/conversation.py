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
        from ..tools.tester import TestRunnerTool
        from ..tools.docs import DocGeneratorTool
        
        tools = [
            CodeEditorTool(),
            CodeReviewerTool(),
            TestRunnerTool(),
            DocGeneratorTool(),
        ]
        
        for tool in tools:
            self.tools[tool.name] = tool
        
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
            definitions.append({
                "type": "function",
                "function": {
                    "name": f"code_{tool_name}",
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.list_tools()[0].get("parameters", {}),
                        "required": []
                    }
                }
            })
        
        for tool_id, mcp_tool in self.mcp_tools.items():
            tool = mcp_tool["tool"]
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool_id.replace(":", "_"),
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
                        tool_name.replace("code_", ""),
                        arguments
                    )
                elif "_" in tool_name and ":" in tool_name.replace("_", ":"):
                    mcp_name, tool = tool_name.replace("_", ":").split(":", 1)
                    mcp_tool = f"{mcp_name}:{tool}"
                    result = await self._execute_mcp_tool(mcp_tool, arguments)
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
    
    async def _execute_internal_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Ejecutar herramienta interna."""
        if tool_name not in self.tools:
            return {"error": f"Herramienta no encontrada: {tool_name}"}
        
        tool = self.tools[tool_name]
        
        available_methods = {
            "create_file": tool.create_file,
            "edit_file": tool.edit_file,
            "refactor_file": tool.refactor_file,
            "search_and_replace": tool.search_and_replace,
            "create_directory": tool.create_directory,
            "delete_file": tool.delete_file,
            "analyze_file": tool.analyze_file,
            "find_issues": tool.find_issues,
            "generate_report": tool.generate_report,
            "check_security": tool.check_security,
            "check_complexity": tool.check_complexity,
            "run_tests": tool.run_tests,
            "run_single_test": tool.run_single_test,
            "list_tests": tool.list_tests,
            "generate_coverage": tool.generate_coverage,
            "generate_module_doc": tool.generate_module_doc,
            "generate_class_doc": tool.generate_class_doc,
            "generate_function_doc": tool.generate_function_doc,
            "generate_readme": tool.generate_readme,
        }
        
        method_name = None
        for meth in available_methods:
            if meth.startswith(tool_name.split("_")[0]):
                method_name = meth
                break
        
        if not method_name or method_name not in available_methods:
            return {"error": f"Método no encontrado para herramienta: {tool_name}"}
        
        try:
            result = await available_methods[method_name](**arguments)
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