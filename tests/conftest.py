"""
Configuración de pytest.
"""

import pytest
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_settings():
    """Fixture para Settings mock."""
    from src.utils.config import Settings
    
    return Settings(
        app_name="TestApp",
        app_version="0.0.1",
        model_name="test_model",
        model_provider="test_provider"
    )


@pytest.fixture
def mock_context():
    """Fixture para ContextManager."""
    from src.core.context import ContextManager
    
    context = ContextManager(max_history=10)
    
    # Agregar algunos mensajes de prueba
    context.add_message("user", "Test message 1")
    context.add_message("assistant", "Test response 1")
    context.add_message("user", "Test message 2")
    
    return context


@pytest.fixture
def mock_model():
    """Fixture para modelo mock."""
    from src.models.base import BaseModel
    
    class MockModel(BaseModel):
        async def generate(self, prompt: str, **kwargs) -> str:
            return f"Generated: {prompt}"
        
        async def generate_stream(self, prompt: str, **kwargs):
            yield "Chunk 1"
            yield "Chunk 2"
        
        async def chat(self, messages: list, **kwargs) -> str:
            return f"Response to: {messages[-1]['content']}"
        
        async def chat_stream(self, messages: list, **kwargs):
            yield "Response"
            yield "Stream"
        
        async def is_available(self) -> bool:
            return True
    
    return MockModel(model_id="test_model")


@pytest.fixture
def mock_registry(mock_model):
    """Fixture para ModelRegistry."""
    from src.models.registry import ModelRegistry
    
    registry = ModelRegistry()
    registry.register_model("test_model", mock_model)
    
    return registry


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture para directorio temporal."""
    return tmp_path


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singletons después de cada test."""
    from src.utils.config import _settings
    from src.models.registry import _registry
    
    # Reset antes del test
    import src.utils.config
    import src.models.registry
    
    src.utils.config._settings = None
    src.models.registry._registry = None
    
    yield
    
    # Reset después del test
    src.utils.config._settings = None
    src.models.registry._registry = None
