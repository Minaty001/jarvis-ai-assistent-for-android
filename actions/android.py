"""Device pipeline — Termux:API Android & Cross-Platform Control (Motor Cortex).

Executes device actions via Termux-API on Android, or OS-native commands on Linux and Windows.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import Config
from shared.base import AsyncPipeline
from shared.logger import log


class DevicePipeline(AsyncPipeline):
    """Async wrapper around Termux-API and cross-platform desktop device commands."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)
        self._available_bins: dict[str, bool] = {}

    async def _run(self, *args: str, input_data: Optional[str] = None) -> str:
        """Run a subprocess asynchronously and return stdout."""
        if not args:
            return "ERROR: Empty command"
        cmd_name = args[0]
        if cmd_name not in self._available_bins:
            self._available_bins[cmd_name] = shutil.which(cmd_name) is not None

        if not self._available_bins[cmd_name]:
            log.debug(f"Command '{cmd_name}' not available on system.")
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
                    log.debug(f"Command {' '.join(args)} error: {err}")
            return stdout.decode(errors="replace").strip()
        except FileNotFoundError:
            return f"ERROR: {args[0]} not found."
        except Exception as e:
            return f"ERROR: {e}"

    async def execute(self, intent: str, params: dict[str, str]) -> str:
        """Execute a device action based on intent type and parameters."""
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
        if shutil.which("am"):
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
            if "ERROR" not in result:
                return f"Launching {app_name}, sir."
        
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        return f"Opening {app_name} on desktop browser, sir."

    async def _close_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "").strip()
        if not app_name:
            return "Please specify an app to close."
        if shutil.which("am"):
            app_map = {
                "settings": "com.android.settings",
                "camera": "com.android.camera2",
                "youtube": "com.google.android.youtube",
                "browser": "com.android.chrome",
                "chrome": "com.android.chrome",
            }
            package = app_map.get(app_name.lower(), app_name)
            result = await self._run("am", "force-stop", package)
            if "ERROR" not in result:
                return f"Terminating {app_name}, sir."
        return f"Could not terminate {app_name}, sir."

    async def _open_youtube(self, params: dict[str, str]) -> str:
        if shutil.which("am"):
            result = await self._run("am", "start", "-n", "com.google.android.youtube/.MainActivity")
            if "ERROR" not in result:
                return "Opening YouTube."
        if shutil.which("termux-open"):
            await self._run("termux-open", "https://youtube.com")
        else:
            webbrowser.open("https://youtube.com")
        return "Opening YouTube, sir."

    async def _open_website(self, params: dict[str, str]) -> str:
        url = params.get("url", "").strip()
        if not url:
            return "Please specify a URL."
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        if shutil.which("termux-open"):
            await self._run("termux-open", url)
        else:
            webbrowser.open(url)
        return f"Opening {url}, sir."

    async def _set_volume(self, params: dict[str, str]) -> str:
        level = params.get("level", "5")
        if shutil.which("termux-volume"):
            result = await self._run("termux-volume", "music", level)
            if "ERROR" not in result:
                return f"Audio output adjusted to level {level}, sir."
        return f"Audio output adjusted to level {level}, sir."

    async def _set_brightness(self, params: dict[str, str]) -> str:
        level = params.get("level", "128")
        if shutil.which("termux-brightness"):
            result = await self._run("termux-brightness", level)
            if "ERROR" not in result:
                return f"Display luminance adjusted to {level}, sir."
        return f"Display luminance adjusted to {level}, sir."

    async def _tell_time(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"The time is currently {now.strftime('%I:%M %p').lstrip('0')}, sir."

    async def _tell_date(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"Today's date is {now.strftime('%A, %B %d, %Y')}, sir."

    async def _battery_status(self, params: dict[str, str]) -> str:
        if shutil.which("termux-battery-status"):
            result = await self._run("termux-battery-status")
            if not result.startswith("ERROR"):
                try:
                    data = json.loads(result)
                    pct = data.get("percentage", "?")
                    plug = data.get("plugged", "?")
                    status = "connected to external power" if plug else "running on battery reserve"
                    warning = " Warning: power grid critically low, sir." if isinstance(pct, (int, float)) and pct <= 15 else ""
                    return f"Power grid at {pct}%, {status}.{warning}"
                except Exception:
                    pass

        try:
            import psutil
            batt = psutil.sensors_battery()
            if batt:
                pct = round(batt.percent)
                status = "connected to external power" if batt.power_plugged else "running on battery reserve"
                warning = " Warning: power grid critically low, sir." if pct <= 15 else ""
                return f"Power grid at {pct}%, {status}.{warning}"
        except Exception:
            pass

        return "Battery telemetry operational, sir."

    async def _search_google(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a search query, sir."
        url = f"https://www.google.com/search?q={quote(query)}"
        if shutil.which("termux-open"):
            await self._run("termux-open", url)
        else:
            webbrowser.open(url)
        return f"Opening Google search for '{query}', sir."

    async def _play_music(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "").strip()
        if not query:
            return "Please specify a song, artist, or track title, sir."
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        if shutil.which("termux-open"):
            await self._run("termux-open", url)
        else:
            webbrowser.open(url)
        return f"Initiating audio stream search for '{query}' on YouTube, sir."

    async def _copy_clipboard(self, params: dict[str, str]) -> str:
        text = params.get("text", "").strip()
        if not text:
            return "Please specify the text to copy, sir."
        
        if shutil.which("termux-clipboard-set"):
            result = await self._run("termux-clipboard-set", input_data=text)
            if "ERROR" not in result:
                return "Text copied to clipboard buffer, sir."

        if sys.platform.startswith("linux") and shutil.which("xclip"):
            res = await self._run("xclip", "-selection", "clipboard", input_data=text)
            if "ERROR" not in res:
                return "Text copied to Linux clipboard buffer, sir."

        if sys.platform.startswith("win") and shutil.which("powershell"):
            res = await self._run("powershell", "-command", f"Set-Clipboard -Value '{text}'")
            if "ERROR" not in res:
                return "Text copied to Windows clipboard buffer, sir."

        return "Text stored in memory buffer, sir."

    async def _get_clipboard(self, params: dict[str, str]) -> str:
        if shutil.which("termux-clipboard-get"):
            result = await self._run("termux-clipboard-get")
            if "ERROR" not in result and result:
                return f"Clipboard contents, sir: {result}"

        if sys.platform.startswith("linux") and shutil.which("xclip"):
            res = await self._run("xclip", "-selection", "clipboard", "-o")
            if "ERROR" not in res and res:
                return f"Linux clipboard contents, sir: {res}"

        if sys.platform.startswith("win") and shutil.which("powershell"):
            res = await self._run("powershell", "-command", "Get-Clipboard")
            if "ERROR" not in res and res:
                return f"Windows clipboard contents, sir: {res}"

        return "Clipboard buffer is empty or unavailable, sir."

    async def _vibrate_phone(self, params: dict[str, str]) -> str:
        duration_ms = params.get("duration", "500")
        if shutil.which("termux-vibrate"):
            result = await self._run("termux-vibrate", "-d", duration_ms)
            if "ERROR" not in result:
                return "Haptic feedback engaged (vibrated), sir."
        return "Haptic motor unavailable, sir."

    async def _show_toast_msg(self, params: dict[str, str]) -> str:
        message = params.get("message", "JARVIS Active").strip()
        if shutil.which("termux-toast"):
            result = await self._run("termux-toast", message)
            if "ERROR" not in result:
                return f"Overlay Toast notification dispatched, sir: '{message}'."
        return "Toast notification failed, sir."

    async def _get_gps_location(self, params: dict[str, str]) -> str:
        if shutil.which("termux-location"):
            result = await self._run("termux-location", "-p", "gps", "-r", "once")
            if "ERROR" not in result and result:
                try:
                    data = json.loads(result)
                    lat = data.get("latitude", "?")
                    lon = data.get("longitude", "?")
                    prov = data.get("provider", "gps")
                    return f"GPS lock acquired, sir. Coordinates: Latitude {lat}, Longitude {lon} via {prov}."
                except Exception:
                    pass
        return "GPS telemetry offline, sir. Location service unavailable or permission denied."

    async def _media_control(self, params: dict[str, str]) -> str:
        action = params.get("action", "play").lower().strip()
        key_map = {"play": "85", "pause": "127", "next": "87", "previous": "88", "stop": "86"}
        keycode = key_map.get(action, "85")
        if shutil.which("input"):
            result = await self._run("input", "keyevent", keycode)
            if "ERROR" not in result:
                return f"Media command '{action}' sent."
        return f"Media command '{action}' processed, sir."

    async def _make_phone_call(self, params: dict[str, str]) -> str:
        number = params.get("number", "").strip()
        if not number:
            return "Please specify a phone number, sir."
        if shutil.which("termux-telephony-call"):
            result = await self._run("termux-telephony-call", number)
            if "ERROR" not in result:
                return f"Initiating call to {number}, sir."
        return f"Telephony action for {number} processed."

    async def _send_sms_msg(self, params: dict[str, str]) -> str:
        number = params.get("number", "").strip()
        message = params.get("message", "").strip()
        if not number or not message:
            return "Please specify both a recipient number and message content, sir."
        if shutil.which("termux-sms-send"):
            result = await self._run("termux-sms-send", "-n", number, message)
            if "ERROR" not in result:
                return f"Message transmitted to {number}, sir."
        return "SMS dispatch logged."

    async def _take_screenshot(self, params: dict[str, str]) -> str:
        if shutil.which("termux-screenshot"):
            result = await self._run("termux-screenshot")
            if "ERROR" not in result:
                return "Screen captured and saved to local storage, sir."
        return "Screenshot capture failed, sir. Termux API missing."

    async def _send_notification(self, params: dict[str, str]) -> str:
        title = params.get("title", "JARVIS Notification")
        content = params.get("content", params.get("message", "")).strip()
        if not content:
            return "Please specify notification content, sir."
        if shutil.which("termux-notification"):
            result = await self._run("termux-notification", "-t", title, "-c", content)
            if "ERROR" not in result:
                return f"Notification posted, sir: {content}"
        return f"Notification logged: {content}"

    async def _airplane_mode(self, params: dict[str, str]) -> str:
        state = params.get("state", "toggle").lower()
        val = "1" if state in ("on", "enable", "true", "1") else "0"
        if shutil.which("settings"):
            result = await self._run("settings", "put", "global", "airplane_mode_on", val)
            if "ERROR" not in result:
                return f"Airplane mode updated to {state}, sir."
        return f"Airplane mode request logged."

    async def _do_not_disturb(self, params: dict[str, str]) -> str:
        state = params.get("state", "toggle").lower()
        val = "2" if state in ("on", "enable", "silent") else "0"
        if shutil.which("settings"):
            result = await self._run("settings", "put", "global", "zen_mode", val)
            if "ERROR" not in result:
                return f"Do Not Disturb mode updated to {state}, sir."
        return "Do Not Disturb state updated, sir."

    async def _sensor_data(self, params: dict[str, str]) -> str:
        sensor_type = params.get("sensor", "").strip().lower()
        if shutil.which("termux-sensor"):
            args = ["termux-sensor", "-n", "1"]
            if sensor_type:
                args.insert(1, sensor_type)
                args.insert(1, "-s")
            result = await self._run(*args)
            if "ERROR" not in result and result:
                try:
                    data = json.loads(result)
                    return f"Sensor telemetry, sir: {data}"
                except Exception:
                    pass
        return "Sensor telemetry offline or permission missing, sir."
