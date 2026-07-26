import pytest
from jarvis.pipelines.protocol import ProtocolPipeline


@pytest.mark.asyncio
async def test_execute_unknown_protocol():
    proto = ProtocolPipeline()
    res = await proto.execute_protocol("invalid_protocol")
    assert "not recognized" in res


@pytest.mark.asyncio
async def test_execute_house_party_protocol():
    proto = ProtocolPipeline()
    res = await proto.execute_protocol("house_party")
    assert "House Party Protocol confirmed" in res


@pytest.mark.asyncio
async def test_execute_stealth_protocol():
    proto = ProtocolPipeline()
    res = await proto.execute_protocol("stealth")
    assert "Stealth Mode engaged" in res


@pytest.mark.asyncio
async def test_execute_protocol_alpha():
    proto = ProtocolPipeline()
    res = await proto.execute_protocol("protocol_alpha")
    assert "Protocol Alpha executed" in res
