"""Tests for the Engine orchestrator."""

import pytest
from pathlib import Path
from brain.engine import Engine


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
    assert "noted" in res1.lower() or "remember" in res1.lower() or "stored" in res1.lower()
    fact = await engine.memory.recall("favorite color")
    assert fact == "blue"

    # Take note
    res2 = await engine.process("take a note buy groceries")
    assert "logged" in res2.lower() or "note" in res2.lower()

    # Read notes
    res3 = await engine.process("show my notes")
    assert "buy groceries" in res3.lower()

    # Delete note
    res4 = await engine.process("delete note groceries")
    assert "purged" in res4.lower() or "deleted" in res4.lower() or "note" in res4.lower()

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
    assert "cleared" in res3.lower() or "deleted" in res3.lower() or "reminder" in res3.lower()

    await engine.shutdown()


@pytest.mark.asyncio
async def test_export_conversation(monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    engine.config.database_path = str(tmp_path / "export_test.db")
    await engine.initialize()

    await engine.memory.save_exchange("user", "Hello Jarvis")
    await engine.memory.save_exchange("assistant", "Good day, sir.")
    await engine.memory.save_exchange("user", "What's the weather?")

    export_path = tmp_path / "exports" / "test_export.txt"
    result_path, count = await engine.memory.export_conversation(export_path)
    assert result_path == str(export_path.resolve())
    assert count == 3
    assert export_path.exists()

    content = export_path.read_text()
    assert "Conversation Export" in content
    assert "Hello Jarvis" in content
    assert "Good day, sir." in content
    assert "What's the weather?" in content
    assert "You:" in content
    assert "JARVIS:" in content

    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_export_conversation(monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    engine.config.database_path = str(tmp_path / "engine_export_test.db")
    await engine.initialize()

    await engine.memory.save_exchange("user", "test message one")
    await engine.memory.save_exchange("assistant", "test response one")

    result = await engine.process("export conversation")
    assert "exported" in result.lower()
    assert "2 exchanges archived" in result.lower()

    # Check a file was actually written
    exports_dir = Path(engine.config.database_path).parent / "exports"
    assert list(exports_dir.glob("*.txt"))

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

    res3 = await engine.process("calculate 9**9**9**9")
    assert "Could not calculate" in res3 or "out of bounds" in res3

    await engine.shutdown()
