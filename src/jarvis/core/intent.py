"""Rule-based intent classifier for user commands.

Maps natural language input to structured intents with extracted parameters.
Acts as the prefrontal cortex (PFC) — the first stage of processing.
"""

from __future__ import annotations

import re

_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    ("add_custom_cmd", r"^(?:create|add|set)\s+(?:custom\s+command|shortcut)\s+['\"]?(.+?)['\"]?\s+(?:to|that|and)\s+(.+)", ["trigger_phrase", "actions"]),
    ("list_custom_cmds", r"^(?:list|show|view)\s+(?:my\s+)?custom\s+commands", []),
    ("delete_custom_cmd", r"^(?:delete|remove)\s+custom\s+command\s+['\"]?(.+?)['\"]?$", ["trigger_phrase"]),
    ("copy_clipboard", r"^(?:copy|copy\s+to\s+clipboard)\s+(.+)", ["text"]),
    ("get_clipboard", r"^(?:get|read|show|check)\s+(?:the\s+)?clipboard", []),
    ("vibrate_phone", r"^(?:vibrate|vibrate\s+device|buzz|buzz\s+phone)", []),
    ("show_toast_msg", r"^(?:show\s+toast|toast|popup)\s+(.+)", ["message"]),
    ("get_gps_location", r"^(?:where\s+am\s+i|my\s+location|gps\s+location|current\s+location)", []),
    ("media_control", r"^(?:media\s+|music\s+)?(play|pause|next|previous|stop)(?:\s+track|\s+song)?", ["action"]),
    ("make_phone_call", r"^(?:make\s+a\s+)?(?:call|phone|dial)\s+(.+)", ["number"]),
    ("send_sms_msg", r"^(?:send\s+sms|send\s+text|text)\s+(?:to\s+)?(\d+|\w+)\s+(?:saying|with|that)\s+(.+)", ["number", "message"]),
    ("tell_weather", r"(?:what(?:\'s|\s+is)\s+)?(?:the\s+)?weather(?:\s+in\s+(.+))?", ["location"]),
    ("system_telemetry", r"(?:system\s+status|suit\s+status|diagnostics|telemetry|system\s+diagnostics|health\s+check|system\s+health)", []),
    ("run_protocol", r"(?:initiate|execute|engage|run|start)\s+(?:protocol\s+)?(house\s+party|stealth\s+mode|stealth|lockdown|protocol\s+alpha|clean\s+sweep|overdrive)(?:\s+protocol)?", ["protocol_name"]),
    ("set_timer", r"(?:set|start|create)\s+(?:a\s+)?timer\s+(?:for\s+)?(\d+)\s*(seconds?|secs?|minutes?|mins?)(?:\s+(?:for|called|labeled)\s+(.+))?", ["duration", "unit", "label"]),
    ("view_timers", r"(?:show|view|list|check)\s+(?:my\s+)?timers", []),
    ("cancel_timer", r"(?:cancel|stop|delete)\s+(?:the\s+)?timer\s*(.*)", ["query"]),
    ("scan_vision", r"(?:take\s+a\s+photo|scan\s+environment|take\s+picture|visual\s+scan|inspect\s+camera|look\s+at\s+this)", []),
    ("web_search_intel", r"(?:intelligence\s+search|search\s+intel|live\s+search)\s+(.+)", ["query"]),
    ("open_settings", r"(?:open|launch)\s+(?:the\s+)?settings", []),
    ("open_camera", r"(?:open|launch)\s+(?:the\s+)?camera", []),
    ("open_gallery", r"(?:open|launch)\s+(?:the\s+)?gallery", []),
    ("open_youtube", r"(?:open|launch)\s+youtube", []),
    ("open_website", r"^(?:open|go\s+to|visit)\s+(?:the\s+)?website\s+(.+)", ["url"]),
    ("open_website", r"^(?:open|go\s+to|visit)\s+(https?://\S+|[\w\-]+\.(?:com|org|net|io|edu|gov)\S*)", ["url"]),
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
    ("set_reminder", r"(?:set|create|make)\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+)", ["text"]),
    ("view_reminders", r"(?:view|show|list)\s+(?:my\s+)?reminders", []),
    ("delete_reminder", r"(?:delete|remove|clear)\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+)", ["query"]),
    ("delete_note", r"(?:delete|remove|erase)\s+(?:a\s+)?note\s+(?:that\s+)?(.+)", ["query"]),
    ("delete_note", r"(?:delete|remove|erase)\s+(.+)", ["query"]),
    ("calculate", r"(?:calculate|compute)\s+(.+)", ["expression"]),
    ("remember_fact", r"(?:remember|note|remember\s+that|keep\s+in\s+mind)\s+(?:that\s+)?(.+)", ["fact"]),
    ("what_is", r"what(?:\'s| is)\s+(?:my\s+|the\s+)?(.+)", ["query"]),
    ("who_created", r"(?:who\s+)?(?:created|made|build|built|own|owner|father|creator|maker|made\s+you)\s*(?:you|this|jarvis|jarvis)?\??", []),
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
            elif " is " in fact:
                parts = fact.split(" is ", 1)
                params["key"] = parts[0].strip()
                params["value"] = parts[1].strip()
            else:
                params["key"] = fact
                params["value"] = fact
            if "key" in params:
                params["key"] = re.sub(r"^my\s+", "", params["key"], flags=re.IGNORECASE).strip()
        elif intent == "what_is" and "query" in params:
            q = params["query"].strip()
            if re.match(r"^[\d\s\+\-\*\/\(\)\.\^%]+$", q) and any(c in q for c in "+-*/^%"):
                return "calculate", {"expression": q}

        return intent, params

    return "general_chat", {"text": text}
