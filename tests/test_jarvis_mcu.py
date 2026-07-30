import pytest
from brain.engine import Engine


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
    assert "DIAGNOSTIC REPORT" in resp
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_mcu_protocol_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("execute house party protocol")
    assert "House Party Protocol confirmed" in resp or "House Party" in resp
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_mcu_timer_intent():
    engine = Engine()
    await engine.initialize()
    resp = await engine.process("set a timer for 10 seconds for tea")
    assert "Timer set" in resp
    await engine.shutdown()
