"""Chat pipeline — Multi-Provider LLM client (Wernicke's Area).

Primary: Groq API (llama-3.1-8b-instant).
Fallback: OpenAI API (gpt-4o-mini).
Retries on rate limits and timeout. Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from jarvis.core.config import Config, config as app_config
from jarvis.services.base import AsyncPipeline
from jarvis.utils.logging import log


class ChatPipeline(AsyncPipeline):
    """Async multi-provider LLM client for inference and function calling."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)
        self.timeout = self.config.groq_timeout
        self._client: Any = None
        self._openai_api_key = app_config.openai_api_key

    def _build_payload(self, messages: list[dict], model: str,
                       tools: list[dict] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": app_config.llm_temperature,
            "max_tokens": app_config.llm_max_tokens,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
        return payload

    def _parse_response(self, data: dict) -> dict | str | None:
        """Extract content and optional tool_calls from an OpenAI-compatible response."""
        try:
            msg = data["choices"][0]["message"]
            content = msg.get("content", "") or ""
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                return {"content": content.strip(), "tool_calls": tool_calls}
            return content.strip()
        except (KeyError, IndexError, TypeError) as e:
            log.error(f"Unexpected API response format: {e}")
            return None

    async def _ensure_client(self) -> bool:
        """Create the shared httpx client if not yet created."""
        if self._client is not None:
            return True
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            return True
        except ImportError:
            log.warning("httpx not installed. Chat pipeline unavailable.")
            return False

    async def _call_api(self, base_url: str, api_key: str, model: str,
                        messages: list[dict], tools: list[dict] | None = None,
                        provider_name: str = "LLM") -> dict | str | None:
        """Send a chat completion request to an OpenAI-compatible API.

        Returns:
            Response string or dict with tool_calls, or None on failure.
        """
        if not await self._ensure_client():
            return None

        payload = self._build_payload(messages, model, tools)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        url = f"{base_url.rstrip('/')}/chat/completions"

        for attempt in range(2):
            try:
                resp = await self._client.post(url, json=payload, headers=headers)
                if resp.status_code == 429:
                    log.warning(f"{provider_name} rate limited. Retrying...")
                    await asyncio.sleep(2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return self._parse_response(data)
            except Exception as e:
                log.error(f"{provider_name} API error (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    await asyncio.sleep(1)
                    continue
                return None

        return None

    async def generate(self, messages: list[dict],
                       tools: list[dict] | None = None) -> Optional[dict | str]:
        """Send messages to LLM and return response, with automatic provider fallback.

        Tries Groq API first. If Groq is unavailable or returns an error,
        falls back to OpenAI API (if OPENAI_API_KEY is configured).

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            tools: Optional list of OpenAI-compatible tool spec dicts.

        Returns:
            Response string, or dict with 'content' and optional 'tool_calls',
            or None if all providers fail.
        """
        # Try Groq (primary provider)
        groq_key = app_config.groq_api_key
        if groq_key:
            result = await self._call_api(
                base_url=app_config.groq_api_base,
                api_key=groq_key,
                model=app_config.model_name,
                messages=messages,
                tools=tools,
                provider_name="Groq",
            )
            if result is not None:
                return result
            log.info("Groq API failed — attempting OpenAI fallback.")
        else:
            log.debug("GROQ_API_KEY not set — skipping Groq.")

        # Fallback to OpenAI
        openai_key = self._openai_api_key or app_config.openai_api_key
        if openai_key:
            return await self._call_api(
                base_url=app_config.openai_api_base,
                api_key=openai_key,
                model=app_config.openai_model,
                messages=messages,
                tools=tools,
                provider_name="OpenAI",
            )

        if not groq_key and not openai_key:
            log.error("No LLM API key configured. Set GROQ_API_KEY or OPENAI_API_KEY in .env.")

        return None

    async def stop(self) -> None:
        """Close the HTTP client."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
        await super().stop()
