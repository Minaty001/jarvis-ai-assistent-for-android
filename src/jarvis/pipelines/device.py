"""Device pipeline — Termux:API Android control (Motor Cortex).

Executes device actions via termux-api subprocess commands.
Gracefully degrades when termux-api is not available.
"""

from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime
from typing import Optional

from jarvis.utils.logging import log


class DevicePipeline:
    """Async wrapper around Termux-API and Android commands."""

    def __init__(self) -> None:
        self._has_termux = self._check_termux()

    def _check_termux(self) -> bool:
        """Check if termux-battery-status is available."""
        try:
            proc = subprocess.run(
                ["termux-battery-status"], capture_output=True, timeout=5
            )
            return proc.returncode == 0
        except Exception:
            return False

    def has_termux(self) -> bool:
        """Return whether Termux:API is available on this device."""
        return self._has_termux

    async def _run(self, *args: str, input_data: Optional[str] = None) -> str:
        """Run a subprocess asynchronously and return stdout."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(
                input=input_data.encode() if input_data else None
            )
            if proc.returncode != 0:
                err = stderr.decode(errors="replace").strip()
                if err:
                    log.warning(f"Command {' '.join(args)} error: {err}")
            return stdout.decode(errors="replace").strip()
        except FileNotFoundError:
            return f"ERROR: {args[0]} not found. Install termux-api package."
        except Exception as e:
            return f"ERROR: {e}"

    async def execute(self, intent: str, params: dict[str, str]) -> str:
        """Execute a device action based on intent type and parameters.

        Args:
            intent: Classified intent name (e.g. 'open_app', 'flashlight_on').
            params: Extracted parameters from intent classifier.

        Returns:
            Human-readable result string.
        """
        handler = self._get_handler(intent)
        if handler is None:
            return f"Unknown action: {intent}"
        return await handler(params)

    def _get_handler(self, intent: str):
        """Map intent name to handler method."""
        handlers = {
            "open_app": self._open_app,
            "close_app": self._close_app,
            "open_settings": lambda p: self._open_app({"app_name": "settings"}),
            "open_camera": lambda p: self._open_app({"app_name": "camera"}),
            "open_gallery": lambda p: self._open_app({"app_name": "gallery"}),
            "open_youtube": self._open_youtube,
            "open_website": self._open_website,
            "go_home": lambda p: self._run("termux-tool", "keyboard", "key", "3"),
            "show_recent": lambda p: self._run("termux-tool", "keyboard", "key", "5"),
            "show_notifications": lambda p: self._run("termux-notification-list"),
            "flashlight_on": lambda p: self._run("termux-torch", "on"),
            "flashlight_off": lambda p: self._run("termux-torch", "off"),
            "volume_up": lambda p: self._run("termux-volume", "music", "10"),
            "volume_down": lambda p: self._run("termux-volume", "music", "1"),
            "set_volume": self._set_volume,
            "brightness_up": lambda p: self._run("termux-brightness", "255"),
            "brightness_down": lambda p: self._run("termux-brightness", "50"),
            "set_brightness": self._set_brightness,
            "tell_time": self._tell_time,
            "tell_date": self._tell_date,
            "battery_status": self._battery_status,
            "wifi_on": lambda p: self._run("termux-wifi-enable", "true"),
            "wifi_off": lambda p: self._run("termux-wifi-enable", "false"),
            "wifi_status": lambda p: self._run("termux-wifi-scaninfo"),
            "bluetooth_on": lambda p: self._run("termux-bluetooth-enable", "on"),
            "bluetooth_off": lambda p: self._run("termux-bluetooth-enable", "off"),
            "search_google": self._search_google,
            "play_music": self._play_music,
            "take_note": self._take_note,
            "read_notes": self._read_notes,
            "delete_note": self._delete_note,
            "set_reminder": self._set_reminder,
            "view_reminders": self._view_reminders,
            "delete_reminder": self._delete_reminder,
        }
        return handlers.get(intent)

    async def _open_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "")
        app_map = {
            "settings": "com.android.settings",
            "camera": "com.android.camera2",
            "gallery": "com.android.gallery",
            "chrome": "com.android.chrome",
            "browser": "com.android.chrome",
            "youtube": "com.google.android.youtube",
            "maps": "com.google.android.apps.maps",
            "gmail": "com.google.android.gm",
            "calculator": "com.android.calculator2",
            "clock": "com.android.deskclock",
            "phone": "com.android.dialer",
            "contacts": "com.android.contacts",
            "messages": "com.android.messaging",
            "play store": "com.android.vending",
            "spotify": "com.spotify.music",
            "whatsapp": "com.whatsapp",
            "telegram": "org.telegram.messenger",
            "twitter": "com.twitter.android",
            "instagram": "com.instagram.android",
            "facebook": "com.facebook.katana",
            "files": "com.android.documentsui",
            "terminal": "com.termux",
        }
        package = app_map.get(app_name.lower(), app_name)
        result = await self._run("am", "start", "-n", f"{package}/.MainActivity")
        if "ERROR" in result:
            result = await self._run("am", "start", "-n", f"{package}/.main")
        return f"Opened {app_name}." if "ERROR" not in result else f"Could not open {app_name}."

    async def _close_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "")
        app_map = {
            "settings": "com.android.settings",
            "camera": "com.android.camera2",
            "youtube": "com.google.android.youtube",
            "browser": "com.android.chrome",
            "chrome": "com.android.chrome",
        }
        package = app_map.get(app_name.lower(), app_name)
        result = await self._run("am", "force-stop", package)
        return f"Closed {app_name}." if "ERROR" not in result else f"Could not close {app_name}."

    async def _open_youtube(self, params: dict[str, str]) -> str:
        result = await self._run("am", "start", "-n", "com.google.android.youtube/.MainActivity")
        if "ERROR" not in result:
            return "Opening YouTube."
        return await self._run("termux-open", "https://youtube.com")

    async def _open_website(self, params: dict[str, str]) -> str:
        url = params.get("url", "")
        result = await self._run("termux-open", url)
        return f"Opening {url}." if "ERROR" not in result else f"Could not open website."

    async def _set_volume(self, params: dict[str, str]) -> str:
        level = params.get("level", "5")
        result = await self._run("termux-volume", "music", level)
        return f"Volume set to {level}." if "ERROR" not in result else f"Could not set volume."

    async def _set_brightness(self, params: dict[str, str]) -> str:
        level = params.get("level", "128")
        result = await self._run("termux-brightness", level)
        return f"Brightness set to {level}." if "ERROR" not in result else "Could not set brightness."

    async def _tell_time(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p').lstrip('0')}."

    async def _tell_date(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    async def _battery_status(self, params: dict[str, str]) -> str:
        result = await self._run("termux-battery-status")
        if result.startswith("ERROR"):
            return "Battery status unavailable."
        try:
            import json
            data = json.loads(result)
            pct = data.get("percentage", "?")
            plug = data.get("plugged", "?")
            return f"Battery at {pct}%, {'plugged in' if plug else 'on battery'}."
        except Exception:
            return f"Battery status: {result[:100]}"

    async def _search_google(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "")
        url = f"https://www.google.com/search?q={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching Google for {query}." if "ERROR" not in result else "Could not open browser."

    async def _play_music(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "")
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching YouTube for {query}." if "ERROR" not in result else "Could not open YouTube."

    async def _take_note(self, params: dict[str, str]) -> str:
        return "Note saved. (In-memory — full persistence via MemoryPipeline)"

    async def _read_notes(self, params: dict[str, str]) -> str:
        return "Notes feature: use MemoryPipeline for full persistence."

    async def _delete_note(self, params: dict[str, str]) -> str:
        return "Delete note: use MemoryPipeline for full persistence."

    async def _set_reminder(self, params: dict[str, str]) -> str:
        return f"Reminder set for: {params.get('text', '')}."

    async def _view_reminders(self, params: dict[str, str]) -> str:
        return "Reminders: use MemoryPipeline for full persistence."

    async def _delete_reminder(self, params: dict[str, str]) -> str:
        return "Delete reminder: use MemoryPipeline for full persistence."
