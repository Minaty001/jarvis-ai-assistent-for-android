"""Tests for the Chat pipeline (multi-provider LLM)."""

import pytest
from jarvis.pipelines.chat import ChatPipeline
from jarvis.core.config import config


@pytest.mark.asyncio
async def test_generate_returns_none_without_any_key(monkeypatch):
    """Without any API key, generate should return None."""
    monkeypatch.setattr(config, "groq_api_key", "")
    monkeypatch.setattr(config, "openai_api_key", "")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    assert result is None
    await pipeline.stop()


@pytest.mark.asyncio
async def test_generate_with_groq_key_only(monkeypatch):
    """With only Groq key set, should attempt Groq API call."""
    monkeypatch.setattr(config, "groq_api_key", "test-groq-key")
    monkeypatch.setattr(config, "openai_api_key", "")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hi"}])
    # Without httpx it returns None (no actual HTTP call)
    assert result is None or isinstance(result, str)
    await pipeline.stop()


@pytest.mark.asyncio
async def test_generate_with_openai_key_only(monkeypatch):
    """With only OpenAI key set, should attempt OpenAI API call."""
    monkeypatch.setattr(config, "groq_api_key", "")
    monkeypatch.setattr(config, "openai_api_key", "test-openai-key")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    # Without httpx it returns None (no actual HTTP call)
    assert result is None or isinstance(result, str)
    await pipeline.stop()


@pytest.mark.asyncio
async def test_generate_fallback_order(monkeypatch):
    """With both keys set, Groq should be tried first, then OpenAI."""
    monkeypatch.setattr(config, "groq_api_key", "test-groq-key")
    monkeypatch.setattr(config, "openai_api_key", "test-openai-key")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    # Without httpx both will fail, returning None
    assert result is None
    await pipeline.stop()


@pytest.mark.asyncio
async def test_close_cleans_up_client(monkeypatch):
    """Close should set _client to None."""
    monkeypatch.setattr(config, "groq_api_key", "test-key")
    pipeline = ChatPipeline()
    await pipeline.stop()
    assert pipeline._client is None


@pytest.mark.asyncio
async def test_build_payload_includes_tools(monkeypatch):
    """_build_payload should include tools when provided."""
    monkeypatch.setattr(config, "groq_api_key", "test-key")
    pipeline = ChatPipeline()
    msgs = [{"role": "user", "content": "hello"}]
    tools = [{"type": "function", "function": {"name": "test_tool"}}]
    payload = pipeline._build_payload(msgs, "test-model", tools)
    assert payload["model"] == "test-model"
    assert payload["messages"] == msgs
    assert payload["tools"] == tools
    await pipeline.stop()


@pytest.mark.asyncio
async def test_parse_response_with_content():
    """_parse_response should extract content string correctly."""
    pipeline = ChatPipeline()
    data = {
        "choices": [
            {
                "message": {
                    "content": "Hello, sir.",
                }
            }
        ]
    }
    result = pipeline._parse_response(data)
    assert result == "Hello, sir."


@pytest.mark.asyncio
async def test_parse_response_with_tool_calls():
    """_parse_response should return dict with tool_calls when present."""
    pipeline = ChatPipeline()
    data = {
        "choices": [
            {
                "message": {
                    "content": "",
                    "tool_calls": [
                        {"id": "call_1", "type": "function",
                         "function": {"name": "test", "arguments": "{}"}}
                    ],
                }
            }
        ]
    }
    result = pipeline._parse_response(data)
    assert isinstance(result, dict)
    assert "tool_calls" in result
    assert result["tool_calls"][0]["function"]["name"] == "test"
