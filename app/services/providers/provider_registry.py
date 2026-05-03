from .base import LLMProvider
from .ollama import  OllamaAdapter

PROVIDER_REGISTRY = {
    LLMProvider.OLLAMA: OllamaAdapter,
}
