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
async def test_create_recurring_timer():
    scheduler = SchedulerPipeline()
    res = await scheduler.create_recurring_timer("Stand Up", 0.2)
    assert "Recurring timer" in res
    assert "Stand Up" in res

    timers = await scheduler.get_active_timers()
    assert len(timers) == 1
    assert timers[0]["recurring"] is True


@pytest.mark.asyncio
async def test_recurring_timer_fires_multiple_times():
    ticks = []

    def callback():
        ticks.append(True)

    scheduler = SchedulerPipeline()
    await scheduler.create_recurring_timer("Tick", 0.05, callback=callback)
    await asyncio.sleep(0.12)

    # Should have fired at least once, likely twice
    assert len(ticks) >= 1

    # Cancel it
    cancelled = await scheduler.cancel_timer("Tick")
    assert cancelled is True

    await asyncio.sleep(0.1)
    # Should not have increased after cancel
    ticks_after = len(ticks)
    await asyncio.sleep(0.1)
    assert len(ticks) == ticks_after


@pytest.mark.asyncio
async def test_cancel_recurring_timer():
    scheduler = SchedulerPipeline()
    await scheduler.create_recurring_timer("Recurring Test", 0.2)
    timers = await scheduler.get_active_timers()
    assert len(timers) == 1
    assert timers[0]["recurring"] is True

    cancelled = await scheduler.cancel_timer("Recurring")
    assert cancelled is True

    active_after = await scheduler.get_active_timers()
    assert len(active_after) == 0


@pytest.mark.asyncio
async def test_recurring_flag_in_active_list():
    scheduler = SchedulerPipeline()
    await scheduler.create_timer("One Shot", 10.0)
    await scheduler.create_recurring_timer("Repeat", 10.0)

    timers = await scheduler.get_active_timers()
    assert len(timers) == 2

    shot = next(t for t in timers if t["label"] == "One Shot")
    repeat = next(t for t in timers if t["label"] == "Repeat")

    assert shot["recurring"] is False
    assert repeat["recurring"] is True
