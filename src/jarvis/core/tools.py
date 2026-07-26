"""Tool specifications & dynamic function calling registry for Groq LLM.

Defines OpenAI-compatible JSON tool schemas and connects tool calls to Engine methods.
Crafted by Minaty001.
"""

from __future__ import annotations

import json
from typing import Any, Dict
from jarvis.utils.logging import log

# OpenAI-compatible tool specifications for Groq API function calling
JARVIS_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetch real-time live weather telemetry for a city or current location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or 'auto' for current GPS/IP location."
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "system_telemetry",
            "description": "Fetch real-time CPU load, RAM usage, storage space, and power grid battery status.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_protocol",
            "description": "Execute named MCU Stark security protocol (house_party, stealth_mode, protocol_alpha, lockdown, overdrive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "protocol_name": {
                        "type": "string",
                        "description": "Protocol key: house_party, stealth, protocol_alpha, lockdown, overdrive."
                    }
                },
                "required": ["protocol_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Set a countdown timer with description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "Countdown duration in seconds."
                    },
                    "label": {
                        "type": "string",
                        "description": "Description / label of the timer."
                    }
                },
                "required": ["seconds", "label"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search_intel",
            "description": "Perform live web intelligence search for up-to-date facts, news, and snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "copy_clipboard",
            "description": "Copy text to Android system clipboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to copy."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clipboard",
            "description": "Read the current text content from the Android system clipboard.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_note",
            "description": "Save a note to the user's personal database for later reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The note content to save."
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_reminders",
            "description": "List all active user reminders.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


async def execute_llm_tool_call(engine: Any, tool_call: dict[str, Any]) -> str:
    """Execute a tool call from LLM output.

    Args:
        engine: Engine instance with initialized pipelines.
        tool_call: Tool call dict with 'function' key containing 'name' and 'arguments'.

    Returns:
        String output of executed tool call.
    """
    func_info = tool_call.get("function", {})
    name = func_info.get("name", "")
    args_raw = func_info.get("arguments", "{}")

    try:
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
    except Exception:
        args = {}

    log.info(f"LLM Function Calling tool: {name} with args: {args}")

    if name == "get_weather" and engine.search:
        loc = args.get("location", "auto")
        return await engine.search.get_weather(loc)

    if name == "system_telemetry" and engine.telemetry:
        return await engine.telemetry.format_diagnostic_report()

    if name == "execute_protocol" and engine.protocol:
        pname = args.get("protocol_name", "alpha")
        return await engine.protocol.execute_protocol(pname)

    if name == "set_timer" and engine.scheduler:
        sec = float(args.get("seconds", 60))
        label = args.get("label", "Timer")
        return await engine.scheduler.create_timer(label, sec)

    if name == "web_search_intel" and engine.search:
        q = args.get("query", "")
        return await engine.search.search_web_summary(q)

    if name == "copy_clipboard" and engine.device:
        return await engine.device.execute("copy_clipboard", {"text": args.get("text", "")})

    if name == "get_clipboard" and engine.device:
        return await engine.device.execute("get_clipboard", {})

    if name == "take_note" and engine.memory:
        content = args.get("content", "")
        title = content[:20] + "..." if len(content) > 20 else content
        await engine.memory.save_note(title, content)
        return f"Note saved to your personal database, sir."

    if name == "view_reminders" and engine.memory:
        reminders = await engine.memory.get_reminders()
        if not reminders:
            return "No active reminders on record, sir. All clear."
        return "Active reminders:\n" + "\n".join(f"- {r['text']}" for r in reminders)

    return f"Tool '{name}' execution unavailable."
