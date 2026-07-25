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


@pytest.mark.asyncio
async def test_engine_process_memory_and_notes(monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    engine.config.database_path = str(tmp_path / "engine_test.db")
    await engine.initialize()

    # Remember fact
    res1 = await engine.process("remember that my favorite color is blue")
    assert "remember" in res1.lower()
    fact = await engine.memory.recall("favorite color")
    assert fact == "blue"

    # Take note
    res2 = await engine.process("take a note buy groceries")
    assert "saved note" in res2.lower()

    # Read notes
    res3 = await engine.process("show my notes")
    assert "buy groceries" in res3.lower()

    # Delete note
    res4 = await engine.process("delete note groceries")
    assert "deleted" in res4.lower()

    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_reminders(monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    engine.config.database_path = str(tmp_path / "reminders_test.db")
    await engine.initialize()

    # Set reminder
    res1 = await engine.process("set a reminder to call Mom")
    assert "reminder" in res1.lower()

    # View reminders
    res2 = await engine.process("view my reminders")
    assert "call mom" in res2.lower()

    # Delete reminder
    res3 = await engine.process("delete reminder call Mom")
    assert "deleted" in res3.lower()

    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_calculate(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()

    res1 = await engine.process("calculate 12 * 8")
    assert "96" in res1

    res2 = await engine.process("what is 100 / 4")
    assert "25" in res2

    await engine.shutdown()
