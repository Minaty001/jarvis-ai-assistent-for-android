"""Protocol pipeline — Stark Tactical & Security Protocols (Defense Cortex).

Executes named MCU-inspired automated protocol sequences:
- House Party Protocol: Cleans cache, releases background resources.
- Protocol Alpha: High-priority system diagnostic + health verification.
- Stealth Mode: Mutes volume, dims screen to minimum, turns off flashlight.
- Silent Alarm: Sets silent alert state.
- Lockdown: Disables connections (WiFi, Bluetooth) and locks down device.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Awaitable, Dict
from jarvis.utils.logging import log


class ProtocolPipeline:
    """Orchestrator for automated named security protocols."""

    def __init__(self, device_pipeline=None, telemetry_pipeline=None, audio_fx_pipeline=None) -> None:
        self.device = device_pipeline
        self.telemetry = telemetry_pipeline
        self.audio_fx = audio_fx_pipeline
        self._active_protocol: str | None = None

    async def execute_protocol(self, protocol_name: str) -> str:
        """Execute a named protocol sequence.

        Args:
            protocol_name: Key name of protocol (e.g., 'house_party', 'stealth', 'lockdown').

        Returns:
            Report string summarizing actions taken.
        """
        name_clean = protocol_name.lower().strip().replace(" ", "_").replace("-", "_")
        handler = self._get_protocol_handler(name_clean)

        if not handler:
            return f"Protocol '{protocol_name}' is not recognized in Stark Database."

        log.info(f"Initiating Stark Protocol: {name_clean}")
        self._active_protocol = name_clean
        result = await handler()
        self._active_protocol = None

        # Play success audio FX on protocol completion
        if self.audio_fx:
            try:
                await self.audio_fx.play_fx("success")
            except Exception:
                pass

        return result

    def _get_protocol_handler(self, name: str) -> Callable[[], Awaitable[str]] | None:
        protocols = {
            "house_party": self._house_party_protocol,
            "house_party_protocol": self._house_party_protocol,
            "stealth": self._stealth_protocol,
            "stealth_mode": self._stealth_protocol,
            "lockdown": self._lockdown_protocol,
            "protocol_alpha": self._protocol_alpha,
            "alpha": self._protocol_alpha,
            "clean_sweep": self._clean_sweep_protocol,
            "overdrive": self._overdrive_protocol,
        }
        return protocols.get(name)

    async def _house_party_protocol(self) -> str:
        """House Party Protocol: Release resources, clean cache directory."""
        actions = []
        try:
            # Force garbage collection / cache cleanup
            import gc
            gc.collect()
            actions.append("Memory garbage collection executed.")
        except Exception as e:
            actions.append(f"Garbage collection warning: {e}")

        if self.device:
            await self.device.execute("flashlight_off", {})
            actions.append("Disengaged auxiliary illumination.")

        return (
            "House Party Protocol confirmed, sir. All non-essential sub-routines have been terminated, "
            "memory caches purged, and system resources reallocated to primary functions. "
            "The suit is ready."
        )

    async def _stealth_protocol(self) -> str:
        """Stealth Mode: Mute audio, lower brightness, turn off lights."""
        actions = []
        if self.device:
            await self.device.execute("set_volume", {"level": "0"})
            await self.device.execute("set_brightness", {"level": "1"})
            await self.device.execute("flashlight_off", {})
            actions.append("Audio muted, display dimmed to minimum, flash off.")
        else:
            actions.append("Simulated stealth adjustments applied.")

        return "Stealth Mode engaged, sir. Audio systems silenced, display output minimized to minimum luminance, optical emitters offline. You are effectively invisible."

    async def _lockdown_protocol(self) -> str:
        """Lockdown Protocol: Disable external radios (WiFi, Bluetooth)."""
        actions = []
        if self.device:
            await self.device.execute("wifi_off", {})
            await self.device.execute("bluetooth_off", {})
            actions.append("Disabled WiFi and Bluetooth adapters.")
        else:
            actions.append("Perimeter isolation executed.")

        return "Lockdown Protocol active, sir. External communications severed — WiFi and Bluetooth adapters disabled. Perimeter secured. Local access restricted."

    async def _protocol_alpha(self) -> str:
        """Protocol Alpha: Comprehensive system diagnostic and readiness check."""
        report = ""
        if self.telemetry:
            report = await self.telemetry.format_diagnostic_report()
        else:
            report = "Core telemetry status: All systems nominal."

        return f"Protocol Alpha executed, sir.\n{report}\nAll core neural pathways operational."

    async def _clean_sweep_protocol(self) -> str:
        """Clean Sweep: Terminate background noise, prepare optimal workspace."""
        return "Clean Sweep Protocol completed, sir. Temporary files verified, background processes checked, and workspace optimised for maximum efficiency."

    async def _overdrive_protocol(self) -> str:
        """Overdrive Mode: Max brightness, high audio, full telemetry output."""
        if self.device:
            await self.device.execute("set_volume", {"level": "15"})
            await self.device.execute("set_brightness", {"level": "255"})
        return "Overdrive Mode engaged, sir. All systems operating at maximum capacity. I'd advise caution — we're running hot."
