from typing import Any
from collections import deque
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger()


class ContextManager:
    """Gestor de contexto conversacional."""
    
    def __init__(
        self,
        max_history: int = 50,
        max_context_length: int = 100000,
        max_tokens: int = 4096
    ):
        self.max_history = max_history
        self.max_context_length = max_context_length
        self.max_tokens = max_tokens
        self.history: deque = deque(maxlen=max_history)
        self.metadata: dict[str, Any] = {}
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Agregar mensaje al contexto."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.history.append(message)
        
        logger.debug(f"Mensaje agregado: {role} - {content[:50]}...")
    
    def get_messages(self, limit: int | None = None) -> list[dict[str, str]]:
        """Obtener mensajes del historial."""
        messages = list(self.history)
        
        if limit:
            messages = messages[-limit:]
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    def get_full_context(self) -> list[dict[str, str]]:
        """Obtener contexto completo."""
        return self.get_messages()
    
    def get_last_n_messages(self, n: int) -> list[dict[str, str]]:
        """Obtener últimos N mensajes."""
        return self.get_messages(limit=n)
    
    def get_context_length(self) -> int:
        """Calcular longitud total del contexto en caracteres."""
        total_length = sum(
            len(msg["content"])
            for msg in self.history
        )
        return total_length
    
    def is_context_full(self) -> bool:
        """Verificar si el contexto está lleno."""
        return self.get_context_length() >= self.max_context_length
    
    def prune_context(self, keep_last: int = 10) -> None:
        """Podar contexto manteniendo últimos mensajes."""
        if len(self.history) > keep_last:
            messages_to_keep = list(self.history)[-keep_last:]
            self.history.clear()
            self.history.extend(messages_to_keep)
            
            logger.info(f"Contexto podado, manteniendo {keep_last} mensajes")
    
    def clear(self) -> None:
        """Limpiar contexto completo."""
        self.history.clear()
        self.metadata.clear()
        logger.info("Contexto limpiado")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Establecer metadata del contexto."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Obtener metadata del contexto."""
        return self.metadata.get(key, default)
    
    def export_context(self) -> dict[str, Any]:
        """Exportar contexto para persistencia."""
        return {
            "history": list(self.history),
            "metadata": self.metadata,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_context(self, context_data: dict[str, Any]) -> None:
        """Importar contexto desde persistencia."""
        self.history.clear()
        
        for message in context_data.get("history", []):
            self.history.append(message)
        
        self.metadata = context_data.get("metadata", {})
        
        logger.info(f"Contexto importado: {len(self.history)} mensajes")
    
    def get_summary(self) -> dict[str, Any]:
        """Obtener resumen del contexto."""
        return {
            "total_messages": len(self.history),
            "context_length": self.get_context_length(),
            "is_full": self.is_context_full(),
            "oldest_message": self.history[0]["timestamp"] if self.history else None,
            "newest_message": self.history[-1]["timestamp"] if self.history else None,
            "metadata_keys": list(self.metadata.keys())
        }
    
    def get_token_count(self) -> int:
        """Estimar número de tokens en el contexto."""
        total_chars = self.get_context_length()
        estimated_tokens = total_chars // 4
        return estimated_tokens
