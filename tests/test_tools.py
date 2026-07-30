import pytest
from ai.tools import JARVIS_TOOL_SCHEMAS, execute_llm_tool_call
from brain.engine import Engine


def test_tool_schemas_validity():
    assert len(JARVIS_TOOL_SCHEMAS) >= 9
    names = [t["function"]["name"] for t in JARVIS_TOOL_SCHEMAS]
    assert "get_weather" in names
    assert "system_telemetry" in names
    assert "execute_protocol" in names
    assert "set_timer" in names
    assert "web_search_intel" in names
    assert "copy_clipboard" in names
    assert "get_clipboard" in names
    assert "take_note" in names
    assert "view_reminders" in names
    for tool in JARVIS_TOOL_SCHEMAS:
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]


@pytest.mark.asyncio
async def test_execute_llm_tool_call():
    engine = Engine()
    await engine.initialize()

    tool_call_weather = {
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "Tokyo"}'
        }
    }
    res_weather = await execute_llm_tool_call(engine, tool_call_weather)
    assert isinstance(res_weather, str)
    assert len(res_weather) > 0

    tool_call_telem = {
        "function": {
            "name": "system_telemetry",
            "arguments": "{}"
        }
    }
    res_telem = await execute_llm_tool_call(engine, tool_call_telem)
    assert "DIAGNOSTIC REPORT" in res_telem or "POWER SYSTEMS" in res_telem

    tool_call_proto = {
        "function": {
            "name": "execute_protocol",
            "arguments": '{"protocol_name": "stealth"}'
        }
    }
    res_proto = await execute_llm_tool_call(engine, tool_call_proto)
    assert "Stealth Mode engaged" in res_proto

    await engine.shutdown()


@pytest.mark.asyncio
async def test_execute_new_tools():
    """Test the new tool handlers: get_clipboard, take_note, view_reminders."""
    engine = Engine()
    await engine.initialize()

    # get_clipboard
    tc_clip = {"function": {"name": "get_clipboard", "arguments": "{}"}}
    res_clip = await execute_llm_tool_call(engine, tc_clip)
    assert isinstance(res_clip, str)

    # take_note
    tc_note = {"function": {"name": "take_note", "arguments": '{"content": "test note content"}'}}
    res_note = await execute_llm_tool_call(engine, tc_note)
    assert "saved" in res_note.lower()

    # view_reminders
    tc_rem = {"function": {"name": "view_reminders", "arguments": "{}"}}
    res_rem = await execute_llm_tool_call(engine, tc_rem)
    assert isinstance(res_rem, str)

    await engine.shutdown()
