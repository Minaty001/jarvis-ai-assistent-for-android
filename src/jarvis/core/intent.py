"""Rule-based intent classifier for user commands.

Maps natural language input to structured intents with extracted parameters.
Acts as the prefrontal cortex (PFC) — the first stage of processing.
"""

from __future__ import annotations

import re

_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    ("open_settings", r"(?:open|launch)\s+(?:the\s+)?settings", []),
    ("open_camera", r"(?:open|launch)\s+(?:the\s+)?camera", []),
    ("open_gallery", r"(?:open|launch)\s+(?:the\s+)?gallery", []),
    ("open_youtube", r"(?:open|launch)\s+youtube", []),
    ("open_website", r"(?:open|go\s+to|visit)\s+(?:the\s+)?website\s+(.+)", ["url"]),
    ("open_website", r"go\s+to\s+(.+)", ["url"]),
    ("open_website", r"visit\s+(.+)", ["url"]),
    ("open_app", r"(?:open|launch|start)\s+(?:the\s+)?(.+)", ["app_name"]),
    ("close_app", r"(?:close|exit|quit|kill)\s+(?:the\s+)?(.+)", ["app_name"]),
    ("go_home", r"(?:go\s+)?home\s*(?:screen)?", []),
    ("show_recent", r"(?:show|view)\s+(?:recent|recents|recent\s+apps)", []),
    ("show_notifications", r"(?:show|view|check)\s+(?:notifications|notification)", []),
    ("flashlight_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?flashlight", []),
    ("flashlight_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?flashlight", []),
    ("volume_up", r"(?:turn\s+)?volume\s+up|increase\s+volume", []),
    ("volume_down", r"(?:turn\s+)?volume\s+down|decrease\s+volume|lower\s+volume", []),
    ("set_volume", r"(?:set\s+)?volume\s+to\s+(\d+)", ["level"]),
    ("brightness_up", r"brightness\s+up|increase\s+brightness", []),
    ("brightness_down", r"brightness\s+down|decrease\s+brightness|lower\s+brightness", []),
    ("set_brightness", r"(?:set\s+)?brightness\s+to\s+(\d+)", ["level"]),
    ("tell_time", r"(?:what(?:\'s| is)\s+)?(?:the\s+)?\btime\b(?:\s+now)?", []),
    ("tell_date", r"(?:what(?:\'s| is)\s+)?(?:the\s+)?\bdate\b(?:\s+today)?", []),
    ("battery_status", r"(?:battery|battery\s+status|battery\s+level|how\s+much\s+battery)", []),
    ("wifi_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?wifi", []),
    ("wifi_on", r"wifi\s+(?:on|enable)", []),
    ("wifi_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?wifi", []),
    ("wifi_off", r"wifi\s+(?:off|disable)", []),
    ("wifi_status", r"(?:wifi\s+)?status|is\s+wifi\s+(?:on|connected)", []),
    ("bluetooth_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?bluetooth", []),
    ("bluetooth_on", r"bluetooth\s+(?:on|enable)", []),
    ("bluetooth_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?bluetooth", []),
    ("bluetooth_off", r"bluetooth\s+(?:off|disable)", []),
    ("search_google", r"(?:search\s+(?:the\s+)?(?:web\s+)?(?:for\s+)?|google\s+(?:for\s+)?|look\s+up\s+(?:for\s+)?)(.+)", ["query"]),
    ("play_music", r"(?:play|search)\s+(?:music|song|audio)\s+(.+)|play\s+(.+)", ["query"]),
    ("take_note", r"(?:take|make|create|write|save)\s+(?:a\s+)?note\s+(?:that\s+)?(.+)", ["content"]),
    ("read_notes", r"(?:read|show|list|view)\s+(?:my\s+)?notes", []),
    ("delete_note", r"(?:delete|remove|erase)\s+(?:note\s+)?(.+)", ["query"]),
    ("set_reminder", r"(?:set|create|make)\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+)", ["text"]),
    ("view_reminders", r"(?:view|show|list)\s+(?:my\s+)?reminders", []),
    ("delete_reminder", r"(?:delete|remove|clear)\s+(?:reminder\s+)?(.+)", ["query"]),
    ("calculate", r"(?:calculate|compute)\s+(.+)", ["expression"]),
    ("remember_fact", r"(?:remember|note|remember\s+that|keep\s+in\s+mind)\s+(?:that\s+)?(.+)", ["fact"]),
    ("what_is", r"what(?:\'s| is)\s+(?:my\s+|the\s+)?(.+)", ["query"]),
    ("exit", r"(?:exit|quit|goodbye|bye|shutdown|see\s+you)", []),
]


def classify_intent(text: str) -> tuple[str, dict[str, str]]:
    """Classify user text into an intent type with extracted parameters.

    Args:
        text: Raw user input string.

    Returns:
        Tuple of (intent_type, params_dict). Defaults to
        ('general_chat', {'text': text}) when no pattern matches.
    """
    text_lower = text.strip().lower()
    params: dict[str, str] = {}

    for intent, pattern, param_names in _INTENT_PATTERNS:
        match = re.search(pattern, text_lower)
        if not match:
            continue
        groups = match.groups()
        if param_names:
            for i, name in enumerate(param_names):
                if i < len(groups) and groups[i]:
                    params[name] = groups[i].strip()

        if intent == "search_google" and "query" in params:
            query = params["query"]
            query = re.sub(r"^(?:google\s+(?:for\s+)?|for\s+)", "", query).strip()
            params["query"] = query
        elif intent == "play_music":
            q = " ".join(g for g in groups if g).strip()
            if q:
                params["query"] = q
        elif intent == "open_website" and "url" in params:
            url = params["url"]
            if not url.startswith("http"):
                if "." in url and " " not in url:
                    params["url"] = f"https://{url}"
                else:
                    return "search_google", {"query": url}
        elif intent == "remember_fact" and "fact" in params:
            fact = params["fact"]
            if ":" in fact:
                parts = fact.split(":", 1)
                params["key"] = parts[0].strip()
                params["value"] = parts[1].strip()

        return intent, params

    return "general_chat", {"text": text}
