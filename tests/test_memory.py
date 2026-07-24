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
