"""
Tests de rendimiento y optimización.
"""

import pytest
import time
import asyncio
from src.core.context import ContextManager
from src.models.registry import ModelRegistry
from unittest.mock import AsyncMock, MagicMock


class TestPerformance:
    """Tests de rendimiento."""
    
    def test_context_add_message_speed(self):
        """Test velocidad de agregar mensajes al contexto."""
        context = ContextManager()
        
        start = time.time()
        
        for i in range(10000):
            context.add_message("user", f"Message {i}")
        
        elapsed = time.time() - start
        
        # Debería ser muy rápido (menos de 0.5 segundos para 10k mensajes)
        assert elapsed < 0.5
        
        # Verificar límite
        assert len(context.history) == 50  # max_history default
    
    def test_context_get_messages_speed(self):
        """Test velocidad de obtener mensajes."""
        context = ContextManager()
        
        # Agregar mensajes
        for i in range(1000):
            context.add_message("user", f"Message {i}")
        
        # Medir tiempo de obtener mensajes
        start = time.time()
        
        for _ in range(1000):
            messages = context.get_messages()
        
        elapsed = time.time() - start
        
        # Debería ser muy rápido (menos de 0.1 segundos para 1k llamadas)
        assert elapsed < 0.1
    
    def test_context_export_import_speed(self):
        """Test velocidad de exportar e importar."""
        context = ContextManager()
        
        # Agregar muchos mensajes
        for i in range(1000):
            context.add_message("user", f"Message {i}")
        
        # Medir tiempo de exportación
        start = time.time()
        data = context.export_context()
        export_time = time.time() - start
        
        # Medir tiempo de importación
        start = time.time()
        context2 = ContextManager()
        context2.import_context(data)
        import_time = time.time() - start
        
        # Ambos deberían ser rápidos
        assert export_time < 0.1
        assert import_time < 0.1
    
    def test_registry_register_speed(self):
        """Test velocidad de registro de modelos."""
        from src.models.base import BaseModel
        
        class FastModel(BaseModel):
            async def generate(self, prompt: str, **kwargs) -> str:
                return "test"
            
            async def generate_stream(self, prompt: str, **kwargs):
                yield "test"
            
            async def chat(self, messages: list, **kwargs) -> str:
                return "test"
            
            async def chat_stream(self, messages: list, **kwargs):
                yield "test"
            
            async def is_available(self) -> bool:
                return True
        
        registry = ModelRegistry()
        
        start = time.time()
        
        for i in range(1000):
            model = FastModel(model_id=f"model_{i}")
            registry.register_model(f"model_{i}", model)
        
        elapsed = time.time() - start
        
        # Debería ser muy rápido
        assert elapsed < 0.5
    
    def test_registry_lookup_speed(self):
        """Test velocidad de búsqueda en registro."""
        from src.models.base import BaseModel
        
        class FastModel(BaseModel):
            async def generate(self, prompt: str, **kwargs) -> str:
                return "test"
            
            async def generate_stream(self, prompt: str, **kwargs):
                yield "test"
            
            async def chat(self, messages: list, **kwargs) -> str:
                return "test"
            
            async def chat_stream(self, messages: list, **kwargs):
                yield "test"
            
            async def is_available(self) -> bool:
                return True
        
        registry = ModelRegistry()
        
        # Registrar 1000 modelos
        for i in range(1000):
            model = FastModel(model_id=f"model_{i}")
            registry.register_model(f"model_{i}", model)
        
        # Medir tiempo de búsqueda
        start = time.time()
        
        for i in range(10000):
            model = registry.get_model(f"model_{i % 1000}")
        
        elapsed = time.time() - start
        
        # Debería ser muy rápido (O(1) lookup)
        assert elapsed < 0.1
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test operaciones concurrentes."""
        context = ContextManager()
        
        async def add_messages():
            for i in range(100):
                context.add_message("user", f"Message {i}")
                await asyncio.sleep(0)
        
        # Ejecutar concurrentemente
        tasks = [add_messages() for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Verificar que no hubo corrupción de datos
        assert len(context.history) == 50  # max_history default


class TestMemoryUsage:
    """Tests de uso de memoria."""
    
    def test_context_memory_efficiency(self):
        """Test eficiencia de memoria del contexto."""
        import sys
        
        context = ContextManager(max_history=100)
        
        # Agregar mensajes
        for i in range(100):
            context.add_message("user", f"Message {i}")
        
        # Tamaño del contexto
        size = sys.getsizeof(context.history)
        
        # Debería ser razonable (menos de 100 KB)
        assert size < 100000
    
    def test_registry_memory_efficiency(self):
        """Test eficiencia de memoria del registro."""
        import sys
        from src.models.base import BaseModel
        
        class FastModel(BaseModel):
            async def generate(self, prompt: str, **kwargs) -> str:
                return "test"
            
            async def generate_stream(self, prompt: str, **kwargs):
                yield "test"
            
            async def chat(self, messages: list, **kwargs) -> str:
                return "test"
            
            async def chat_stream(self, messages: list, **kwargs):
                yield "test"
            
            async def is_available(self) -> bool:
                return True
        
        registry = ModelRegistry()
        
        # Registrar muchos modelos
        for i in range(100):
            model = FastModel(model_id=f"model_{i}")
            registry.register_model(f"model_{i}", model)
        
        # Tamaño del registro
        size = sys.getsizeof(registry._models)
        
        # Debería ser razonable
        assert size < 50000


class TestOptimizations:
    """Tests de optimizaciones."""
    
    def test_context_pruning_optimization(self):
        """Test optimización de poda del contexto."""
        context = ContextManager(max_history=1000)
        
        # Agregar muchos mensajes
        for i in range(1000):
            context.add_message("user", f"Message {i}")
        
        # Medir tiempo de poda
        start = time.time()
        context.prune_context(keep_last=10)
        elapsed = time.time() - start
        
        # Debería ser rápido
        assert elapsed < 0.01
        
        # Verificar resultado
        assert len(context.history) == 10
    
    def test_context_get_summary_speed(self):
        """Test velocidad de obtener resumen."""
        context = ContextManager()
        
        # Agregar mensajes
        for i in range(1000):
            context.add_message("user", f"Message {i}")
        
        # Medir tiempo
        start = time.time()
        summary = context.get_summary()
        elapsed = time.time() - start
        
        # Debería ser rápido
        assert elapsed < 0.01
        
        # Verificar contenido
        assert "total_messages" in summary
        assert summary["total_messages"] == 50  # max_history default
