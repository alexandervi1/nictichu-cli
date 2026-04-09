from collections import deque
from typing import Any


class ContextManager:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
    
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
    
    def get_messages(self):
        return list(self.history)
    
    def clear(self):
        self.history.clear()
