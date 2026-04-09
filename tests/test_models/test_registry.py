"""
Tests para el registro de modelos.
"""

import pytest
from src.models.registry import ModelRegistry, get_registry
from src.models.base import BaseModel


class MockModel(BaseModel):
    """Modelo mock para testing."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        return f"Generated: {prompt}"
    
    async def generate_stream(self, prompt: str, **kwargs):
        yield "Chunk 1"
        yield "Chunk 2"
    
    async def chat(self, messages: list, **kwargs) -> str:
        return f"Chat response"
    
    async def chat_stream(self, messages: list, **kwargs):
        yield "Chat"
        yield "Stream"
    
    async def is_available(self) -> bool:
        return True


class TestModelRegistry:
    """Tests para ModelRegistry."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.registry = ModelRegistry()
    
    def test_registry_initialization(self):
        """Test inicialización del registro."""
        assert len(self.registry._models) == 0
        assert len(self.registry._providers) == 0
    
    def test_register_provider(self):
        """Test registro de proveedor."""
        self.registry.register_provider("test_provider", MockModel)
        
        assert "test_provider" in self.registry._providers
        assert self.registry._providers["test_provider"] == MockModel
    
    def test_register_model(self):
        """Test registro de modelo."""
        model = MockModel(model_id="test_model")
        self.registry.register_model("test_model", model)
        
        assert "test_model" in self.registry._models
        assert self.registry._models["test_model"] == model
    
    def test_get_model(self):
        """Test obtener modelo."""
        model = MockModel(model_id="test_model")
        self.registry.register_model("test_model", model)
        
        retrieved = self.registry.get_model("test_model")
        
        assert retrieved == model
        assert retrieved.model_id == "test_model"
    
    def test_get_model_not_found(self):
        """Test obtener modelo que no existe."""
        model = self.registry.get_model("nonexistent")
        
        assert model is None
    
    def test_get_provider(self):
        """Test obtener proveedor."""
        self.registry.register_provider("test_provider", MockModel)
        
        provider = self.registry.get_provider("test_provider")
        
        assert provider == MockModel
    
    def test_get_provider_not_found(self):
        """Test obtener proveedor que no existe."""
        provider = self.registry.get_provider("nonexistent")
        
        assert provider is None
    
    def test_create_model(self):
        """Test crear modelo desde proveedor."""
        self.registry.register_provider("test_provider", MockModel)
        
        model = self.registry.create_model(
            provider="test_provider",
            model_id="test_model",
            config={"key": "value"}
        )
        
        assert model is not None
        assert model.model_id == "test_model"
        assert model.config == {"key": "value"}
    
    def test_create_model_provider_not_found(self):
        """Test crear modelo con proveedor que no existe."""
        model = self.registry.create_model(
            provider="nonexistent",
            model_id="test_model"
        )
        
        assert model is None
    
    def test_list_models(self):
        """Test listar modelos."""
        model1 = MockModel(model_id="model1")
        model2 = MockModel(model_id="model2")
        
        self.registry.register_model("model1", model1)
        self.registry.register_model("model2", model2)
        
        models = self.registry.list_models()
        
        assert len(models) == 2
        assert "model1" in models
        assert "model2" in models
    
    def test_list_providers(self):
        """Test listar proveedores."""
        self.registry.register_provider("provider1", MockModel)
        self.registry.register_provider("provider2", MockModel)
        
        providers = self.registry.list_providers()
        
        assert len(providers) == 2
        assert "provider1" in providers
        assert "provider2" in providers
    
    def test_clear(self):
        """Test limpiar registro."""
        model = MockModel(model_id="test_model")
        self.registry.register_model("test_model", model)
        self.registry.register_provider("test_provider", MockModel)
        
        self.registry.clear()
        
        assert len(self.registry._models) == 0
        assert len(self.registry._providers) == 0


class TestGetRegistry:
    """Tests para get_registry."""
    
    def test_get_registry_singleton(self):
        """Test que get_registry retorna singleton."""
        registry1 = get_registry()
        registry2 = get_registry()
        
        assert registry1 is registry2
    
    def test_get_registry_returns_registry_instance(self):
        """Test que get_registry retorna instancia de ModelRegistry."""
        registry = get_registry()
        
        assert isinstance(registry, ModelRegistry)
