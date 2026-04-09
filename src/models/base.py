from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    def __init__(self, model_id: str):
        self.model_id = model_id
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        pass
    
    def get_info(self) -> dict[str, Any]:
        return {"model_id": self.model_id, "provider": self.__class__.__name__}
