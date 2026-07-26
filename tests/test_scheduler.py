import pytest
import asyncio
from jarvis.pipelines.scheduler import SchedulerPipeline


@pytest.mark.asyncio
async def test_create_and_cancel_timer():
    scheduler = SchedulerPipeline()
    res = await scheduler.create_timer("Focus Time", 10.0)
    assert "Focus Time" in res

    timers = await scheduler.get_active_timers()
    assert len(timers) == 1
    assert timers[0]["label"] == "Focus Time"

    cancelled = await scheduler.cancel_timer("Focus")
    assert cancelled is True

    active_after = await scheduler.get_active_timers()
    assert len(active_after) == 0


@pytest.mark.asyncio
async def test_timer_completion():
    completed = []

    def callback():
        completed.append(True)

    scheduler = SchedulerPipeline()
    await scheduler.create_timer("Quick Alarm", 0.1, callback=callback)
    await asyncio.sleep(0.2)

    assert len(completed) == 1


@pytest.mark.asyncio
async def test_cancel_timer_empty_query_safeguard():
    scheduler = SchedulerPipeline()
    await scheduler.create_timer("Focus Time", 10.0)
    cancelled = await scheduler.cancel_timer("")
    assert cancelled is False
    cancelled_spaces = await scheduler.cancel_timer("   ")
    assert cancelled_spaces is False
    timers = await scheduler.get_active_timers()
    assert len(timers) == 1
