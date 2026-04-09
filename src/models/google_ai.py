"""Modelo Google AI Studio para inferencia."""

import json
from typing import Any, AsyncGenerator

from .base import BaseModel
from ..utils.logger import get_logger

logger = get_logger()


class GoogleAIModel(BaseModel):
    """Modelo que se conecta a Google AI Studio."""
    
    def __init__(self, model_id: str, config: dict[str, Any] | None = None):
        super().__init__(model_id, config)
        self.api_key = config.get("api_key") if config else None
        self.base_url = config.get("base_url", "https://generativelanguage.googleapis.com/v1beta") if config else "https://generativelanguage.googleapis.com/v1beta"
        self.generation_config = config.get("generation_config", {}) if config else {}
        self.safety_settings = config.get("safety_settings", []) if config else []
        
        self._client = None
    
    async def _ensure_client(self):
        """Asegurar que el cliente está inicializado."""
        if self._client is None:
            try:
                import google.generativeai as genai
                
                if not self.api_key:
                    raise ValueError("API key requerida para Google AI Studio")
                
                genai.configure(api_key=self.api_key)
                
                valid_models = {
                    "gemini-pro": "gemini-pro",
                    "gemini-pro-vision": "gemini-pro-vision",
                    "gemini-1.5-pro": "gemini-1.5-pro",
                    "gemini-1.5-flash": "gemini-1.5-flash",
                }
                
                model_name = valid_models.get(self.model_id, self.model_id)
                
                self._client = genai.GenerativeModel(
                    model_name,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
            except ImportError:
                raise ImportError(
                    "google-generativeai no está instalado. "
                    "Instálelo con: pip install google-generativeai"
                )
        
        return self._client
    
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
            messages.append({"role": "user", "parts": [system]})
            messages.append({"role": "model", "parts": ["Entendido."]})
        messages.append({"role": "user", "parts": [prompt]})
        
        return await self.chat(messages, tools=tools, **kwargs)
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> str:
        """Chat con el modelo."""
        client = await self._ensure_client()
        
        try:
            formatted_messages = self._format_messages_for_gemini(messages)
            
            chat = client.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            last_message = formatted_messages[-1]["parts"][0] if formatted_messages else ""
            
            if tools:
                gemini_tools = self._format_tools_for_gemini(tools)
                response = await chat.send_message_async(
                    last_message,
                    tools=gemini_tools,
                    **kwargs
                )
            else:
                response = await chat.send_message_async(last_message, **kwargs)
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                if candidate.content and candidate.content.parts:
                    text_parts = []
                    tool_calls = []
                    
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            text_parts.append(part.text)
                        
                        if hasattr(part, "function_call"):
                            tool_calls.append({
                                "name": part.function_call.name,
                                "arguments": dict(part.function_call.args)
                            })
                    
                    if tool_calls:
                        return json.dumps({
                            "text": " ".join(text_parts),
                            "tool_calls": tool_calls
                        })
                    
                    return " ".join(text_parts)
            
            return ""
        
        except Exception as e:
            logger.error(f"Error en chat con Google AI: {e}")
            raise
    
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
            messages.append({"role": "user", "parts": [system]})
            messages.append({"role": "model", "parts": ["Entendido."]})
        messages.append({"role": "user", "parts": [prompt]})
        
        async for chunk in self.chat_stream(messages, tools=tools, **kwargs):
            yield chunk
    
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Chat con streaming."""
        client = await self._ensure_client()
        
        try:
            formatted_messages = self._format_messages_for_gemini(messages)
            
            chat = client.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            last_message = formatted_messages[-1]["parts"][0] if formatted_messages else ""
            
            if tools:
                gemini_tools = self._format_tools_for_gemini(tools)
                response = await chat.send_message_async(
                    last_message,
                    tools=gemini_tools,
                    stream=True,
                    **kwargs
                )
            else:
                response = await chat.send_message_async(last_message, stream=True, **kwargs)
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Error en streaming con Google AI: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Verificar si el modelo está disponible."""
        if not self.api_key:
            return False
        
        try:
            client = await self._ensure_client()
            return client is not None
        except Exception:
            return False
    
    def _format_messages_for_gemini(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Formatear mensajes para Gemini API."""
        formatted = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", msg.get("parts", [""])[0] if "parts" in msg else "")
            
            if isinstance(content, str):
                parts = [content]
            elif isinstance(content, list):
                parts = content
            else:
                parts = [str(content)]
            
            formatted.append({
                "role": "user" if role in ("user", "human") else "model",
                "parts": parts
            })
        
        return formatted
    
    def _format_tools_for_gemini(self, tools: list[dict[str, Any]]) -> list[Any]:
        """Formatear herramientas para Gemini."""
        try:
            import google.generativeai.types as genai_types
            
            function_declarations = []
            
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool.get("function", {})
                    
                    function_declarations.append(
                        genai_types.FunctionDeclaration(
                            name=func.get("name", ""),
                            description=func.get("description", ""),
                            parameters=func.get("parameters", {})
                        )
                    )
            
            return [genai_types.Tool(function_declarations=function_declarations)]
        
        except ImportError:
            logger.warning("google-generativeai.types no disponible")
            return []