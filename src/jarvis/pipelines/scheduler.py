"""Scheduler pipeline — Proactive Timers & Background Reminders (Cerebellum Clock).

Manages active async countdown timers, scheduled tasks, and alert callbacks.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Optional, Dict, Any
from jarvis.utils.logging import log


class ScheduledTask:
    """Represents an active background task / timer."""

    def __init__(self, task_id: str, label: str, duration_sec: float, callback: Optional[Callable[[], Any]] = None) -> None:
        self.task_id = task_id
        self.label = label
        self.duration_sec = duration_sec
        self.callback = callback
        self.remaining_sec = duration_sec
        self.completed = False
        self._async_task: Optional[asyncio.Task] = None


class SchedulerPipeline:
    """Async background task scheduler and countdown manager."""

    def __init__(self) -> None:
        self.tasks: dict[str, ScheduledTask] = {}
        self._next_id = 1

    async def create_timer(self, label: str, seconds: float, callback: Optional[Callable[[], Any]] = None) -> str:
        """Create and start a countdown timer.

        Args:
            label: Human-readable timer description (e.g. 'Coffee break').
            seconds: Duration in seconds.
            callback: Optional sync or async function to call when timer expires.

        Returns:
            Task creation confirmation message.
        """
        task_id = f"timer_{self._next_id}"
        self._next_id += 1

        sched_task = ScheduledTask(task_id, label, seconds, callback)
        self.tasks[task_id] = sched_task

        # Launch async task
        sched_task._async_task = asyncio.create_task(self._run_timer(sched_task))
        log.info(f"Timer created [{task_id}]: '{label}' for {seconds} seconds.")

        min_val = round(seconds / 60, 1)
        if min_val >= 1.0:
            return f"Timer set for {min_val} minutes: '{label}'."
        return f"Timer set for {int(seconds)} seconds: '{label}'."

    async def _run_timer(self, task: ScheduledTask) -> None:
        """Internal worker loop for counting down timer."""
        try:
            await asyncio.sleep(task.duration_sec)
            task.completed = True
            log.info(f"Timer expired [{task.task_id}]: {task.label}")
            if task.callback:
                if inspect.iscoroutinefunction(task.callback):
                    await task.callback()
                else:
                    task.callback()
        except asyncio.CancelledError:
            log.info(f"Timer cancelled [{task.task_id}]: {task.label}")

    async def get_active_timers(self) -> list[dict[str, Any]]:
        """Return list of active countdown timers."""
        active = []
        for tid, t in self.tasks.items():
            if not t.completed and t._async_task and not t._async_task.done():
                active.append({
                    "id": tid,
                    "label": t.label,
                    "duration_sec": t.duration_sec,
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
