import pytest
from jarvis.modules.search import SearchPipeline


@pytest.mark.asyncio
async def test_get_weather_handles_gracefully():
    search = SearchPipeline()
    res = await search.get_weather("London")
    assert isinstance(res, str)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_search_web_summary():
    search = SearchPipeline()
    res = await search.search_web_summary("Quantum computing")
    assert isinstance(res, str)
    assert len(res) > 0
