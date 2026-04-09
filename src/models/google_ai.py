"""Modelo Google AI Studio para inferencia."""

import json
import httpx
from typing import Any, AsyncGenerator

from .base import BaseModel
from ..utils.logger import get_logger

logger = get_logger()

GEMINI_MODELS = {
    "gemini-2.5-flash": "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
    "gemini-1.5-pro": "gemini-1.5-pro",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-pro": "gemini-1.5-pro",
}


class GoogleAIModel(BaseModel):
    """Modelo que se conecta a Google AI Studio via HTTP (sin SDK)."""
    
    def __init__(self, model_id: str, config: dict[str, Any] | None = None):
        super().__init__(model_id, config)
        self.api_key = config.get("api_key") if config else None
        self.base_url = config.get(
            "base_url",
            "https://generativelanguage.googleapis.com/v1beta"
        ) if config else "https://generativelanguage.googleapis.com/v1beta"
        self.generation_config = config.get("generation_config", {}) if config else {}
        self.timeout = config.get("timeout", 120) if config else 120
        
        model_name = GEMINI_MODELS.get(model_id, config.get("model_name", model_id)) if config else GEMINI_MODELS.get(model_id, model_id)
        self.resolved_model = model_name
    
    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "user", "content": system})
            messages.append({"role": "model", "content": "Entendido."})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, tools=tools, **kwargs)
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> str:
        url = f"{self.base_url}/models/{self.resolved_model}:generateContent?key={self.api_key}"
        
        contents = self._format_messages(messages)
        payload: dict[str, Any] = {"contents": contents}
        
        generation_config = {
            "temperature": self.generation_config.get("temperature", 1.0),
            "topP": self.generation_config.get("top_p", 0.95),
            "topK": self.generation_config.get("top_k", 64),
            "maxOutputTokens": self.generation_config.get("max_output_tokens", 8192),
        }
        payload["generationConfig"] = generation_config
        
        if tools:
            payload["tools"] = self._format_tools_for_gemini(tools)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            return ""
        
        candidate = data["candidates"][0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        
        text_parts = []
        tool_calls = []
        
        for part in parts:
            if "text" in part:
                text_parts.append(part["text"])
            if "functionCall" in part:
                fc = part["functionCall"]
                tool_calls.append({
                    "name": fc.get("name", ""),
                    "arguments": fc.get("args", {})
                })
        
        if tool_calls:
            return json.dumps({
                "text": " ".join(text_parts),
                "tool_calls": tool_calls
            })
        
        return " ".join(text_parts)
    
    async def generate_stream(
        self,
        prompt: str,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system:
            messages.append({"role": "user", "content": system})
            messages.append({"role": "model", "content": "Entendido."})
        messages.append({"role": "user", "content": prompt})
        
        async for chunk in self.chat_stream(messages, tools=tools, **kwargs):
            yield chunk
    
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/models/{self.resolved_model}:streamGenerateContent?key={self.api_key}&alt=sse"
        
        contents = self._format_messages(messages)
        payload: dict[str, Any] = {"contents": contents}
        
        generation_config = {
            "temperature": self.generation_config.get("temperature", 1.0),
            "topP": self.generation_config.get("top_p", 0.95),
            "topK": self.generation_config.get("top_k", 64),
            "maxOutputTokens": self.generation_config.get("max_output_tokens", 8192),
        }
        payload["generationConfig"] = generation_config
        
        if tools:
            payload["tools"] = self._format_tools_for_gemini(tools)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "candidates" in data and data["candidates"]:
                                parts = data["candidates"][0].get("content", {}).get("parts", [])
                                for part in parts:
                                    if "text" in part:
                                        yield part["text"]
                        except json.JSONDecodeError:
                            continue
    
    async def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False
    
    def _format_messages(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                role = "user"
            
            gemini_role = "user" if role in ("user", "human", "system") else "model"
            
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return contents
    
    def _format_tools_for_gemini(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        function_declarations = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                params = func.get("parameters", {})
                
                if isinstance(params, dict) and "properties" in params:
                    prop = params["properties"]
                elif isinstance(params, dict):
                    prop = params
                else:
                    prop = {}
                
                declarations = {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                }
                
                if prop:
                    declarations["parameters"] = {
                        "type": "object",
                        "properties": prop,
                    }
                
                function_declarations.append(declarations)
        
        return [{"functionDeclarations": function_declarations}]