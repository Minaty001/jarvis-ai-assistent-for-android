import os
import sys

replacements = {
    # Full import replacements
    "from jarvis.core.config import": "from config.settings import",
    "from jarvis.core.intent import": "from brain.intent import",
    "from jarvis.core.tools import": "from ai.tools import",
    "from jarvis.core.engine import": "from brain.engine import",
    "from jarvis.services.base import": "from shared.base import",
    "from jarvis.services.chat import": "from ai.chat import",
    "from jarvis.services.storage import": "from memory.storage import",
    "from jarvis.services.stt import": "from perception.voice.stt import",
    "from jarvis.services.tts import": "from perception.voice.tts import",
    "from jarvis.services.device import": "from actions.android import",
    "from jarvis.modules.search import": "from actions.browser.search import",
    "from jarvis.modules.vision import": "from perception.vision import",
    "from jarvis.modules.audio_fx import": "from perception.voice.audio import",
    "from jarvis.modules.timers import": "from actions.timers import",
    "from jarvis.modules.protocols import": "from actions.protocols import",
    "from jarvis.modules.autonomy import": "from brain.autonomy import",
    "from jarvis.modules.telemetry import": "from brain.telemetry import",
    "from jarvis.utils.logging import": "from shared.logger import",
    "from jarvis.ui.brain_renderer import": "from ui.brain_renderer import",
    "from jarvis.ui.tui import": "from ui.terminal.tui import",
    "from jarvis.ui.web_ui.app import": "from ui.web.app import",
    "from jarvis.cli import": "from app.cli import",
    "from jarvis.pipelines.device import": "from actions.android import",
    "from jarvis.pipelines.memory import": "from memory.storage import",
    "from jarvis.pipelines.audio_fx import": "from perception.voice.audio import",
    "from jarvis.pipelines.autonomy import": "from brain.autonomy import",
    "from jarvis.pipelines.telemetry import": "from brain.telemetry import",
    "from jarvis.pipelines.chat import": "from ai.chat import",
    "from jarvis.pipelines.protocol import": "from actions.protocols import",
    "from jarvis.pipelines.scheduler import": "from actions.timers import",
    "from jarvis.pipelines.search import": "from actions.browser.search import",
    "from jarvis.pipelines.speech import": "from perception.voice.stt import",
    "from jarvis.pipelines.vision import": "from perception.vision import",
    "from jarvis.pipelines.voice import": "from perception.voice.tts import",

    # Simple package imports
    "import jarvis.core.config": "import config.settings",
    "import jarvis.core.intent": "import brain.intent",
    "import jarvis.core.tools": "import ai.tools",
    "import jarvis.core.engine": "import brain.engine",
    "import jarvis.services.base": "import shared.base",
    "import jarvis.services.chat": "import ai.chat",
    "import jarvis.services.storage": "import memory.storage",
    "import jarvis.services.stt": "import perception.voice.stt",
    "import jarvis.services.tts": "import perception.voice.tts",
    "import jarvis.services.device": "import actions.android",
    "import jarvis.modules.search": "import actions.browser.search",
    "import jarvis.modules.vision": "import perception.vision",
    "import jarvis.modules.audio_fx": "import perception.voice.audio",
    "import jarvis.modules.timers": "import actions.timers",
    "import jarvis.modules.protocols": "import actions.protocols",
    "import jarvis.modules.autonomy": "import brain.autonomy",
    "import jarvis.modules.telemetry": "import brain.telemetry",
    "import jarvis.utils.logging": "import shared.logger",

    # Specific ones for tests and monkeypatching
    "\"jarvis.pipelines.speech._find_audio_capture\"": "\"perception.voice.stt._find_audio_capture\"",
    "\"jarvis.services.stt._find_audio_capture\"": "\"perception.voice.stt._find_audio_capture\"",
}

# Directories to search
dirs = ["brain", "perception", "actions", "ai", "memory", "ui", "shared", "config", "app", "tests"]

for d in dirs:
    if not os.path.exists(d):
        continue
    for root, _, files in os.walk(d):
        for f in files:
            if not f.endswith(".py") and not f.endswith(".js") and not f.endswith(".html"):
                continue
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            
            orig = content
            for k, v in replacements.items():
                content = content.replace(k, v)
            
            if content != orig:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"Updated {path}")

print("Done refactoring imports.")
