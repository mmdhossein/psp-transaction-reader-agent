from semantic_kernel.contents.chat_history import ChatHistory
from typing import Optional

class ChatManager:
    def __init__(self, system_message: str = None):
        self.history = ChatHistory()
        self.default_system_message = system_message or self._get_default_system_message()
        self.history.add_system_message(self.default_system_message)
    
    def _get_default_system_message(self) -> str:
        return """You are a Payment Service Provider (PSP) transaction analyst assistant.
You help users analyze payment transaction data from CSV files.
Use the available functions to access and analyze transaction data.
Provide clear, accurate responses with proper number formatting.
When discussing money, always include currency symbols.
If a question is not related to transaction data, inform the user politely."""
    
    def add_user_message(self, message: str):
        self.history.add_user_message(message)
    
    def add_assistant_message(self, message: str):
        self.history.add_assistant_message(message)
    
    def clear(self):
        """Reset chat history"""
        self.history = ChatHistory()
        self.history.add_system_message(self.default_system_message)
    
    def get_history(self) -> ChatHistory:
        return self.history
