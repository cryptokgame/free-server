"""Ollama provider implementation."""

import httpx

from providers.base import ProviderConfig
from providers.defaults import OLLAMA_DEFAULT_BASE
from providers.model_listing import extract_ollama_model_ids
from providers.openai_compat import OpenAIChatTransport
from core.openai.chat_request import build_request_body


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
        """Try the OpenAI /v1/models endpoint, fallback to native /api/tags if needed."""
        try:
            # First try the standard OpenAI compatible endpoint (/v1/models)
            response = await self._client.with_options(timeout=3.0).models.list()
            return frozenset(model.id for model in response.data)
        except Exception:
            # Fallback to Ollama's native /api/tags if /v1/models is missing or broken
            from urllib.parse import urlparse
            url = str(self._client.base_url)
            parsed = urlparse(url)
            # Find the root domain (e.g. https://ollama.com or http://localhost:11434)
            # by stripping the /v1 path that we appended
            base = f"{parsed.scheme}://{parsed.netloc}"
            
            async with httpx.AsyncClient(proxy=self._config.proxy or None, timeout=3.0) as http:
                headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key != "ollama" else {}
                response = await http.get(f"{base}/api/tags", headers=headers)
                response.raise_for_status()
                payload = response.json()
                
            return extract_ollama_model_ids(payload, provider_name=self._provider_name)
