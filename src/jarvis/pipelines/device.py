"""Device pipeline — Termux:API Android control (Motor Cortex).

Executes device actions via termux-api subprocess commands.
Gracefully degrades when termux-api is not available.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

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
            "volume_down": lambda p: self._run("termux-volume", "music", "3"),
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
            "copy_clipboard": self._copy_clipboard,
            "get_clipboard": self._get_clipboard,
            "vibrate_phone": self._vibrate_phone,
            "show_toast_msg": self._show_toast_msg,
            "get_gps_location": self._get_gps_location,
            "media_control": self._media_control,
            "make_phone_call": self._make_phone_call,
            "send_sms_msg": self._send_sms_msg,
            "take_screenshot": self._take_screenshot,
            "send_notification": self._send_notification,
            "airplane_mode": self._airplane_mode,
            "do_not_disturb": self._do_not_disturb,
            "sensor_data": self._sensor_data,
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
        return f"Launching {app_name}, sir." if "ERROR" not in result else f"Unable to locate {app_name} in the app registry, sir."

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
        return f"Terminating {app_name}, sir." if "ERROR" not in result else f"Could not terminate {app_name}, sir."

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
        return f"Audio output adjusted to level {level}, sir." if "ERROR" not in result else "Could not adjust volume, sir."

    async def _set_brightness(self, params: dict[str, str]) -> str:
        level = params.get("level", "128")
        result = await self._run("termux-brightness", level)
        return f"Display luminance adjusted to {level}, sir." if "ERROR" not in result else "Could not adjust brightness, sir."

    async def _tell_time(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"The time is currently {now.strftime('%I:%M %p').lstrip('0')}, sir."

    async def _tell_date(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"Today's date is {now.strftime('%A, %B %d, %Y')}, sir."

    async def _battery_status(self, params: dict[str, str]) -> str:
        result = await self._run("termux-battery-status")
        if result.startswith("ERROR"):
            return "Battery telemetry unavailable, sir. Termux API may be offline."
        try:
            data = json.loads(result)
            pct = data.get("percentage", "?")
            plug = data.get("plugged", "?")
            status = "connected to external power" if plug else "running on battery reserve"
            warning = " Warning: power grid critically low, sir." if isinstance(pct, (int, float)) and pct <= 15 else ""
            return f"Power grid at {pct}%, {status}.{warning}"
        except Exception:
            return f"Battery telemetry: {result[:100]}"

    async def _search_google(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a search query, sir."
        url = f"https://www.google.com/search?q={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Opening Google search for '{query}', sir." if "ERROR" not in result else "Unable to open browser, sir."

    async def _play_music(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a song, artist, or track title, sir."
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Initiating audio stream search for '{query}' on YouTube, sir." if "ERROR" not in result else "Unable to launch YouTube client, sir."

    async def _copy_clipboard(self, params: dict[str, str]) -> str:
        text = params.get("text", "").strip()
        if not text:
            return "Please specify the text to copy, sir."
        result = await self._run("termux-clipboard-set", input_data=text)
        return f"Text copied to clipboard buffer, sir." if "ERROR" not in result else "Clipboard subsystem unavailable, sir."

    async def _get_clipboard(self, params: dict[str, str]) -> str:
        result = await self._run("termux-clipboard-get")
        if "ERROR" in result or not result:
            return "Clipboard buffer is empty or unavailable, sir."
        return f"Clipboard contents, sir: {result}"

    async def _vibrate_phone(self, params: dict[str, str]) -> str:
        duration_ms = params.get("duration", "500")
        result = await self._run("termux-vibrate", "-d", duration_ms)
        return "Haptic feedback engaged, sir." if "ERROR" not in result else "Haptic motor unavailable, sir."

    async def _show_toast_msg(self, params: dict[str, str]) -> str:
        message = params.get("message", "JARVIS Active").strip()
        result = await self._run("termux-toast", message)
        return f"Overlay notification dispatched, sir: '{message}'." if "ERROR" not in result else "Toast notification subsystem offline, sir."

    async def _get_gps_location(self, params: dict[str, str]) -> str:
        result = await self._run("termux-location", "-p", "gps", "-r", "once")
        if "ERROR" in result or not result:
            return "GPS telemetry offline, sir. Location service unavailable or permission denied."
        try:
            data = json.loads(result)
            lat = data.get("latitude", "?")
            lon = data.get("longitude", "?")
            prov = data.get("provider", "gps")
            return f"GPS lock acquired, sir. Coordinates: Latitude {lat}, Longitude {lon} via {prov}."
        except Exception:
            return f"Location telemetry: {result[:120]}"

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
            return "Please specify a phone number, sir."
        result = await self._run("termux-telephony-call", number)
        return f"Initiating call to {number}, sir." if "ERROR" not in result else "Telephony system unavailable, sir. Check Termux API permissions."

    async def _send_sms_msg(self, params: dict[str, str]) -> str:
        number = params.get("number", "").strip()
        message = params.get("message", "").strip()
        if not number or not message:
            return "Please specify both a recipient number and message content, sir."
        result = await self._run("termux-sms-send", "-n", number, message)
        return f"Message transmitted to {number}, sir." if "ERROR" not in result else "SMS dispatch failed, sir. Check Termux API permissions."

    async def _take_screenshot(self, params: dict[str, str]) -> str:
        """Capture a screenshot and save it."""
        result = await self._run("termux-screenshot")
        if "ERROR" in result:
            return "Screenshot capture failed, sir. Termux API screenshot permission may be missing."
        return "Screen captured and saved to local storage, sir."

    async def _send_notification(self, params: dict[str, str]) -> str:
        """Send a persistent notification via Termux:API."""
        title = params.get("title", "JARVIS Notification")
        content = params.get("content", params.get("message", "")).strip()
        if not content:
            return "Please specify notification content, sir."
        result = await self._run("termux-notification", "-t", title, "-c", content)
        if "ERROR" in result:
            return "Notification dispatch failed, sir."
        return f"Notification posted, sir: {content}"

    async def _airplane_mode(self, params: dict[str, str]) -> str:
        """Toggle airplane mode on/off."""
        state = params.get("state", "toggle").lower()
        if state in ("on", "enable", "true", "1"):
            val = "1"
            label = "enabled"
        elif state in ("off", "disable", "false", "0"):
            val = "0"
            label = "disabled"
        else:
            # Toggle — read current state first
            current = await self._run("settings", "get", "global", "airplane_mode_on")
            val = "0" if current.strip() == "1" else "1"
            label = "toggled"
        result = await self._run("settings", "put", "global", "airplane_mode_on", val)
        return f"Airplane mode {label}, sir." if "ERROR" not in result else "Unable to change airplane mode, sir."

    async def _do_not_disturb(self, params: dict[str, str]) -> str:
        """Toggle Do Not Disturb mode."""
        state = params.get("state", "toggle").lower()
        if state in ("on", "enable", "silent"):
            val = "2"  # DND mode: 0=off, 1=priority, 2=total silence
            label = "enabled"
        elif state in ("off", "disable"):
            val = "0"
            label = "disabled"
        else:
            current = await self._run("settings", "get", "global", "zen_mode")
            val = "0" if current.strip() == "2" else "2"
            label = "toggled"
        result = await self._run("settings", "put", "global", "zen_mode", val)
        return f"Do Not Disturb {label}, sir." if "ERROR" not in result else "Unable to change Do Not Disturb mode, sir."

    async def _sensor_data(self, params: dict[str, str]) -> str:
        """Read sensor data from available device sensors."""
        sensor_type = params.get("sensor", "").strip().lower()
        args = ["termux-sensor"]
        if sensor_type:
            args.extend(["-s", sensor_type])
        args.extend(["-n", "1"])
        result = await self._run(*args)
        if "ERROR" in result or not result:
            return "Sensor telemetry unavailable, sir. Termux API sensor permission may be missing."
        try:
            data = json.loads(result)
            if sensor_type and sensor_type in data:
                vals = data[sensor_type]
                if isinstance(vals, list) and vals:
                    vals = vals[0]
                values = ", ".join(f"{k}: {v}" for k, v in vals.items() if k != "timestamp")
                return f"{sensor_type.title()} readings, sir: {values}"
            lines = []
            for sname, sdata in data.items():
                if isinstance(sdata, list) and sdata:
                    sdata = sdata[0]
                if isinstance(sdata, dict):
                    vals = ", ".join(f"{k}: {v}" for k, v in sdata.items() if k != "timestamp")
                    lines.append(f"{sname}: {vals}")
            return "Sensor telemetry, sir:\n" + "\n".join(lines[:5])
        except (json.JSONDecodeError, TypeError):
            return f"Sensor data: {result[:200]}"


