"""Tests for the Engine orchestrator."""

import pytest
from jarvis.core.engine import Engine


@pytest.mark.asyncio
async def test_engine_initializes_and_shuts_down(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    # All pipelines should be loaded
    assert engine.chat is not None
    assert engine.memory is not None
    assert engine.voice is not None
    assert engine.device is not None
    assert engine.speech is not None
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_returns_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("hello")
    assert isinstance(result, str)
    assert len(result) > 0
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_tell_time(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("what's the time")
    assert "time" in result.lower() or ":" in result
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_general_chat(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("tell me a joke")
    assert isinstance(result, str)
    await engine.shutdown()
