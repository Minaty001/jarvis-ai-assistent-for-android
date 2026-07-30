"""Tests for the Device pipeline (Termux:API control)."""

import pytest
from jarvis.services.device import DevicePipeline


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


@pytest.mark.asyncio
async def test_execute_take_screenshot_without_termux():
    pipeline = DevicePipeline()
    result = await pipeline.execute("take_screenshot", {})
    assert isinstance(result, str)
    assert "error" in result.lower() or "fail" in result.lower() or "unavailable" in result.lower() or "missing" in result.lower()


@pytest.mark.asyncio
async def test_execute_send_notification_without_termux():
    pipeline = DevicePipeline()
    result = await pipeline.execute("send_notification", {"content": "test"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_execute_airplane_mode_without_termux():
    pipeline = DevicePipeline()
    result = await pipeline.execute("airplane_mode", {"state": "on"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_execute_do_not_disturb_without_termux():
    pipeline = DevicePipeline()
    result = await pipeline.execute("do_not_disturb", {"state": "on"})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_execute_sensor_data_without_termux():
    pipeline = DevicePipeline()
    result = await pipeline.execute("sensor_data", {})
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_send_notification_no_content():
    pipeline = DevicePipeline()
    result = await pipeline.execute("send_notification", {})
    assert "specify" in result.lower()


@pytest.mark.asyncio
async def test_send_notification_no_title():
    pipeline = DevicePipeline()
    result = await pipeline.execute("send_notification", {"content": "hello"})
    assert isinstance(result, str)
