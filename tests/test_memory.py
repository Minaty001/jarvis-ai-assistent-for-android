"""Tests for the Memory pipeline (SQLite storage)."""

import pytest
from jarvis.pipelines.memory import MemoryPipeline


@pytest.fixture
async def mem(tmp_path):
    db_path = str(tmp_path / "test.db")
    pipeline = MemoryPipeline(db_path=db_path)
    await pipeline.initialize()
    yield pipeline
    await pipeline.close()


@pytest.mark.asyncio
async def test_save_and_load_exchange(mem):
    await mem.save_exchange("user", "hello")
    await mem.save_exchange("assistant", "hi there")
    recent = await mem.load_recent(limit=10)
    assert len(recent) == 2
    assert recent[0]["role"] == "user"
    assert recent[0]["content"] == "hello"
    assert recent[1]["role"] == "assistant"
    assert recent[1]["content"] == "hi there"


@pytest.mark.asyncio
async def test_load_recent_respects_limit(mem):
    for i in range(5):
        await mem.save_exchange("user", f"msg{i}")
    recent = await mem.load_recent(limit=3)
    assert len(recent) == 3
    assert recent[-1]["content"] == "msg4"  # most recent last


@pytest.mark.asyncio
async def test_remember_and_recall(mem):
    await mem.remember("color", "blue")
    result = await mem.recall("color")
    assert result == "blue"


@pytest.mark.asyncio
async def test_recall_nonexistent(mem):
    result = await mem.recall("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_remember_overwrites(mem):
    await mem.remember("name", "Alice")
    await mem.remember("name", "Bob")
    result = await mem.recall("name")
    assert result == "Bob"


@pytest.mark.asyncio
async def test_get_facts(mem):
    await mem.remember("city", "Tokyo")
    await mem.remember("pet", "dog")
    facts = await mem.get_facts()
    assert "city: Tokyo" in facts
    assert "pet: dog" in facts


@pytest.mark.asyncio
async def test_get_facts_empty(mem):
    facts = await mem.get_facts()
    assert facts == ""


@pytest.mark.asyncio
async def test_build_context_includes_facts(mem):
    await mem.remember("name", "Jarvis")
    await mem.save_exchange("user", "hello")
    system_prompt, messages = await mem.build_context("what's my name?")
    assert "name: Jarvis" in system_prompt
    assert len(messages) >= 2  # system + user
    assert messages[-1]["content"] == "what's my name?"


@pytest.mark.asyncio
async def test_notes_crud(mem):
    note_id = await mem.save_note("Groceries", "buy milk and eggs")
    assert note_id > 0

    notes = await mem.get_notes()
    assert len(notes) == 1
    assert notes[0]["title"] == "Groceries"
    assert notes[0]["content"] == "buy milk and eggs"

    deleted = await mem.delete_note("milk")
    assert deleted is True

    notes_after = await mem.get_notes()
    assert len(notes_after) == 0


@pytest.mark.asyncio
async def test_reminders_crud(mem):
    rem_id = await mem.save_reminder("Call Doctor")
    assert rem_id > 0

    rems = await mem.get_reminders()
    assert len(rems) == 1
    assert rems[0]["text"] == "Call Doctor"

    deleted = await mem.delete_reminder("Doctor")
    assert deleted is True

    rems_after = await mem.get_reminders()
    assert len(rems_after) == 0


@pytest.mark.asyncio
async def test_delete_note_empty_query_safeguard(mem):
    await mem.save_note("Groceries", "buy milk")
    deleted = await mem.delete_note("")
    assert deleted is False
    deleted_spaces = await mem.delete_note("   ")
    assert deleted_spaces is False
    notes = await mem.get_notes()
    assert len(notes) == 1


@pytest.mark.asyncio
async def test_delete_reminder_empty_query_safeguard(mem):
    await mem.save_reminder("Call Doctor")
    deleted = await mem.delete_reminder("")
    assert deleted is False
    deleted_spaces = await mem.delete_reminder("   ")
    assert deleted_spaces is False
    rems = await mem.get_reminders()
    assert len(rems) == 1


@pytest.mark.asyncio
async def test_delete_custom_command_empty_query_safeguard(mem):
    await mem.add_custom_command("morning", "system_telemetry")
    deleted = await mem.delete_custom_command("")
    assert deleted is False
    deleted_spaces = await mem.delete_custom_command("   ")
    assert deleted_spaces is False
    cmds = await mem.list_custom_commands()
    assert len(cmds) == 1

