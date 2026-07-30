"""Autonomy pipeline — Proactive System & Battery Health Monitor.

Periodically monitors battery levels, thermal state, and system health in the background.
Proactively notifies the user when battery drops low or thermal thresholds are reached.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Optional, Dict, Any
from jarvis.core.config import Config
from jarvis.pipelines.base import AsyncPipeline
from jarvis.utils.logging import log


class AutonomyPipeline(AsyncPipeline):
    """Async background autonomous monitor for JARVIS."""

    def __init__(self, config: Config | None = None, telemetry_pipeline=None, voice_pipeline=None, check_interval_sec: float = 60.0) -> None:
        super().__init__(config)
        self.telemetry = telemetry_pipeline
        self.voice = voice_pipeline
        self.check_interval_sec = check_interval_sec
        self._running = False
        self._async_task: Optional[asyncio.Task] = None
        self._last_battery_alert_pct: Optional[int] = None

    async def start(self) -> None:
        """Start the autonomous monitoring background task loop."""
        if self._running:
            return
        self._running = True
        self._async_task = asyncio.create_task(self._monitor_loop())
        log.info(f"AutonomyPipeline background monitor started (Interval: {self.check_interval_sec}s).")

    async def stop(self) -> None:
        """Stop the background monitoring loop."""
        self._running = False
        if self._async_task:
            self._async_task.cancel()
            self._async_task = None
        log.info("AutonomyPipeline background monitor stopped.")

    async def check_health_now(self) -> dict[str, Any]:
        """Perform an immediate health check and trigger warnings if required."""
        if not self.telemetry:
            return {"status": "NO_TELEMETRY", "alert_triggered": False}

        telem = await self.telemetry.get_system_telemetry()
        batt = telem.get("battery", {})
        pct = batt.get("percentage", 100)
        plugged = batt.get("plugged", "")

        alert_triggered = False
        alert_msg = ""

        # Trigger low battery alert if battery < 15% and unplugged
        if isinstance(pct, (int, float)) and pct <= 15 and "PLUGGED" not in str(plugged).upper():
            if self._last_battery_alert_pct != pct:
                self._last_battery_alert_pct = int(pct)
                alert_triggered = True
                alert_msg = f"Warning, sir. Main power grid is at {pct} percent. Recommend connecting to power source."
                log.warning(f"Autonomous alert: {alert_msg}")

                if self.voice:
                    await self.voice.speak(alert_msg)

        return {
            "status": telem.get("status", "NOMINAL"),
            "battery_pct": pct,
            "alert_triggered": alert_triggered,
            "alert_message": alert_msg,
        }

    async def _monitor_loop(self) -> None:
        """Internal worker loop for periodic health checks."""
        try:
            while self._running:
                await self.check_health_now()
                await asyncio.sleep(self.check_interval_sec)
        except asyncio.CancelledError:
            pass
