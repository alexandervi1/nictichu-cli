from typing import Any


class NictichuCore:
    def __init__(self, model_name: str = "gemma:7b", provider: str = "ollama"):
        self.model_name = model_name
        self.provider = provider
    
    async def initialize(self):
        print(f"Inicializando {self.model_name} con {self.provider}...")
        return True
    
    async def process_message(self, message: str) -> str:
        return f"Respuesta de {self.model_name}: {message}"
    
    async def shutdown(self):
        print("Cerrando conexiones...")
