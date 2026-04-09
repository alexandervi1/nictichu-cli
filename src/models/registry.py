from typing import Any
from .base import BaseModel


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, BaseModel] = {}
        self._providers: dict[str, type[BaseModel]] = {}
    
    def register_provider(self, name: str, provider_class: type[BaseModel]):
        self._providers[name] = provider_class
    
    def list_providers(self) -> list[str]:
        return list(self._providers.keys())


_registry: ModelRegistry | None = None


def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
