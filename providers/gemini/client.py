"""Google AI Studio Gemini provider (OpenAI-compatible chat completions)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from providers.base import ProviderConfig
from providers.defaults import GEMINI_DEFAULT_BASE
from providers.openai_compat import OpenAIChatTransport
from loguru import logger

from .request import build_request_body

_MAX_TOOL_CALL_EXTRA_CONTENT_CACHE = 4096

FREE_TIER_MODELS = [
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite"
]

class GeminiProvider(OpenAIChatTransport):
    """Gemini API using ``https://generativelanguage.googleapis.com/v1beta/openai/``."""

    def __init__(self, config: ProviderConfig):
        super().__init__(
            config,
            provider_name="GEMINI",
            base_url=config.base_url or GEMINI_DEFAULT_BASE,
            api_key=config.api_key,
        )
        self._tool_call_extra_content_by_id: dict[str, dict[str, Any]] = {}
        self._free_tier_models = FREE_TIER_MODELS
        self._current_model_idx = 0

    def _prepare_create_body(self, body: dict[str, Any]) -> dict[str, Any]:
        body = super()._prepare_create_body(body)
        body["model"] = self._free_tier_models[self._current_model_idx]
        return body

    def _rotate_key_on_429(self, exc: Exception = None) -> bool:
        # Rotación ultra-agresiva: Ante CUALQUIER error de Rate Limit (429), 
        # intentamos rotar al siguiente modelo gratuito en la misma API key primero.
        # Esto preserva nuestra investigación de evadir límites cambiando de modelo velozmente.
        next_model_idx = self._current_model_idx + 1
        if next_model_idx < len(self._free_tier_models):
            self._current_model_idx = next_model_idx
            logger.warning(f"Gemini Limit hit. Rotating MODEL to {self._free_tier_models[self._current_model_idx]} on same API Key.")
            return True
            
        logger.warning("All models exhausted for current API Key. Rotating API KEY...")
        rotated = self._config.mark_key_exhausted()
        if rotated:
            self._client.api_key = self._config.get_api_key()
            self._current_model_idx = 0
            logger.warning(f"Rotated to new API Key. Resetting model to {self._free_tier_models[0]}.")
            return True
            
        return False

    def _record_tool_call_extra_content(
        self, tool_call_id: str, extra_content: dict[str, Any]
    ) -> None:
        if (
            tool_call_id not in self._tool_call_extra_content_by_id
            and len(self._tool_call_extra_content_by_id)
            >= _MAX_TOOL_CALL_EXTRA_CONTENT_CACHE
        ):
            self._tool_call_extra_content_by_id.pop(
                next(iter(self._tool_call_extra_content_by_id))
            )
        self._tool_call_extra_content_by_id[tool_call_id] = deepcopy(extra_content)

    def _build_request_body(
        self, request: Any, thinking_enabled: bool | None = None
    ) -> dict:
        return build_request_body(
            request,
            thinking_enabled=self._is_thinking_enabled(request, thinking_enabled),
            tool_call_extra_content_by_id=self._tool_call_extra_content_by_id,
        )
