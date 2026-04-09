"""Modelo Ollama para inferencia local."""

import json
import httpx
from typing import Any, AsyncGenerator

from .base import BaseModel
from ..utils.logger import get_logger

logger = get_logger()


class OllamaModel(BaseModel):
    """Modelo que se conecta a Ollama para inferencia local."""
    
    def __init__(self, model_id: str, config: dict[str, Any] | None = None):
        super().__init__(model_id, config)
        self.base_url = config.get("base_url", "http://localhost:11434") if config else "http://localhost:11434"
        self.timeout = config.get("timeout", 120) if config else 120
        self.options = config.get("options", {}) if config else {}
    
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> str:
        """Generar respuesta del modelo."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, tools=tools, **kwargs)
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> str:
        """Chat con el modelo."""
        payload = {
            "model": self.model_id,
            "messages": messages,
            "stream": False,
            "options": self.options,
            **kwargs
        }
        
        if tools:
            payload["tools"] = self._format_tools_for_ollama(tools)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if "message" in data:
                content = data["message"].get("content", "")
                
                if "tool_calls" in data["message"]:
                    return json.dumps({
                        "text": content,
                        "tool_calls": data["message"]["tool_calls"]
                    })
                
                return content
            
            return ""
    
    async def generate_stream(
        self,
        prompt: str,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generar respuesta con streaming."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        async for chunk in self.chat_stream(messages, tools=tools, **kwargs):
            yield chunk
    
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Chat con streaming."""
        payload = {
            "model": self.model_id,
            "messages": messages,
            "stream": True,
            "options": self.options,
            **kwargs
        }
        
        if tools:
            payload["tools"] = self._format_tools_for_ollama(tools)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    
    async def is_available(self) -> bool:
        """Verificar si el modelo está disponible."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return any(m["name"] == self.model_id for m in models)
        except Exception as e:
            logger.debug(f"Modelo {self.model_id} no disponible: {e}")
            return False
        return False
    
    async def pull_model(self) -> bool:
        """Descargar modelo si no está disponible."""
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model_id}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error descargando modelo {self.model_id}: {e}")
            return False
    
    def _format_tools_for_ollama(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Formatear herramientas para Ollama."""
        formatted_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": func.get("name", ""),
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {})
                    }
                })
        
        return formatted_tools