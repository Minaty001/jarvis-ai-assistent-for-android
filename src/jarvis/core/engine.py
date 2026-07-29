"""Engine orchestrator — lightweight cortical relay (Prefrontal Cortex).

Manages pipeline lifecycle, intent routing, and the main interaction loop.
Pipelines are independent; the engine routes data between them.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
from pathlib import Path
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
                if op_type is ast.Pow:
                    if abs(left) > 1000 or right > 1000 or right < -1000:
                        raise ValueError("Exponent or base out of bounds")
                if op_type in _SAFE_OPERATORS:
                    res = _SAFE_OPERATORS[op_type](left, right)
                    if isinstance(res, (int, float)) and abs(res) > 1e100:
                        raise ValueError("Calculation result out of bounds")
                    return res
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
        self.autonomy = None
        self._running = False

    async def initialize(self, no_voice: bool = False, silent_boot: bool = False) -> None:
        """Load all pipeline instances.

        Args:
            no_voice: If True, disables TTS output (voice pipeline set to None after greeting).
            silent_boot: If True, suppresses startup boot greeting voice/stdout.
        """
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
        from jarvis.pipelines.autonomy import AutonomyPipeline

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

        # Wire audio_fx into protocol for post-execution sound feedback
        self.protocol.audio_fx = self.audio_fx

        # Wire voice + audio_fx into scheduler for timer expiry alerts
        self.scheduler.voice = self.voice
        self.scheduler.audio_fx = self.audio_fx

        # Start Autonomy pipeline (background battery & health monitor)
        self.autonomy = AutonomyPipeline(
            telemetry_pipeline=self.telemetry,
            voice_pipeline=self.voice,
            check_interval_sec=60.0,
        )
        await self.autonomy.start()

        # Load STT model (non-blocking if not available)
        await self.speech.load_model()

        # If running on Termux but Termux:API binaries are missing, warn the user
        try:
            if app_config.is_termux and not app_config.termux_api_available:
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
            return "Powering down all systems. It has been a pleasure, sir. JARVIS offline."

        if intent == "who_created":
            self.state = EngineState.IDLE
            return "I was designed and built by Minaty001, sir — an architect of considerable talent. I exist to serve."

        # Handle memory and note/reminder intents
        if intent == "remember_fact":
            key = params.get("key", params.get("fact", text))
            val = params.get("value", params.get("fact", text))
            await self.memory.remember(key, val)
            self.state = EngineState.IDLE
            return f"Noted and stored in your personal archive, sir. {key}: {val}."

        if intent == "take_note":
            content = params.get("content", text)
            title = content[:20] + "..." if len(content) > 20 else content
            await self.memory.save_note(title, content)
            self.state = EngineState.IDLE
            return f"Note logged to your personal database, sir: '{content}'."

        if intent == "read_notes":
            notes = await self.memory.get_notes()
            self.state = EngineState.IDLE
            if not notes:
                return "Your personal archive is currently empty, sir. No notes on file."
            return "Retrieving your notes, sir:\n" + "\n".join(f"- {n['content']}" for n in notes)

        if intent == "search_conversation":
            query = params.get("query", "")
            results = await self.memory.search_conversation(query)
            self.state = EngineState.IDLE
            if not results:
                return f"No conversation history found matching '{query}', sir."
            formatted = "\n".join(
                f"[{r['timestamp'][:16]}] {r['role']}: {r['content'][:100]}"
                for r in results
            )
            return f"I found these entries in your conversation history, sir:\n{formatted}"

        if intent == "export_conversation":
            export_dir = Path(self.config.database_path).parent / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = export_dir / f"conversation_{stamp}.txt"
            path_str, count = await self.memory.export_conversation(filepath)
            self.state = EngineState.IDLE
            return f"Conversation history exported to {path_str}, sir. All {count} exchanges archived."

        if intent == "delete_note":
            query = params.get("query", "")
            deleted = await self.memory.delete_note(query)
            self.state = EngineState.IDLE
            return f"Note purged from archive, sir." if deleted else f"No notes matching '{query}' found in the database, sir."

        if intent == "set_reminder":
            rem_text = params.get("text", text)
            await self.memory.save_reminder(rem_text)
            self.state = EngineState.IDLE
            return f"Reminder set and standing by, sir: '{rem_text}'."

        if intent == "view_reminders":
            reminders = await self.memory.get_reminders()
            self.state = EngineState.IDLE
            if not reminders:
                return "No active reminders on record, sir. All clear."
            return "Active reminders on file, sir:\n" + "\n".join(f"- {r['text']}" for r in reminders)

        if intent == "delete_reminder":
            query = params.get("query", "")
            deleted = await self.memory.delete_reminder(query)
            self.state = EngineState.IDLE
            return f"Reminder cleared from the queue, sir." if deleted else f"No matching reminder found for '{query}', sir."

        if intent == "add_custom_cmd":
            trig = params.get("trigger_phrase", "")
            act = params.get("actions", "")
            await self.memory.add_custom_command(trig, act)
            self.state = EngineState.IDLE
            return f"Custom voice command '{trig}' registered in the system, sir. Standing by for activation."

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
            return f"Custom command '{trig}' has been removed from the registry, sir." if deleted else f"No custom command found for '{trig}', sir."

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
            # Detect recurring from original text
            is_recurring = any(w in text.lower() for w in ("recurring", "repeat", "every"))
            if is_recurring:
                return await self.scheduler.create_recurring_timer(label, seconds)
            return await self.scheduler.create_timer(label, seconds)

        if intent == "view_timers":
            timers = await self.scheduler.get_active_timers()
            self.state = EngineState.IDLE
            if not timers:
                return "No active countdowns running, sir. All timers have completed or none were set."
            lines = []
            for t in timers:
                interval = f"every {t['duration_sec']}s" if t.get("recurring") else f"{t['duration_sec']}s total"
                lines.append(f"- {t['label']} ({interval})")
            return "Active countdowns, sir:\n" + "\n".join(lines)

        if intent == "cancel_timer":
            q = params.get("query", "")
            cancelled = await self.scheduler.cancel_timer(q)
            self.state = EngineState.IDLE
            return f"Countdown aborted, sir. Timer '{q}' has been cancelled." if cancelled else f"No active timer matching '{q}' found, sir."

        if intent == "scan_vision":
            self.state = EngineState.IDLE
            return await self.vision.analyze_visual_target(query="Visual scan requested")

        if intent == "web_search_intel":
            q = params.get("query", "")
            self.state = EngineState.IDLE
            return await self.search.search_web_summary(q)

        # what_is: check memory first before sending to LLM
        if intent == "what_is":
            query_key = params.get("query", "").strip().lower()
            if query_key:
                stored = await self.memory.recall(query_key)
                if stored:
                    self.state = EngineState.IDLE
                    return f"According to your personal archive, sir: {query_key} is {stored}."

        # Intents that need state detection from the raw text
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

        # send_notigation: default title
        if intent == "send_notification":
            if "title" not in params:
                params["title"] = "JARVIS Notification"

        # Check if device can handle it
        if intent not in ("general_chat", "what_is"):
            result = await self.device.execute(intent, params)
            self.state = EngineState.IDLE
            await self.memory.save_exchange("user", text)
            await self.memory.save_exchange("assistant", result)
            return result

        # Build LLM context with memory
        _system_prompt, messages = await self.memory.build_context(text)

        # Get LLM response with tool specifications
        from jarvis.core.tools import JARVIS_TOOL_SCHEMAS, execute_llm_tool_call
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
        if self.autonomy:
            await self.autonomy.stop()
        if self.speech:
            await self.speech.stop()
        if self.chat:
            await self.chat.close()
        if self.memory:
            await self.memory.close()
        log.info("Engine shut down.")
