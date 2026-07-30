"""All intent handlers in one place — each maps an intent name to a callable.

Every handler receives ``(engine, intent, params, text)`` and returns a
response string or ``None`` (fall through to LLM).
"""

from __future__ import annotations

import ast
import operator
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from jarvis.core.engine import Engine


# ── Base ──────────────────────────────────────────────────────────────────────

class IntentHandler(ABC):
    @abstractmethod
    async def handle(self, engine: Any, intent: str, params: dict[str, str], text: str) -> Optional[str]:
        ...


# ── Calculator ────────────────────────────────────────────────────────────────

_SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(expr: str) -> str:
    e = expr.replace("^", "**").strip()
    if not e:
        return "Please specify a calculation."
    try:
        node = ast.parse(e, mode="eval")
        def _eval(n):
            if isinstance(n, ast.Expression):
                return _eval(n.body)
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                return n.value
            if isinstance(n, ast.BinOp):
                l, r = _eval(n.left), _eval(n.right)
                if type(n.op) is ast.Pow and (abs(l) > 1000 or r > 1000 or r < -1000):
                    raise ValueError
                if type(n.op) in _SAFE_OPS:
                    res = _SAFE_OPS[type(n.op)](l, r)
                    if isinstance(res, (int, float)) and abs(res) > 1e100:
                        raise ValueError
                    return res
            if isinstance(n, ast.UnaryOp):
                o = _eval(n.operand)
                if type(n.op) in _SAFE_OPS:
                    return _SAFE_OPS[type(n.op)](o)
            raise ValueError
        r = _eval(node)
        if isinstance(r, float) and r.is_integer():
            r = int(r)
        return f"The result of {expr} is {r}."
    except ZeroDivisionError:
        return "Division by zero is not defined."
    except Exception:
        return f"Could not calculate '{expr}'."


# ── Concrete handlers ─────────────────────────────────────────────────────────

class _SimpleHandler(IntentHandler):
    """Wrap a sync/async callable as a handler."""
    def __init__(self, fn) -> None:
        self._fn = fn
    async def handle(self, engine, intent, params, text):
        return await self._fn(engine, params, text) if hasattr(self._fn, '__await__') else self._fn(engine, params, text)


class _Exit(IntentHandler):
    async def handle(self, engine, intent, params, text):
        await engine.shutdown()
        return "Powering down all systems. It has been a pleasure, sir. JARVIS offline."


class _WhoCreated(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return "I was designed and built by Minaty001, sir — an architect of considerable talent. I exist to serve."


class _Calculate(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return _safe_eval(params.get("expression", ""))


class _WhatIs(IntentHandler):
    async def handle(self, engine, intent, params, text):
        q = params.get("query", "").strip().lower()
        if q:
            stored = await engine.memory.recall(q)
            if stored:
                return f"According to your personal archive, sir: {q} is {stored}."
        return None


class _RememberFact(IntentHandler):
    async def handle(self, engine, intent, params, text):
        k = params.get("key", params.get("fact", text))
        v = params.get("value", params.get("fact", text))
        await engine.memory.remember(k, v)
        return f"Noted and stored in your personal archive, sir. {k}: {v}."


class _TakeNote(IntentHandler):
    async def handle(self, engine, intent, params, text):
        c = params.get("content", text)
        await engine.memory.save_note(c[:20] + "..." if len(c) > 20 else c, c)
        return f"Note logged to your personal database, sir: '{c}'."


class _ReadNotes(IntentHandler):
    async def handle(self, engine, intent, params, text):
        notes = await engine.memory.get_notes()
        if not notes:
            return "Your personal archive is currently empty, sir. No notes on file."
        return "Retrieving your notes, sir:\n" + "\n".join(f"- {n['content']}" for n in notes)


class _SearchConversation(IntentHandler):
    async def handle(self, engine, intent, params, text):
        q = params.get("query", "")
        results = await engine.memory.search_conversation(q)
        if not results:
            return f"No conversation history found matching '{q}', sir."
        return "I found these entries in your conversation history, sir:\n" + "\n".join(
            f"[{r['timestamp'][:16]}] {r['role']}: {r['content'][:100]}" for r in results)


class _ExportConversation(IntentHandler):
    async def handle(self, engine, intent, params, text):
        d = Path(engine.config.database_path).parent / "exports"
        d.mkdir(parents=True, exist_ok=True)
        fp = d / f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        p, c = await engine.memory.export_conversation(fp)
        return f"Conversation history exported to {p}, sir. All {c} exchanges archived."


class _DeleteNote(IntentHandler):
    async def handle(self, engine, intent, params, text):
        q = params.get("query", "")
        return f"Note purged from archive, sir." if await engine.memory.delete_note(q) else f"No notes matching '{q}' found in the database, sir."


class _SetReminder(IntentHandler):
    async def handle(self, engine, intent, params, text):
        t = params.get("text", text)
        await engine.memory.save_reminder(t)
        return f"Reminder set and standing by, sir: '{t}'."


class _ViewReminders(IntentHandler):
    async def handle(self, engine, intent, params, text):
        r = await engine.memory.get_reminders()
        if not r:
            return "No active reminders on record, sir. All clear."
        return "Active reminders on file, sir:\n" + "\n".join(f"- {x['text']}" for x in r)


class _DeleteReminder(IntentHandler):
    async def handle(self, engine, intent, params, text):
        q = params.get("query", "")
        return f"Reminder cleared from the queue, sir." if await engine.memory.delete_reminder(q) else f"No matching reminder found for '{q}', sir."


class _AddCustomCmd(IntentHandler):
    async def handle(self, engine, intent, params, text):
        t, a = params.get("trigger_phrase", ""), params.get("actions", "")
        await engine.memory.add_custom_command(t, a)
        return f"Custom voice command '{t}' registered in the system, sir."


class _ListCustomCmds(IntentHandler):
    async def handle(self, engine, intent, params, text):
        cmds = await engine.memory.list_custom_commands()
        if not cmds:
            return "No custom voice commands created yet, sir."
        return "Registered custom commands:\n" + "\n".join(f"- '{c['trigger_phrase']}': {c['actions']}" for c in cmds)


class _DeleteCustomCmd(IntentHandler):
    async def handle(self, engine, intent, params, text):
        t = params.get("trigger_phrase", "")
        return f"Custom command '{t}' has been removed from the registry, sir." if await engine.memory.delete_custom_command(t) else f"No custom command found for '{t}', sir."


class _SetTimer(IntentHandler):
    async def handle(self, engine, intent, params, text):
        d = params.get("duration", "60")
        u = params.get("unit", "seconds").lower()
        lb = params.get("label", "Timer") or "Timer"
        try:
            sec = float(d) * 60 if "min" in u else float(d)
        except ValueError:
            sec = 60.0
        if any(w in text.lower() for w in ("recurring", "repeat", "every")):
            return await engine.scheduler.create_recurring_timer(lb, sec)
        return await engine.scheduler.create_timer(lb, sec)


class _ViewTimers(IntentHandler):
    async def handle(self, engine, intent, params, text):
        t = await engine.scheduler.get_active_timers()
        if not t:
            return "No active countdowns running, sir. All timers have completed or none were set."
        return "Active countdowns, sir:\n" + "\n".join(
            f"- {x['label']} ({'every ' + str(x['duration_sec']) + 's' if x.get('recurring') else str(x['duration_sec']) + 's total'})" for x in t)


class _CancelTimer(IntentHandler):
    async def handle(self, engine, intent, params, text):
        q = params.get("query", "")
        return f"Countdown aborted, sir. Timer '{q}' has been cancelled." if await engine.scheduler.cancel_timer(q) else f"No active timer matching '{q}' found, sir."


class _RunProtocol(IntentHandler):
    async def handle(self, engine, intent, params, text):
        p = params.get("protocol_name", "alpha")
        if getattr(engine, "audio_fx", None):
            await engine.audio_fx.play_fx("protocol")
        return await engine.protocol.execute_protocol(p)


class _Telemetry(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return await engine.telemetry.format_diagnostic_report()


class _Weather(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return await engine.search.get_weather(params.get("location", "auto"))


class _WebSearch(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return await engine.search.search_web_summary(params.get("query", ""))


class _ScanVision(IntentHandler):
    async def handle(self, engine, intent, params, text):
        return await engine.vision.analyze_visual_target(query="Visual scan requested")


class _Device(IntentHandler):
    """Generic: delegates any device intent to engine.device.execute()."""
    async def handle(self, engine, intent, params, text):
        result = await engine.device.execute(intent, params)
        await engine.memory.save_exchange("user", text)
        await engine.memory.save_exchange("assistant", result)
        return result


# ── Registry ──────────────────────────────────────────────────────────────────

_ALL_DEVICE_INTS = {
    "open_app", "close_app", "open_settings", "open_camera", "open_gallery",
    "open_youtube", "open_website", "go_home", "show_recent", "show_notifications",
    "flashlight_on", "flashlight_off", "volume_up", "volume_down", "set_volume",
    "brightness_up", "brightness_down", "set_brightness", "tell_time", "tell_date",
    "battery_status", "wifi_on", "wifi_off", "wifi_status", "bluetooth_on", "bluetooth_off",
    "search_google", "play_music", "copy_clipboard", "get_clipboard", "vibrate_phone",
    "show_toast_msg", "get_gps_location", "media_control", "make_phone_call", "send_sms_msg",
    "take_screenshot", "send_notification", "airplane_mode", "do_not_disturb", "sensor_data",
}

_dev = _Device()
INTENT_HANDLERS: dict[str, IntentHandler] = {
    **dict.fromkeys(_ALL_DEVICE_INTS, _dev),
    "exit": _Exit(),
    "who_created": _WhoCreated(),
    "calculate": _Calculate(),
    "what_is": _WhatIs(),
    "remember_fact": _RememberFact(),
    "take_note": _TakeNote(),
    "read_notes": _ReadNotes(),
    "search_conversation": _SearchConversation(),
    "export_conversation": _ExportConversation(),
    "delete_note": _DeleteNote(),
    "set_reminder": _SetReminder(),
    "view_reminders": _ViewReminders(),
    "delete_reminder": _DeleteReminder(),
    "add_custom_cmd": _AddCustomCmd(),
    "list_custom_cmds": _ListCustomCmds(),
    "delete_custom_cmd": _DeleteCustomCmd(),
    "set_timer": _SetTimer(),
    "view_timers": _ViewTimers(),
    "cancel_timer": _CancelTimer(),
    "run_protocol": _RunProtocol(),
    "system_telemetry": _Telemetry(),
    "tell_weather": _Weather(),
    "web_search_intel": _WebSearch(),
    "scan_vision": _ScanVision(),
}
