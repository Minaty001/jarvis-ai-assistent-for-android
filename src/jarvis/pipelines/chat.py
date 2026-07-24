"""Chat pipeline — Groq LLM client (Wernicke's Area).

Sends messages to Groq API and returns the response text.
Retries on rate limits and timeout. Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log


class ChatPipeline:
    """Async Groq API client for LLM inference."""

    def __init__(self) -> None:
        self.api_key = app_config.groq_api_key
        self.model = app_config.model_name
        self.base_url = app_config.groq_api_base
        self.timeout = app_config.groq_timeout
        self._client: Any = None

    async def generate(self, messages: list[dict]) -> Optional[str]:
        """Send messages to Groq and return the response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            Response text string, or None on failure.
        """
        if not self.api_key:
            log.error("GROQ_API_KEY not set.")
            return None

        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    timeout=self.timeout,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
            except ImportError:
                log.warning("httpx not installed. Chat pipeline unavailable.")
                return None

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
            "stream": False,
        }

        for attempt in range(2):
            try:
                resp = await self._client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                )
                if resp.status_code == 429:
                    log.warning("Groq rate limited. Retrying...")
                    await asyncio.sleep(2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                log.error(f"Groq API error (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    await asyncio.sleep(1)
                    continue
                return None

        return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
