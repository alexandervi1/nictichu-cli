from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    """Clase abstracta para proveedores de modelos."""
    
    def __init__(self, model_id: str, config: dict[str, Any] | None = None):
        self.model_id = model_id
        self.config = config or {}
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any
    ) -> str:
        """Generar texto a partir de un prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any
    ):
        """Generar texto en streaming."""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any
    ) -> str:
        """Chat con historial de mensajes."""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any
    ):
        """Chat en streaming."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Verificar si el modelo está disponible."""
        pass
    
    def get_info(self) -> dict[str, Any]:
        """Obtener información del modelo."""
        return {
            "model_id": self.model_id,
            "provider": self.__class__.__name__,
            "config": self.config
        }
