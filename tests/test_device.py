"""Tests for the Device pipeline (Termux:API control)."""

import pytest
from jarvis.pipelines.device import DevicePipeline


@pytest.mark.asyncio
async def test_execute_tell_time():
    pipeline = DevicePipeline()
    result = await pipeline.execute("tell_time", {})
    assert "time" in result.lower() or ":" in result


@pytest.mark.asyncio
async def test_execute_tell_date():
    pipeline = DevicePipeline()
    result = await pipeline.execute("tell_date", {})
    assert "today" in result.lower() or "202" in result


@pytest.mark.asyncio
async def test_execute_unknown_intent_returns_error():
    pipeline = DevicePipeline()
    result = await pipeline.execute("nonexistent_intent", {})
    assert "unknown" in result.lower()


@pytest.mark.asyncio
async def test_execute_flashlight_on_without_termux():
    pipeline = DevicePipeline()
    # Without termux-api, should return error message, not crash
    result = await pipeline.execute("flashlight_on", {})
    assert isinstance(result, str)
