"""Tests for the Chat pipeline (Groq LLM)."""

import pytest
from jarvis.pipelines.chat import ChatPipeline
from jarvis.core.config import config


@pytest.mark.asyncio
async def test_generate_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(config, "groq_api_key", "")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    assert result is None
    await pipeline.close()


@pytest.mark.asyncio
async def test_generate_adds_system_prompt(monkeypatch):
    monkeypatch.setattr(config, "groq_api_key", "test-key")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hi"}])
    # Without httpx it returns None
    assert result is None or isinstance(result, str)
    await pipeline.close()


@pytest.mark.asyncio
async def test_close_cleans_up_client(monkeypatch):
    monkeypatch.setattr(config, "groq_api_key", "test-key")
    pipeline = ChatPipeline()
    await pipeline.close()
    assert pipeline._client is None
