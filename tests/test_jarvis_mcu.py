import pytest
from jarvis.core.engine import Engine


@pytest.mark.asyncio
async def test_engine_mcu_weather_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("what is the weather in Tokyo")
    assert isinstance(resp, str)
    assert len(resp) > 0
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_mcu_telemetry_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("suit status")
    assert "JARVIS System Telemetry" in resp
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_mcu_protocol_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("execute house party protocol")
    assert "House Party Protocol initiated" in resp
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_mcu_timer_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("set a timer for 10 seconds for tea")
    assert "Timer set" in resp
    await engine.shutdown()
