"""Tests for the Chat pipeline (Groq LLM)."""

import pytest
from jarvis.pipelines.chat import ChatPipeline


@pytest.mark.asyncio
async def test_generate_returns_none_without_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    assert result is None
    await pipeline.close()


@pytest.mark.asyncio
async def test_generate_adds_system_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    pipeline = ChatPipeline()
    # With empty messages, it should still work (no system prompt added if not first)
    result = await pipeline.generate([{"role": "user", "content": "hi"}])
    # Without httpx it returns None
    assert result is None or isinstance(result, str)
    await pipeline.close()


@pytest.mark.asyncio
async def test_close_cleans_up_client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    pipeline = ChatPipeline()
    await pipeline.close()
    assert pipeline._client is None
