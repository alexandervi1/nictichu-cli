from typing import Any

from ..utils.logger import get_logger
from .base import BaseModel

logger = get_logger()


class ModelRegistry:
    """Registro de modelos disponibles."""
    
    def __init__(self):
        self._models: dict[str, BaseModel] = {}
        self._providers: dict[str, type[BaseModel]] = {}
    
    def register_provider(self, name: str, provider_class: type[BaseModel]) -> None:
        """Registrar un proveedor de modelos."""
        self._providers[name] = provider_class
        logger.info(f"Proveedor registrado: {name}")
    
    def register_model(self, name: str, model: BaseModel) -> None:
        """Registrar un modelo específico."""
        self._models[name] = model
        logger.info(f"Modelo registrado: {name}")
    
    def get_model(self, name: str) -> BaseModel | None:
        """Obtener un modelo por nombre."""
        return self._models.get(name)
    
    def get_provider(self, name: str) -> type[BaseModel] | None:
        """Obtener una clase de proveedor por nombre."""
        return self._providers.get(name)
    
    def create_model(
        self,
        provider: str,
        model_id: str,
        config: dict[str, Any] | None = None
    ) -> BaseModel | None:
        """Crear una instancia de modelo."""
        provider_class = self._providers.get(provider)
        if provider_class is None:
            logger.error(f"Proveedor no encontrado: {provider}")
            return None
        
        model = provider_class(model_id=model_id, config=config)
        return model
    
    def list_models(self) -> list[str]:
        """Listar todos los modelos registrados."""
        return list(self._models.keys())
    
    def list_providers(self) -> list[str]:
        """Listar todos los proveedores registrados."""
        return list(self._providers.keys())
    
    def clear(self) -> None:
        """Limpiar el registro."""
        self._models.clear()
        self._providers.clear()


_registry: ModelRegistry | None = None


def get_registry() -> ModelRegistry:
    """Obtener instancia singleton del registro."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
