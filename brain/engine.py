"""Engine orchestrator — lightweight cortical relay (Prefrontal Cortex).

Manages pipeline lifecycle, intent routing, and the main interaction loop.
Pipelines are independent; the engine routes data between them.
"""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import Optional

from config.settings import Config, config as app_config
from brain.intent import classify_intent
from shared.base import AsyncPipeline
from shared.logger import log


class EngineState(Enum):
    """Engine state machine states."""
    IDLE = "idle"
    WAKE_WORD = "wake_word"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    TEXT_INPUT = "text_input"


# Order matters: pipelines that provide dependencies must appear before consumers.
_PIPELINE_REGISTRY: list[tuple[str, type[AsyncPipeline]]] = []


def _get_greeting() -> str:
    """Return a time-aware JARVIS boot greeting."""
    import datetime
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 21:
        period = "evening"
    else:
        period = "night"
    return (
        f"Good {period}, sir. J.A.R.V.I.S. online. "
        "All eleven cortical systems are operational and standing by. "
        "How may I assist you today?"
    )


class Engine:
    """Lightweight orchestrator for pipeline coordination.

    Pipelines are loaded via ``_PIPELINE_REGISTRY`` which maps names to classes.
    Override with ``pipeline_overrides`` for testing / DI.
    """

    PIPELINE_REGISTRY: list[tuple[str, type[AsyncPipeline]]] = []

    def __init__(self, config: Config | None = None,
                 pipeline_overrides: dict[str, AsyncPipeline] | None = None) -> None:
        self.config = config or app_config
        self.state = EngineState.IDLE
        self._pipelines: dict[str, AsyncPipeline] = {}
        self._pipeline_overrides = pipeline_overrides or {}
        # Expose attribute references for backward-compatible access
        self.speech = None
        self.chat = None
        self.voice = None
        self.device = None
        self.memory = None
        self.vision = None
        self.telemetry = None
        self.protocol = None
        self.search = None
        self.scheduler = None
        self.autonomy = None
        self.audio_fx = None
        self._running = False

    def _get_pipeline(self, name: str) -> AsyncPipeline | None:
        """Retrieve a pipeline instance by registered name."""
        return self._pipelines.get(name)

    async def initialize(self, no_voice: bool = False, silent_boot: bool = False) -> None:
        """Load all pipeline instances.

        Args:
            no_voice: If True, disables TTS output (voice pipeline set to None after greeting).
            silent_boot: If True, suppresses startup boot greeting voice/stdout.
        """
        from perception.voice.stt import SpeechPipeline
        from ai.chat import ChatPipeline
        from perception.voice.tts import VoicePipeline
        from actions.android import DevicePipeline
        from memory.storage import MemoryPipeline
        from perception.vision import VisionPipeline
        from brain.telemetry import TelemetryPipeline
        from actions.protocols import ProtocolPipeline
        from actions.browser.search import SearchPipeline
        from actions.timers import SchedulerPipeline
        from perception.voice.audio import AudioFXPipeline
        from brain.autonomy import AutonomyPipeline

        # Internal registry with dependency-safe ordering
        registry: list[tuple[str, type[AsyncPipeline], dict]] = [
            ("memory",      MemoryPipeline,      {"config": self.config}),
            ("chat",        ChatPipeline,         {"config": self.config}),
            ("voice",       VoicePipeline,        {"config": self.config}),
            ("device",      DevicePipeline,       {"config": self.config}),
            ("speech",      SpeechPipeline,       {"config": self.config}),
            ("vision",      VisionPipeline,       {"config": self.config}),
            ("telemetry",   TelemetryPipeline,    {"config": self.config}),
            ("search",      SearchPipeline,       {"config": self.config}),
            ("audio_fx",    AudioFXPipeline,      {"config": self.config}),
        ]

        # Instantiate core pipelines (no cross-dependencies)
        for name, cls, kwargs in registry:
            pipe = self._pipeline_overrides.get(name) or cls(**kwargs)
            self._pipelines[name] = pipe
            setattr(self, name, pipe)

        # Pipelines with cross-dependencies
        self.protocol = self._pipeline_overrides.get("protocol") or ProtocolPipeline(
            config=self.config, device_pipeline=self.device, telemetry_pipeline=self.telemetry,
        )
        self._pipelines["protocol"] = self.protocol

        self.scheduler = self._pipeline_overrides.get("scheduler") or SchedulerPipeline(
            config=self.config, voice_pipeline=self.voice, audio_fx_pipeline=self.audio_fx,
        )
        self._pipelines["scheduler"] = self.scheduler

        # Wire audio_fx into protocol for post-execution sound feedback
        self.protocol.audio_fx = self.audio_fx

        # Initialize all pipelines (in dependency order)
        for name in ("memory",):  # memory first — needed by chat context
            pipe = self._pipelines.get(name)
            if pipe:
                await pipe.initialize()
        # Start all pipelines that have background work
        for name in ("memory", "telemetry"):
            pipe = self._pipelines.get(name)
            if pipe:
                await pipe.start()

        # Autonomy depends on telemetry + voice
        self.autonomy = self._pipeline_overrides.get("autonomy") or AutonomyPipeline(
            config=self.config,
            telemetry_pipeline=self.telemetry,
            voice_pipeline=self.voice,
            check_interval_sec=60.0,
        )
        self._pipelines["autonomy"] = self.autonomy
        await self.autonomy.start()

        # Load STT model (non-blocking if not available)
        await self.speech.load_model()

        # If running on Termux but Termux:API binaries are missing, warn the user
        try:
            if self.config.is_termux and not self.config.termux_api_available:
                log.warning(
                    "Termux environment detected but Termux:API binaries (termux-microphone-record/termux-tts-speak) are not available. "
                    "Install the Termux:API add-on to enable device features and voice fallbacks."
                )
        except Exception:
            pass

        log.info("Engine initialized — all 11 cortical pipelines loaded.")

        # Boot greeting
        if not silent_boot:
            greeting = _get_greeting()
            log.info(f"JARVIS: {greeting}")
            if self.voice:
                await self.voice.speak(greeting)
            else:
                print(f"JARVIS: {greeting}")

        # Disable voice AFTER greeting if --no-voice was requested
        if no_voice:
            self.voice = None
            self.scheduler.voice = None
            self.autonomy.voice = None
            log.info("Voice output disabled — TTS pipeline offline.")

    async def _preprocess_intent(self, intent: str, params: dict[str, str], text: str) -> dict[str, str]:
        """Enrich params dict with derived state for intents that need it."""
        if intent == "airplane_mode":
            text_lower = text.lower()
            if any(w in text_lower for w in ("on", "enable")):
                params["state"] = "on"
            elif any(w in text_lower for w in ("off", "disable")):
                params["state"] = "off"
            else:
                params["state"] = "toggle"

        if intent == "do_not_disturb":
            text_lower = text.lower()
            if any(w in text_lower for w in ("on", "enable", "silent")):
                params["state"] = "on"
            elif any(w in text_lower for w in ("off", "disable")):
                params["state"] = "off"
            else:
                params["state"] = "toggle"

        if intent == "send_notification":
            if "title" not in params:
                params["title"] = "JARVIS Notification"

        return params

    async def _llm_chat(self, text: str) -> str:
        """Fallback: build LLM context and call the chat pipeline."""
        _system_prompt, messages = await self.memory.build_context(text)

        from ai.tools import JARVIS_TOOL_SCHEMAS, execute_llm_tool_call
        response_obj = await self.chat.generate(messages, tools=JARVIS_TOOL_SCHEMAS)

        if response_obj is None:
            response = "I'm afraid my neural pathways are experiencing interference, sir. Please repeat your request."
        elif isinstance(response_obj, dict) and "tool_calls" in response_obj:
            tool_outputs = []
            for tc in response_obj["tool_calls"]:
                out = await execute_llm_tool_call(self, tc)
                tool_outputs.append(out)
            content_prefix = response_obj.get("content", "")
            combined_tool = "\n".join(tool_outputs)
            response = f"{content_prefix}\n{combined_tool}".strip() if content_prefix else combined_tool
        else:
            response = str(response_obj)

        await self.memory.save_exchange("user", text)
        await self.memory.save_exchange("assistant", response)
        return response

    async def process(self, text: str) -> str:
        """Process a single text input and return a response.

        Args:
            text: User input text.

        Returns:
            Response string to speak/display.
        """
        self.state = EngineState.PROCESSING

        intent, params = classify_intent(text)

        # Check if text matches a user-defined custom command macro first
        custom_action = await self.memory.get_custom_command(text)
        if custom_action:
            self.state = EngineState.IDLE
            return await self.process(custom_action)

        # Pre-process params that need state detection from raw text
        params = await self._preprocess_intent(intent, params, text)

        # Try the handler registry
        from brain.handlers import INTENT_HANDLERS
        handler = INTENT_HANDLERS.get(intent)
        if handler:
            result = await handler.handle(self, intent, params, text)
            if result is not None:
                self.state = EngineState.IDLE
                # Save conversation exchange for non-chat intents
                if intent not in ("general_chat", "what_is"):
                    await self.memory.save_exchange("user", text)
                    await self.memory.save_exchange("assistant", result)
                return result

        # LLM fallback for general_chat or what_is (when memory had no answer)
        self.state = EngineState.IDLE
        return await self._llm_chat(text)

    async def run_text_mode(self, prompt: str = "You: ") -> None:
        """Text-only interactive loop.

        Reads lines from stdin, processes them, and prints responses.
        Exits on ``exit``, ``quit``, ``bye``, or EOF/KeyboardInterrupt.
        """
        self._running = True
        try:
            while self._running:
                self.state = EngineState.TEXT_INPUT
                try:
                    text = await asyncio.get_running_loop().run_in_executor(
                        None, lambda: input(prompt)
                    )
                    if text.strip().lower() in ("exit", "quit", "bye"):
                        print("JARVIS: Powering down. It has been a pleasure, sir.")
                        break
                    response = await self.process(text)
                    print(f"JARVIS: {response}")
                except (EOFError, KeyboardInterrupt):
                    print("\nJARVIS: Goodbye, sir.")
                    break
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def run(self) -> None:
        """Main interaction loop.

        Runs wake-word detection, then listens, processes, and speaks
        in a continuous cycle. Falls back to text input if STT is unavailable.
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

                    # Play wake audio FX and speak acknowledgement
                    if hasattr(self, "audio_fx") and self.audio_fx:
                        await self.audio_fx.play_fx("wake")
                    if self.voice:
                        await self.voice.speak("Yes, sir?")

                    command = await self.speech.listen()

                    if command:
                        response = await self.process(command)
                        self.state = EngineState.SPEAKING
                        if self.voice:
                            await self.voice.speak(response)
                    else:
                        log.debug("No command heard.")
                else:
                    await self.run_text_mode(prompt="You: ")
                    break
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shut down all pipelines."""
        self._running = False
        for name in ("autonomy", "speech", "scheduler", "chat", "memory", "telemetry", "vision", "voice", "device", "search", "protocol", "audio_fx"):
            pipe = self._pipelines.get(name)
            if pipe and hasattr(pipe, "stop"):
                try:
                    await pipe.stop()
                except Exception:
                    pass
        log.info("Engine shut down.")
