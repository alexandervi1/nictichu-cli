"""Modelos disponibles para NictichuCLI."""

from .base import BaseModel
from .registry import ModelRegistry, get_registry
from .ollama import OllamaModel
from .google_ai import GoogleAIModel
from .vertex_ai import VertexAIModel

__all__ = [
    "BaseModel",
    "ModelRegistry",
    "get_registry",
    "OllamaModel",
    "GoogleAIModel",
    "VertexAIModel",
]