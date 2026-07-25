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
import ast
import operator

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval_expr(expr: str) -> str:
    """Safely evaluate mathematical expression string."""
    expr_clean = expr.replace("^", "**").strip()
    if not expr_clean:
        return "Please specify a calculation."
    try:
        node = ast.parse(expr_clean, mode="eval")
        def _eval(n):
            if isinstance(n, ast.Expression):
                return _eval(n.body)
            elif isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                return n.value
            elif isinstance(n, ast.BinOp):
                left = _eval(n.left)
                right = _eval(n.right)
                op_type = type(n.op)
                if op_type in _SAFE_OPERATORS:
                    return _SAFE_OPERATORS[op_type](left, right)
            elif isinstance(n, ast.UnaryOp):
                operand = _eval(n.operand)
                op_type = type(n.op)
                if op_type in _SAFE_OPERATORS:
                    return _SAFE_OPERATORS[op_type](operand)
            raise ValueError("Unsupported operation")
        res = _eval(node)
        if isinstance(res, float) and res.is_integer():
            res = int(res)
        return f"The result of {expr} is {res}."
    except ZeroDivisionError:
        return "Division by zero is not defined."
    except Exception:
        return f"Could not calculate '{expr}'."


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
        self.vision = None
        self.telemetry = None
        self.protocol = None
        self.search = None
        self.scheduler = None
        self._running = False

    async def initialize(self) -> None:
        """Load all pipeline instances."""
        from jarvis.pipelines.speech import SpeechPipeline
        from jarvis.pipelines.chat import ChatPipeline
        from jarvis.pipelines.voice import VoicePipeline
        from jarvis.pipelines.device import DevicePipeline
        from jarvis.pipelines.memory import MemoryPipeline
        from jarvis.pipelines.vision import VisionPipeline
        from jarvis.pipelines.telemetry import TelemetryPipeline
        from jarvis.pipelines.protocol import ProtocolPipeline
        from jarvis.pipelines.search import SearchPipeline
        from jarvis.pipelines.scheduler import SchedulerPipeline
        from jarvis.pipelines.audio_fx import AudioFXPipeline

        self.memory = MemoryPipeline()
        await self.memory.initialize()

        self.chat = ChatPipeline()
        self.voice = VoicePipeline()
        self.device = DevicePipeline()
        self.speech = SpeechPipeline()
        self.vision = VisionPipeline()
        self.telemetry = TelemetryPipeline()
        self.protocol = ProtocolPipeline(device_pipeline=self.device, telemetry_pipeline=self.telemetry)
        self.search = SearchPipeline()
        self.scheduler = SchedulerPipeline()
        self.audio_fx = AudioFXPipeline()

        # Load Vosk model (non-blocking if not available)
        await self.speech.load_model()

        log.info("Engine initialized — all 11 cortical pipelines loaded.")

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

        # Handle memory and note/reminder intents
        if intent == "remember_fact":
            key = params.get("key", params.get("fact", text))
            val = params.get("value", params.get("fact", text))
            await self.memory.remember(key, val)
            self.state = EngineState.IDLE
            return f"I will remember that {key} is {val}."

        if intent == "take_note":
            content = params.get("content", text)
            title = content[:20] + "..." if len(content) > 20 else content
            await self.memory.save_note(title, content)
            self.state = EngineState.IDLE
            return f"Saved note: '{content}'."

        if intent == "read_notes":
            notes = await self.memory.get_notes()
            self.state = EngineState.IDLE
            if not notes:
                return "You have no saved notes."
            return "Your notes:\n" + "\n".join(f"- {n['content']}" for n in notes)

        if intent == "delete_note":
            query = params.get("query", "")
            deleted = await self.memory.delete_note(query)
            self.state = EngineState.IDLE
            return f"Deleted notes matching '{query}'." if deleted else f"No notes found matching '{query}'."

        if intent == "set_reminder":
            rem_text = params.get("text", text)
            await self.memory.save_reminder(rem_text)
            self.state = EngineState.IDLE
            return f"Set reminder: '{rem_text}'."

        if intent == "view_reminders":
            reminders = await self.memory.get_reminders()
            self.state = EngineState.IDLE
            if not reminders:
                return "You have no active reminders."
            return "Your reminders:\n" + "\n".join(f"- {r['text']}" for r in reminders)

        if intent == "delete_reminder":
            query = params.get("query", "")
            deleted = await self.memory.delete_reminder(query)
            self.state = EngineState.IDLE
            return f"Deleted reminders matching '{query}'." if deleted else f"No reminders found matching '{query}'."

        if intent == "add_custom_cmd":
            trig = params.get("trigger_phrase", "")
            act = params.get("actions", "")
            await self.memory.add_custom_command(trig, act)
            self.state = EngineState.IDLE
            return f"Custom voice command '{trig}' created successfully."

        if intent == "list_custom_cmds":
            cmds = await self.memory.list_custom_commands()
            self.state = EngineState.IDLE
            if not cmds:
                return "No custom voice commands created yet, sir."
            return "Registered custom commands:\n" + "\n".join(f"- '{c['trigger_phrase']}': {c['actions']}" for c in cmds)

        if intent == "delete_custom_cmd":
            trig = params.get("trigger_phrase", "")
            deleted = await self.memory.delete_custom_command(trig)
            self.state = EngineState.IDLE
            return f"Deleted custom command '{trig}'." if deleted else f"No custom command found for '{trig}'."

        # Check if text matches a user-defined custom command macro
        custom_action = await self.memory.get_custom_command(text)
        if custom_action:
            self.state = EngineState.IDLE
            return await self.process(custom_action)

        if intent == "calculate":
            expr = params.get("expression", "")
            self.state = EngineState.IDLE
            return _safe_eval_expr(expr)

        if intent == "tell_weather":
            loc = params.get("location", "auto")
            self.state = EngineState.IDLE
            return await self.search.get_weather(loc)

        if intent == "system_telemetry":
            self.state = EngineState.IDLE
            return await self.telemetry.format_diagnostic_report()

        if intent == "run_protocol":
            pname = params.get("protocol_name", "alpha")
            if hasattr(self, "audio_fx") and self.audio_fx:
                await self.audio_fx.play_fx("protocol")
            self.state = EngineState.IDLE
            return await self.protocol.execute_protocol(pname)

        if intent == "set_timer":
            dur_str = params.get("duration", "60")
            unit = params.get("unit", "seconds").lower()
            label = params.get("label", "Timer") or "Timer"
            try:
                seconds = float(dur_str)
                if "min" in unit:
                    seconds *= 60
            except ValueError:
                seconds = 60.0
            self.state = EngineState.IDLE
            return await self.scheduler.create_timer(label, seconds)

        if intent == "view_timers":
            timers = await self.scheduler.get_active_timers()
            self.state = EngineState.IDLE
            if not timers:
                return "No active timers currently running, sir."
            return "Active timers:\n" + "\n".join(f"- {t['label']}: {t['duration_sec']}s total" for t in timers)

        if intent == "cancel_timer":
            q = params.get("query", "")
            cancelled = await self.scheduler.cancel_timer(q)
            self.state = EngineState.IDLE
            return f"Cancelled timer matching '{q}', sir." if cancelled else f"No timer found matching '{q}'."

        if intent == "scan_vision":
            self.state = EngineState.IDLE
            return await self.vision.analyze_visual_target(query="Visual scan requested")

        if intent == "web_search_intel":
            q = params.get("query", "")
            self.state = EngineState.IDLE
            return await self.search.search_web_summary(q)

        # Check if device can handle it
        if intent not in ("general_chat", "what_is"):
            result = await self.device.execute(intent, params)
            self.state = EngineState.IDLE
            return result

        # Build LLM context with memory
        _system_prompt, messages = await self.memory.build_context(text)

        # Get LLM response with tool specifications
        from jarvis.core.tools import JARVIS_TOOL_SCHEMAS, execute_llm_tool_call
        response_obj = await self.chat.generate(messages, tools=JARVIS_TOOL_SCHEMAS)

        if response_obj is None:
            response = "I'm having trouble thinking right now."
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
