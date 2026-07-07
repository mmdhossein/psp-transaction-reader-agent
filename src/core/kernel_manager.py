import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory

class KernelManager:
    def __init__(self):
        self.kernel = None
        self.chat_service = None
        self.current_api_key = None
    
    def setup(self, api_key: str, base_url: str = None, model: str = None):
        """Initialize Semantic Kernel with OpenAI-compatible service"""
        if self.current_api_key == api_key and self.kernel is not None:
            return
        
        os.environ["OPENAI_API_KEY"] = api_key
        
        if base_url:
            os.environ["OPENAI_BASE_URL"] = base_url
        
        if model:
            os.environ["OPENAI_CHAT_MODEL_ID"] = model
        
        self.kernel = Kernel()
        self.chat_service = OpenAIChatCompletion(service_id="chat_service")
        self.kernel.add_service(self.chat_service)
        self.current_api_key = api_key
    
    def add_plugin(self, plugin, plugin_name: str):
        """Register a plugin with the kernel"""
        if self.kernel:
            self.kernel.add_plugin(plugin, plugin_name=plugin_name)
    
    def get_kernel(self) -> Kernel:
        return self.kernel
    
    def get_chat_service(self) -> OpenAIChatCompletion:
        return self.chat_service
