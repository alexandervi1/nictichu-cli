"""
Tests de integración.
"""

import pytest
import asyncio
from src.core.core import NictichuCore
from src.core.context import ContextManager
from src.models.base import BaseModel
from unittest.mock import AsyncMock, MagicMock, patch


class MockModel(BaseModel):
    """Modelo mock para testing."""
    
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


@pytest.mark.asyncio
class TestIntegration:
    """Tests de integración."""
    
    async def test_core_with_context(self):
        """Test core con contexto conversacional."""
        # Crear contexto
        context = ContextManager(max_history=10)
        
        # Agregar mensajes al contexto
        context.add_message("user", "Hola")
        context.add_message("assistant", "¡Hola! ¿En qué puedo ayudarte?")
        
        # Crear core con modelo mock
        core = NictichuCore(model_name="test", provider="mock")
        core.model = MockModel(model_id="test")
        
        # Procesar mensaje con contexto
        response = await core.process_message(
            "¿Cómo estás?",
            context=context.get_messages()
        )
        
        assert "Response to:" in response
        
        # Verificar contexto
        messages = context.get_messages()
        assert len(messages) == 2
    
    async def test_context_persistence(self):
        """Test persistencia del contexto."""
        context = ContextManager(max_history=5)
        
        # Agregar varios mensajes
        for i in range(10):
            context.add_message("user", f"Message {i}")
        
        # Verificar que solo se mantienen los últimos 5
        assert len(context.history) == 5
        
        messages = context.get_messages()
        assert messages[0]["content"] == "Message 5"
        assert messages[-1]["content"] == "Message 9"
    
    async def test_context_export_import(self):
        """Test exportar e importar contexto."""
        context1 = ContextManager()
        
        # Agregar mensajes
        context1.add_message("user", "Test message")
        context1.set_metadata("key", "value")
        
        # Exportar
        data = context1.export_context()
        
        assert "history" in data
        assert "metadata" in data
        
        # Importar en nuevo contexto
        context2 = ContextManager()
        context2.import_context(data)
        
        assert len(context2.history) == 1
        assert context2.get_metadata("key") == "value"
    
    async def test_multiple_conversations(self):
        """Test múltiples conversaciones."""
        # Contexto 1
        context1 = ContextManager()
        context1.add_message("user", "Conversation 1")
        
        # Contexto 2
        context2 = ContextManager()
        context2.add_message("user", "Conversation 2")
        
        # Verificar que son independientes
        assert len(context1.history) == 1
        assert len(context2.history) == 1
        assert context1.history[0]["content"] == "Conversation 1"
        assert context2.history[0]["content"] == "Conversation 2"


@pytest.mark.asyncio
class TestModelSwitching:
    """Tests de cambio de modelos."""
    
    async def test_switch_models(self):
        """Test cambiar entre modelos."""
        core = NictichuCore(model_name="model1", provider="test")
        
        # Modelo inicial
        assert core.model_name == "model1"
        
        # Cambiar modelo
        core.model_name = "model2"
        assert core.model_name == "model2"
        
        # Verificar que el core puede manejar el cambio
        core.model = MockModel(model_id="model2")
        assert core.model.model_id == "model2"


@pytest.mark.asyncio
class TestErrorHandling:
    """Tests de manejo de errores."""
    
    async def test_model_not_available(self):
        """Test modelo no disponible."""
        model = MockModel(model_id="test")
        model.is_available = AsyncMock(return_value=False)
        
        core = NictichuCore(model_name="test", provider="mock")
        core.model = model
        
        # El core debería manejar modelo no disponible
        available = await core.model.is_available()
        assert available is False
    
    async def test_context_limit_reached(self):
        """Test límite de contexto alcanzado."""
        context = ContextManager(max_history=2)
        
        context.add_message("user", "Message 1")
        context.add_message("user", "Message 2")
        context.add_message("user", "Message 3")
        
        # Verificar límite
        assert len(context.history) == 2
    
    async def test_empty_context(self):
        """Test contexto vacío."""
        context = ContextManager()
        
        messages = context.get_messages()
        assert len(messages) == 0
        
        summary = context.get_summary()
        assert summary["total_messages"] == 0


@pytest.mark.asyncio
class TestPerformance:
    """Tests de rendimiento."""
    
    async def test_context_performance(self):
        """Test rendimiento del contexto."""
        import time
        
        context = ContextManager()
        
        start = time.time()
        
        # Agregar muchos mensajes
        for i in range(1000):
            context.add_message("user", f"Message {i}")
        
        elapsed = time.time() - start
        
        # Debería ser rápido (menos de 1 segundo)
        assert elapsed < 1.0
        
        # Verificar límite
        assert len(context.history) == 50  # max_history default
    
    async def test_context_memory_usage(self):
        """Test uso de memoria del contexto."""
        context = ContextManager(max_history=100)
        
        # Agregar muchos mensajes
        for i in range(1000):
            context.add_message("user", "A" * 100)  # 100 caracteres
        
        # Verificar longitud
        length = context.get_context_length()
        
        # Debería estar dentro del límite
        assert length <= context.max_context_length
    
    async def test_context_pruning(self):
        """Test poda del contexto."""
        context = ContextManager(max_history=100)
        
        # Agregar muchos mensajes
        for i in range(100):
            context.add_message("user", f"Message {i}")
        
        # Poda
        context.prune_context(keep_last=10)
        
        # Verificar que solo quedan 10
        assert len(context.history) == 10
