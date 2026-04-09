"""Modelo Vertex AI para inferencia empresarial."""

import json
from typing import Any, AsyncGenerator

from .base import BaseModel
from ..utils.logger import get_logger

logger = get_logger()


class VertexAIModel(BaseModel):
    """Modelo que se conecta a Google Cloud Vertex AI."""
    
    def __init__(self, model_id: str, config: dict[str, Any] | None = None):
        super().__init__(model_id, config)
        self.project = config.get("project") if config else None
        self.location = config.get("location", "us-central1") if config else "us-central1"
        self.credentials_path = config.get("credentials_path") if config else None
        self.generation_config = config.get("generation_config", {}) if config else {}
        
        self._client = None
        self._endpoint = None
    
    async def _ensure_client(self):
        """Asegurar que el cliente está inicializado."""
        if self._client is None:
            try:
                from google.cloud import aiplatform
                
                if self.credentials_path:
                    aiplatform.init(
                        project=self.project,
                        location=self.location,
                        credentials=self._load_credentials()
                    )
                else:
                    aiplatform.init(
                        project=self.project,
                        location=self.location
                    )
                
                self._client = aiplatform
                
                valid_models = {
                    "gemini-pro": "gemini-pro",
                    "gemini-pro-vision": "gemini-pro-vision",
                    "text-bison": "text-bison",
                    "text-unicorn": "text-unicorn",
                    "code-bison": "code-bison",
                }
                
                model_name = valid_models.get(self.model_id, self.model_id)
                
                self._endpoint = aiplatform.Endpoint(model_name)
                
            except ImportError:
                raise ImportError(
                    "google-cloud-aiplatform no está instalado. "
                    "Instálelo con: pip install google-cloud-aiplatform"
                )
            except Exception as e:
                logger.error(f"Error iniciando Vertex AI: {e}")
                raise
        
        return self._endpoint
    
    def _load_credentials(self):
        """Cargar credenciales desde archivo."""
        if self.credentials_path:
            from google.oauth2 import service_account
            return service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
        return None
    
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
        endpoint = await self._ensure_client()
        
        try:
            instances = self._format_messages_for_vertex(messages)
            
            if tools:
                instances[0]["tools"] = self._format_tools_for_vertex(tools)
            
            parameters = {
                "temperature": self.generation_config.get("temperature", 0.7),
                "maxOutputTokens": self.generation_config.get("max_output_tokens", 2048),
                "topP": self.generation_config.get("top_p", 0.95),
                "topK": self.generation_config.get("top_k", 40),
                **kwargs
            }
            
            response = await endpoint.predict_async(
                instances=instances,
                parameters=parameters
            )
            
            if response.predictions and len(response.predictions) > 0:
                prediction = response.predictions[0]
                
                if isinstance(prediction, dict):
                    if "content" in prediction:
                        content = prediction["content"]
                        
                        if "tool_calls" in prediction:
                            return json.dumps({
                                "text": content,
                                "tool_calls": prediction["tool_calls"]
                            })
                        
                        return content
                
                return str(prediction)
            
            return ""
        
        except Exception as e:
            logger.error(f"Error en chat con Vertex AI: {e}")
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
        endpoint = await self._ensure_client()
        
        try:
            instances = self._format_messages_for_vertex(messages)
            
            if tools:
                instances[0]["tools"] = self._format_tools_for_vertex(tools)
            
            parameters = {
                "temperature": self.generation_config.get("temperature", 0.7),
                "maxOutputTokens": self.generation_config.get("max_output_tokens", 2048),
                "topP": self.generation_config.get("top_p", 0.95),
                "topK": self.generation_config.get("top_k", 40),
                **kwargs
            }
            
            response_stream = await endpoint.predict_streaming_async(
                instances=instances,
                parameters=parameters
            )
            
            async for chunk in response_stream:
                if chunk.predictions and len(chunk.predictions) > 0:
                    prediction = chunk.predictions[0]
                    if isinstance(prediction, dict) and "content" in prediction:
                        yield prediction["content"]
                    elif isinstance(prediction, str):
                        yield prediction
        
        except Exception as e:
            logger.error(f"Error en streaming con Vertex AI: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Verificar si el modelo está disponible."""
        if not self.project:
            return False
        
        try:
            await self._ensure_client()
            return self._endpoint is not None
        except Exception:
            return False
    
    def _format_messages_for_vertex(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Formatear mensajes para Vertex AI."""
        formatted_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            formatted_messages.append({
                "author": role,
                "content": content
            })
        
        return [{"messages": formatted_messages}]
    
    def _format_tools_for_vertex(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Formatear herramientas para Vertex AI."""
        vertex_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                
                vertex_tools.append({
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": func.get("parameters", {}),
                    }
                })
        
        return vertex_tools