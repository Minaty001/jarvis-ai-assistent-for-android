"""Engine orchestrator — lightweight cortical relay (Prefrontal Cortex).

Manages pipeline lifecycle, intent routing, and the main interaction loop.
Pipelines are independent; the engine routes data between them.
"""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import Optional

from jarvis.core.config import Config, config as app_config
from jarvis.core.intent import classify_intent
from jarvis.utils.logging import log


class EngineState(Enum):
    """Engine state machine states."""
    IDLE = "idle"
    WAKE_WORD = "wake_word"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    TEXT_INPUT = "text_input"


class Engine:
    """Lightweight orchestrator for pipeline coordination."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or app_config
        self.state = EngineState.IDLE
        self.speech = None
        self.chat = None
        self.voice = None
        self.device = None
        self.memory = None
        self._running = False

    async def initialize(self) -> None:
        """Load all pipeline instances."""
        from jarvis.pipelines.speech import SpeechPipeline
        from jarvis.pipelines.chat import ChatPipeline
        from jarvis.pipelines.voice import VoicePipeline
        from jarvis.pipelines.device import DevicePipeline
        from jarvis.pipelines.memory import MemoryPipeline

        self.memory = MemoryPipeline()
        await self.memory.initialize()

        self.chat = ChatPipeline()
        self.voice = VoicePipeline()
        self.device = DevicePipeline()
        self.speech = SpeechPipeline()

        # Load Vosk model (non-blocking if not available)
        await self.speech.load_model()

        log.info("Engine initialized — all pipelines loaded.")

    async def process(self, text: str) -> str:
        """Process a single text input and return a response.

        Args:
            text: User input text.

        Returns:
            Response string to speak/display.
        """
        self.state = EngineState.PROCESSING

        # Classify intent
        intent, params = classify_intent(text)

        # Handle non-chat intents
        if intent == "exit":
            await self.shutdown()
            return "Shutting down. Goodbye!"

        if intent == "who_created":
            self.state = EngineState.IDLE
            return "Minaty001 made me for him, but you can use me too!"

        # Check if device can handle it
        if intent not in ("general_chat", "what_is"):
            result = await self.device.execute(intent, params)
            # For simple commands, return the device result directly
            if intent not in ("take_note", "set_reminder", "remember_fact", "search_google", "play_music", "open_website", "open_app", "close_app"):
                self.state = EngineState.IDLE
                return result

        # Build LLM context with memory
        _system_prompt, messages = await self.memory.build_context(text)

        # Get LLM response
        response = await self.chat.generate(messages)
        if response is None:
            response = "I'm having trouble thinking right now."

        # Save to memory
        await self.memory.save_exchange("user", text)
        await self.memory.save_exchange("assistant", response)

        self.state = EngineState.IDLE
        return response

    async def run(self) -> None:
        """Main interaction loop.

        Runs wake-word detection, then listens, processes, and speaks
        in a continuous cycle.
        """
        self._running = True
        log.info("Engine running. Say the wake word to activate.")

        try:
            while self._running:
                # Try voice-first: wait for wake word
                if self.speech and self.speech.model:
                    self.state = EngineState.WAKE_WORD
                    log.debug("Waiting for wake word...")
                    triggered = await self.speech.wait_for_wake()
                    if not triggered:
                        continue

                    self.state = EngineState.LISTENING
                    log.info("Wake word detected. Listening for command...")
                    command = await self.speech.listen()

                    if command:
                        response = await self.process(command)
                        self.state = EngineState.SPEAKING
                        if self.voice:
                            await self.voice.speak(response)
                    else:
                        log.debug("No command heard.")
                else:
                    # Fallback to text input
                    self.state = EngineState.TEXT_INPUT
                    try:
                        text = await asyncio.get_running_loop().run_in_executor(
                            None, lambda: input("You: ")
                        )
                        if text.strip().lower() in ("exit", "quit", "bye"):
                            break
                        response = await self.process(text)
                        print(f"JARVIS: {response}")
                    except (EOFError, KeyboardInterrupt):
                        break
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shut down all pipelines."""
        self._running = False
        if self.speech:
            await self.speech.stop()
        if self.chat:
            await self.chat.close()
        if self.memory:
            await self.memory.close()
        log.info("Engine shut down.")
