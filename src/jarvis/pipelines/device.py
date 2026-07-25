"""Device pipeline — Termux:API Android control (Motor Cortex).

Executes device actions via termux-api subprocess commands.
Gracefully degrades when termux-api is not available.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import subprocess
import json
from datetime import datetime
from typing import Optional

import shutil
from jarvis.utils.logging import log


class DevicePipeline:
    """Async wrapper around Termux-API and Android commands."""

    def __init__(self) -> None:
        self._available_bins: dict[str, bool] = {}

    async def _run(self, *args: str, input_data: Optional[str] = None) -> str:
        """Run a subprocess asynchronously and return stdout."""
        if not args:
            return "ERROR: Empty command"
        cmd_name = args[0]
        if cmd_name not in self._available_bins:
            self._available_bins[cmd_name] = shutil.which(cmd_name) is not None

        if not self._available_bins[cmd_name]:
            log.warning(f"Command '{cmd_name}' not available on system.")
            return f"ERROR: '{cmd_name}' is not installed or available."
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
            "search_google": self._search_google,
            "play_music": self._play_music,
            "copy_clipboard": self._copy_clipboard,
            "get_clipboard": self._get_clipboard,
            "vibrate_phone": self._vibrate_phone,
            "show_toast_msg": self._show_toast_msg,
            "get_gps_location": self._get_gps_location,
            "media_control": self._media_control,
            "make_phone_call": self._make_phone_call,
            "send_sms_msg": self._send_sms_msg,
        }
        return handlers.get(intent)

    async def _open_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "").strip()
        if not app_name:
            return "Please specify an app to open."
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
        app_name = params.get("app_name", "").strip()
        if not app_name:
            return "Please specify an app to close."
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
        url = params.get("url", "").strip()
        if not url:
            return "Please specify a URL."
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
            data = json.loads(result)
            pct = data.get("percentage", "?")
            plug = data.get("plugged", "?")
            return f"Battery at {pct}%, {'plugged in' if plug else 'on battery'}."
        except Exception:
            return f"Battery status: {result[:100]}"

    async def _search_google(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a query to search."
        url = f"https://www.google.com/search?q={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching Google for {query}." if "ERROR" not in result else "Could not open browser."

    async def _play_music(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a song or artist."
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching YouTube for {query}." if "ERROR" not in result else "Could not open YouTube."

    async def _copy_clipboard(self, params: dict[str, str]) -> str:
        text = params.get("text", "").strip()
        if not text:
            return "Please specify text to copy to clipboard."
        result = await self._run("termux-clipboard-set", input_data=text)
        return f"Copied to clipboard: '{text}'." if "ERROR" not in result else f"Clipboard set failed."

    async def _get_clipboard(self, params: dict[str, str]) -> str:
        content = await self._run("termux-clipboard-get")
        if "ERROR" in content or not content:
            return "Clipboard is empty or termux-api permission missing."
        return f"Clipboard content: '{content}'."

    async def _vibrate_phone(self, params: dict[str, str]) -> str:
        duration_ms = params.get("duration", "500")
        result = await self._run("termux-vibrate", "-d", duration_ms)
        return "Device vibrated." if "ERROR" not in result else "Vibration trigger unavailable."

    async def _show_toast_msg(self, params: dict[str, str]) -> str:
        message = params.get("message", "JARVIS Active").strip()
        result = await self._run("termux-toast", message)
        return f"Toast displayed: '{message}'." if "ERROR" not in result else "Toast notification failed."

    async def _get_gps_location(self, params: dict[str, str]) -> str:
        result = await self._run("termux-location", "-p", "gps", "-r", "once")
        if "ERROR" in result or not result:
            return "Location service unavailable or permission denied."
        try:
            data = json.loads(result)
            lat = data.get("latitude", "?")
            lon = data.get("longitude", "?")
            prov = data.get("provider", "gps")
            return f"Device location: Lat {lat}, Lon {lon} ({prov})."
        except Exception:
            return f"Location: {result[:120]}"

    async def _media_control(self, params: dict[str, str]) -> str:
        action = params.get("action", "play").lower().strip()
        key_map = {
            "play": "85",
            "pause": "127",
            "next": "87",
            "previous": "88",
            "stop": "86",
        }
        keycode = key_map.get(action, "85")
        result = await self._run("input", "keyevent", keycode)
        return f"Media command '{action}' sent." if "ERROR" not in result else f"Could not send media command."

    async def _make_phone_call(self, params: dict[str, str]) -> str:
        number = params.get("number", "").strip()
        if not number:
            return "Please specify a phone number to call."
        result = await self._run("termux-telephony-call", number)
        return f"Initiating call to {number}." if "ERROR" not in result else "Phone call permission unavailable."

    async def _send_sms_msg(self, params: dict[str, str]) -> str:
        number = params.get("number", "").strip()
        message = params.get("message", "").strip()
        if not number or not message:
            return "Please specify both phone number and message for SMS."
        result = await self._run("termux-sms-send", "-n", number, message)
        return f"SMS sent to {number}." if "ERROR" not in result else "SMS dispatch failed."


