import pytest
from jarvis.core.tools import JARVIS_TOOL_SCHEMAS, execute_llm_tool_call
from jarvis.core.engine import Engine


def test_tool_schemas_validity():
    assert len(JARVIS_TOOL_SCHEMAS) >= 5
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
    assert "JARVIS System Telemetry" in res_telem

    tool_call_proto = {
        "function": {
            "name": "execute_protocol",
            "arguments": '{"protocol_name": "stealth"}'
        }
    }
    res_proto = await execute_llm_tool_call(engine, tool_call_proto)
    assert "Stealth Mode engaged" in res_proto

    await engine.shutdown()
