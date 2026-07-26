import pytest
from jarvis.pipelines.memory import MemoryPipeline
from jarvis.core.engine import Engine
from jarvis.core.intent import classify_intent


@pytest.mark.asyncio
async def test_custom_commands_memory_crud(tmp_path):
    db_path = str(tmp_path / "custom_cmd_test.db")
    memory = MemoryPipeline(db_path=db_path)
    await memory.initialize()

    # Add command
    res1 = await memory.add_custom_command("good night", "execute stealth mode")
    assert res1 > 0

    # Get command
    action = await memory.get_custom_command("Good Night")
    assert action == "execute stealth mode"

    # List commands
    cmds = await memory.list_custom_commands()
    assert len(cmds) == 1
    assert cmds[0]["trigger_phrase"] == "good night"

    # Delete command
    deleted = await memory.delete_custom_command("good night")
    assert deleted is True

    # Get deleted command
    action_after = await memory.get_custom_command("good night")
    assert action_after is None

    await memory.close()


def test_custom_command_intent_classification():
    intent1, params1 = classify_intent("add custom command 'morning protocol' to run stealth mode")
    assert intent1 == "add_custom_cmd"
    assert params1.get("trigger_phrase") == "morning protocol"
    assert params1.get("actions") == "run stealth mode"

    intent2, _ = classify_intent("list my custom commands")
    assert intent2 == "list_custom_cmds"

    intent3, params3 = classify_intent("delete custom command 'morning protocol'")
    assert intent3 == "delete_custom_cmd"
    assert params3.get("trigger_phrase") == "morning protocol"


@pytest.mark.asyncio
async def test_engine_executes_custom_command(tmp_path):
    engine = Engine()
    engine.config.database_path = str(tmp_path / "engine_custom_cmd.db")
    await engine.initialize()

    # Register custom command
    resp1 = await engine.process("add custom command 'arm suit' to execute protocol alpha")
    assert "registered" in resp1.lower() or "created" in resp1.lower() or "custom" in resp1.lower()

    # Execute custom command by speaking its trigger phrase
    resp2 = await engine.process("arm suit")
    assert "Protocol Alpha executed" in resp2

    await engine.shutdown()
