"""Tool specifications and function-calling dispatch for LLM.

Each tool is defined as a lightweight tuple and converted to the
OpenAI-compatible JSON schema at runtime.  The dispatch table reuses the
same engine method calls the intent handlers do.
"""

from __future__ import annotations

import json
from typing import Any

from shared.logger import log


# (name, description, params_dict)  — params_dict: {name: (type, description, required?)}
_TOOL_DEFS: list[tuple[str, str, dict[str, tuple[str, str, bool]]]] = [
    ("get_weather", "Fetch real-time live weather for a city or current location.",
     {"location": ("string", "City name or 'auto' for current GPS/IP location.", True)}),
    ("system_telemetry", "Fetch CPU load, RAM, storage, and battery status.",
     {}),
    ("execute_protocol", "Execute MCU Stark protocol (house_party, stealth, lockdown, alpha, overdrive).",
     {"protocol_name": ("string", "Protocol key.", True)}),
    ("set_timer", "Set a countdown timer with label.",
     {"seconds": ("number", "Duration in seconds.", True),
      "label": ("string", "Timer description.", True)}),
    ("web_search_intel", "Search the web for up-to-date facts and news.",
     {"query": ("string", "Search query.", True)}),
    ("copy_clipboard", "Copy text to Android clipboard.",
     {"text": ("string", "Text to copy.", True)}),
    ("get_clipboard", "Read current clipboard content.",
     {}),
    ("take_note", "Save a note to user's personal database.",
     {"content": ("string", "Note content.", True)}),
    ("view_reminders", "List all active reminders.",
     {}),
]


def _build_schema(name: str, desc: str, params: dict) -> dict:
    props = {}
    required = []
    for pname, (ptype, pdesc, req) in params.items():
        props[pname] = {"type": ptype, "description": pdesc}
        if req:
            required.append(pname)
    schema = {"type": "object", "properties": props, "required": required}
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": schema}}


JARVIS_TOOL_SCHEMAS: list[dict[str, Any]] = [_build_schema(n, d, p) for n, d, p in _TOOL_DEFS]


async def execute_llm_tool_call(engine: Any, tool_call: dict[str, Any]) -> str:
    info = tool_call.get("function", {})
    name = info.get("name", "")
    raw = info.get("arguments", "{}")
    try:
        args = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        args = {}

    log.info(f"LLM tool call: {name} args={args}")

    _DISPATCH = {
        "get_weather": lambda: engine.search.get_weather(args.get("location", "auto")),
        "system_telemetry": lambda: engine.telemetry.format_diagnostic_report(),
        "execute_protocol": lambda: engine.protocol.execute_protocol(args.get("protocol_name", "alpha")),
        "set_timer": lambda: engine.scheduler.create_timer(args.get("label", "Timer"), float(args.get("seconds", 60))),
        "web_search_intel": lambda: engine.search.search_web_summary(args.get("query", "")),
        "copy_clipboard": lambda: engine.device.execute("copy_clipboard", {"text": args.get("text", "")}),
        "get_clipboard": lambda: engine.device.execute("get_clipboard", {}),
        "take_note": lambda: _do_take_note(engine, args.get("content", "")),
        "view_reminders": lambda: _do_view_reminders(engine),
    }

    fn = _DISPATCH.get(name)
    if fn is None:
        return f"Tool '{name}' not available."

    try:
        return await fn()
    except Exception as e:
        return f"Tool '{name}' failed: {e}"


async def _do_take_note(engine: Any, content: str) -> str:
    title = content[:20] + "..." if len(content) > 20 else content
    await engine.memory.save_note(title, content)
    return "Note saved to your personal database, sir."


async def _do_view_reminders(engine: Any) -> str:
    reminders = await engine.memory.get_reminders()
    if not reminders:
        return "No active reminders on record, sir. All clear."
    return "Active reminders:\n" + "\n".join(f"- {r['text']}" for r in reminders)
