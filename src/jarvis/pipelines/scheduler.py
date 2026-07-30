"""Scheduler pipeline — Proactive Timers & Background Reminders (Cerebellum Clock).

Manages active async countdown timers, scheduled tasks, and alert callbacks.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Optional, Dict, Any, Union
from jarvis.core.config import Config
from jarvis.pipelines.base import AsyncPipeline
from jarvis.utils.logging import log


class ScheduledTask:
    """Represents an active background task / timer."""

    def __init__(self, task_id: str, label: str, duration_sec: float, callback: Optional[Callable[[], Any]] = None, recurring: bool = False) -> None:
        self.task_id = task_id
        self.label = label
        self.duration_sec = duration_sec
        self.callback = callback
        self.remaining_sec = duration_sec
        self.completed = False
        self.recurring = recurring
        self._async_task: Optional[asyncio.Task] = None


class SchedulerPipeline(AsyncPipeline):
    """Async background task scheduler and countdown manager."""

    def __init__(self, config: Config | None = None, voice_pipeline=None, audio_fx_pipeline=None) -> None:
        super().__init__(config)
        self.tasks: dict[str, ScheduledTask] = {}
        self._next_id = 1
        self.voice = voice_pipeline
        self.audio_fx = audio_fx_pipeline

    async def create_timer(self, label: str, seconds: float, callback: Optional[Callable[[], Any]] = None) -> str:
        """Create and start a countdown timer.

        Args:
            label: Human-readable timer description (e.g. 'Coffee break').
            seconds: Duration in seconds.
            callback: Optional sync or async function to call when timer expires.

        Returns:
            Task creation confirmation message.
        """
        return await self._create_timer(label, seconds, callback, recurring=False)

    async def create_recurring_timer(self, label: str, seconds: float, callback: Optional[Callable[[], Any]] = None) -> str:
        """Create and start a recurring countdown timer that repeats until cancelled.

        Args:
            label: Human-readable timer description (e.g. 'Stand up').
            seconds: Interval in seconds between repetitions.
            callback: Optional sync or async function to call on each tick.

        Returns:
            Task creation confirmation message.
        """
        return await self._create_timer(label, seconds, callback, recurring=True)

    async def _create_timer(self, label: str, seconds: float, callback: Optional[Callable[[], Any]] = None, recurring: bool = False) -> str:
        """Internal: create and start a timer (one-shot or recurring)."""
        task_id = f"timer_{self._next_id}"
        self._next_id += 1

        sched_task = ScheduledTask(task_id, label, seconds, callback, recurring=recurring)
        self.tasks[task_id] = sched_task

        # Launch async task
        sched_task._async_task = asyncio.create_task(self._run_timer(sched_task))
        log.info(f"Timer created [{task_id}]: '{label}' for {seconds} seconds{' (recurring)' if recurring else ''}.")

        min_val = round(seconds / 60, 1)
        if min_val >= 1.0:
            interval_str = f"every {min_val} minutes" if recurring else f"{min_val} minutes"
            return f"{'Recurring timer' if recurring else 'Timer'} set for {interval_str}: '{label}'."
        interval_str = f"every {int(seconds)} seconds" if recurring else f"{int(seconds)} seconds"
        return f"{'Recurring timer' if recurring else 'Timer'} set for {interval_str}: '{label}'."

    async def _run_timer(self, task: ScheduledTask) -> None:
        """Internal worker loop for counting down timer."""
        try:
            while True:
                await asyncio.sleep(task.duration_sec)
                if task.completed:
                    break
                log.info(f"Timer expired [{task.task_id}]: {task.label}")

                # Voice alert when timer expires
                alert_msg = f"Sir, your {task.label} timer has completed."
                if task.recurring:
                    alert_msg = f"Sir, your recurring {task.label} timer. Interval completed."

                if self.audio_fx:
                    try:
                        await self.audio_fx.play_fx("success")
                    except Exception:
                        pass
                if self.voice:
                    try:
                        await self.voice.speak(alert_msg)
                    except Exception:
                        pass
                else:
                    log.info(f"JARVIS Timer Alert: {alert_msg}")

                if task.callback:
                    if inspect.iscoroutinefunction(task.callback):
                        await task.callback()
                    else:
                        task.callback()

                if not task.recurring:
                    task.completed = True
                    break
                # For recurring timers: loop back for another interval
        except asyncio.CancelledError:
            log.info(f"Timer cancelled [{task.task_id}]: {task.label}")
        finally:
            task.completed = True

    async def get_active_timers(self) -> list[dict[str, Any]]:
        """Return list of active countdown timers."""
        active = []
        for tid, t in self.tasks.items():
            if not t.completed and t._async_task and not t._async_task.done():
                active.append({
                    "id": tid,
                    "label": t.label,
                    "duration_sec": t.duration_sec,
                    "recurring": t.recurring,
                })
        return active

    async def cancel_timer(self, query: str) -> bool:
        """Cancel timer(s) matching query string."""
        cancelled = False
        for tid, t in list(self.tasks.items()):
            if not t.completed and (query.lower() in t.label.lower() or query.lower() in tid.lower()):
                if t._async_task:
                    t._async_task.cancel()
                t.completed = True
                cancelled = True
        return cancelled
