"""Ollama provider implementation."""

import httpx

from providers.base import ProviderConfig
from providers.defaults import OLLAMA_DEFAULT_BASE
from providers.model_listing import extract_ollama_model_ids
from providers.openai_compat import OpenAIChatTransport
from .request import build_request_body


class OllamaProvider(OpenAIChatTransport):
    """Ollama provider using OpenAI compatibility layer."""

    def __init__(self, config: ProviderConfig):
        base_url = config.base_url or OLLAMA_DEFAULT_BASE
        
        # Normalize the base URL to point to the OpenAI compatible /v1 endpoint
        # Users often enter http://localhost:11434 or https://ollama.com or https://ollama.com/api
        if base_url.endswith("/api"):
            base_url = base_url[:-4] + "/v1"
        elif not base_url.endswith("/v1") and not base_url.endswith("/v1/"):
            base_url = base_url.rstrip("/") + "/v1"

        super().__init__(
            config,
            provider_name="OLLAMA",
            base_url=base_url,
            api_key=config.api_key or "ollama"
        )

    def _build_request_body(
        self, request: object, thinking_enabled: bool | None = None
    ) -> dict:
        return build_request_body(
            request,
            thinking_enabled=self._is_thinking_enabled(request, thinking_enabled),
        )

    async def list_model_ids(self) -> frozenset[str]:
        """Return hardcoded models as requested by user."""
        return frozenset([
            "deepseek-v4-flash-free",
            "minimax-m3:cloud"
        ])
