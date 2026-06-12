from __future__ import annotations

from providers.base import AIProvider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider


def get_provider(
    provider_name: str,
    gemini_key: str | None = None,
    ollama_url: str = "http://localhost:11434",
    ollama_model: str = "llama3.2",
) -> AIProvider:
    """Instantiate and return the appropriate AIProvider based on selection."""
    if provider_name == "Ollama":
        return OllamaProvider(base_url=ollama_url, model_name=ollama_model)
    else:
        return GeminiProvider(api_key=gemini_key)
