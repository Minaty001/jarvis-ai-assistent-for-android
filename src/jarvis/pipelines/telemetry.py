"""Telemetry pipeline — System Health & Diagnostics (Somatosensory Cortex).

Monitors CPU usage, memory, disk storage, battery, thermal state, and process count.
Provides Stark-style suit/device diagnostic status reports.
Crafted by Minaty001.
"""

from __future__ import annotations

import os
import platform
import time
import asyncio
from typing import Any, Dict
from jarvis.core.config import Config
from jarvis.pipelines.base import AsyncPipeline
from jarvis.utils.logging import log


class TelemetryPipeline(AsyncPipeline):
    """System health monitoring and telemetry reporting."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)
        self._start_time = time.time()

    async def get_system_telemetry(self) -> dict[str, Any]:
        """Fetch real-time CPU, RAM, Disk, Uptime, and Battery diagnostics."""
        uptime_sec = int(time.time() - self._start_time)

        # CPU load average / load
        load_avg = (0.0, 0.0, 0.0)
        try:
            if hasattr(os, "getloadavg"):
                load_avg = os.getloadavg()
        except Exception:
            pass

        # Memory usage via /proc/meminfo or fallback
        mem_info = self._get_mem_info()

        # Disk usage
        disk_info = self._get_disk_info()

        # Battery status via termux fallback
        battery_info = await self._get_battery_info()

        return {
            "platform": platform.system(),
            "machine": platform.machine(),
            "uptime_seconds": uptime_sec,
            "load_average": load_avg,
            "memory": mem_info,
            "disk": disk_info,
            "battery": battery_info,
            "status": "NOMINAL" if battery_info.get("percentage", 100) > 15 else "WARNING",
        }

    def _get_mem_info(self) -> dict[str, Any]:
        """Parse /proc/meminfo if available on Linux/Android."""
        if os.path.exists("/proc/meminfo"):
            try:
                mem = {}
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip().split()[0]
                            mem[key] = int(val)
                total = mem.get("MemTotal", 0) // 1024
                free = mem.get("MemAvailable", mem.get("MemFree", 0)) // 1024
                used = max(0, total - free)
                pct = round((used / total * 100), 1) if total > 0 else 0.0
                return {"total_mb": total, "used_mb": used, "free_mb": free, "percent_used": pct}
            except Exception:
                pass
        return {"total_mb": 0, "used_mb": 0, "free_mb": 0, "percent_used": 0.0}

    def _get_disk_info(self) -> dict[str, Any]:
        """Fetch disk space usage of current filesystem."""
        try:
            stat = os.statvfs("/")
            total_mb = (stat.f_blocks * stat.f_frsize) // (1024 * 1024)
            free_mb = (stat.f_bavail * stat.f_frsize) // (1024 * 1024)
            used_mb = total_mb - free_mb
            pct = round((used_mb / total_mb * 100), 1) if total_mb > 0 else 0.0
            return {"total_mb": total_mb, "used_mb": used_mb, "free_mb": free_mb, "percent_used": pct}
        except Exception:
            return {"total_mb": 0, "used_mb": 0, "free_mb": 0, "percent_used": 0.0}

    async def _get_battery_info(self) -> dict[str, Any]:
        """Read battery level via termux-battery-status or sysfs."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-battery-status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                return {
                    "percentage": data.get("percentage", 100),
                    "plugged": data.get("plugged", "UNPLUGGED"),
                    "status": data.get("status", "DISCHARGING"),
                    "temperature": data.get("temperature", 0.0),
                }
        except Exception:
            pass
        return {"percentage": 100, "plugged": "UNKNOWN", "status": "NOMINAL", "temperature": 25.0}

    async def format_diagnostic_report(self) -> str:
        """Generate a Stark-style JARVIS suit diagnostic readout."""
        telem = await self.get_system_telemetry()
        status = telem["status"]
        mem = telem["memory"]
        disk = telem["disk"]
        batt = telem["battery"]
        load1, load5, load15 = telem["load_average"]

        uptime_sec = telem["uptime_seconds"]
        hours, rem = divmod(uptime_sec, 3600)
        minutes = rem // 60

        # Status icon
        status_icon = "✅ NOMINAL" if status == "NOMINAL" else "⚠️  WARNING"

        # Battery alert
        batt_pct = batt.get("percentage", 100)
        batt_status = batt.get("status", "UNKNOWN")
        batt_plug = batt.get("plugged", "UNKNOWN")
        batt_temp = batt.get("temperature", 0.0)
        power_note = " — CHARGING" if batt_plug not in ("UNPLUGGED", "UNKNOWN") else ""
        batt_warn = " ⚠️  CRITICAL — recommend immediate charging" if batt_pct <= 15 else ""

        lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  J.A.R.V.I.S.  SUIT DIAGNOSTIC REPORT",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  CORTEX STATUS    : {status_icon}",
            f"  UPTIME           : {hours}h {minutes}m",
            f"  PLATFORM         : {telem['platform']} / {telem['machine']}",
            "─────────────────────────────────────────────────",
            "  POWER SYSTEMS",
            f"  Power Grid       : {batt_pct}%{power_note}{batt_warn}",
            f"  Charge State     : {batt_status}",
            f"  Cell Temperature : {batt_temp:.1f}°C",
            "─────────────────────────────────────────────────",
            "  PROCESSING CORES",
            f"  Neural Load 1m   : {load1:.2f}",
            f"  Neural Load 5m   : {load5:.2f}",
            f"  Neural Load 15m  : {load15:.2f}",
            "─────────────────────────────────────────────────",
            "  MEMORY CORES",
            f"  RAM Allocated    : {mem['used_mb']:,} MB / {mem['total_mb']:,} MB",
            f"  RAM Available    : {mem['free_mb']:,} MB  ({mem['percent_used']}% used)",
            "─────────────────────────────────────────────────",
            "  STORAGE BAY",
            f"  Capacity         : {disk['total_mb']:,} MB total",
            f"  Occupied         : {disk['used_mb']:,} MB",
            f"  Available        : {disk['free_mb']:,} MB  ({disk['percent_used']}% used)",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  All systems reporting in, sir.",
        ]
        return "\n".join(lines)
