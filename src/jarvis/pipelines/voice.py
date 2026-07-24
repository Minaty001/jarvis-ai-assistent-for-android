"""Voice pipeline — Text-to-Speech (Broca's Area).

Primary: Piper TTS (local, low-latency).
Fallback: termux-tts-speak (Android TTS engine).
Final fallback: log only.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from typing import Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log


class VoicePipeline:
    """Async TTS with Piper (preferred) and termux-tts-speak fallback."""

    def __init__(self) -> None:
        self._speak_task: Optional[asyncio.Task] = None

    async def speak(self, text: str) -> None:
        """Speak text. Cancels any current speech first (interrupt behavior).

        Args:
            text: Text to speak aloud.
        """
        await self.cancel()
        if not text.strip():
            return
        log.info(f"JARVIS: {text}")
        self._speak_task = asyncio.create_task(self._do_speak(text))

    async def _do_speak(self, text: str) -> None:
        """Internal: try Piper, then termux-tts-speak, then log-only."""
        if await self._try_piper(text):
            return
        if await self._try_termux_tts(text):
            return
        log.info(f"(TTS unavailable) Would say: {text}")

    async def _try_piper(self, text: str) -> bool:
        """Try Piper TTS. Returns True if speech was produced."""
        piper = self._find_piper()
        voice = self._find_piper_voice()
        if not piper or not voice:
            return False

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, self._run_piper_sync, piper, voice, text, output_path
            )
            await loop.run_in_executor(None, self._play_wav_sync, output_path)
            return True
        except Exception as e:
            log.debug(f"Piper TTS failed: {e}")
            return False

    def _run_piper_sync(self, piper_bin: str, voice_path: str, text: str, output_path: str) -> None:
        try:
            proc = subprocess.run(
                [piper_bin, "--model", voice_path, "--output_file", output_path],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
            if proc.returncode != 0:
                log.warning(f"Piper error: {proc.stderr.decode(errors='replace')[:200]}")
        except Exception as e:
            log.debug(f"Piper execution failed: {e}")

    def _play_wav_sync(self, path: str) -> None:
        try:
            subprocess.run(["termux-media-player", "play", path], capture_output=True, timeout=10)
        except Exception:
            try:
                subprocess.run(["aplay", path], capture_output=True, timeout=10)
            except Exception:
                pass
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass

    def _find_piper(self) -> Optional[str]:
        candidates = ["piper", os.path.expanduser("~/.local/bin/piper")]
        for c in candidates:
            try:
                proc = subprocess.run(["which", c], capture_output=True, timeout=5)
                if proc.returncode == 0:
                    return c.strip()
            except Exception:
                continue
        return None

    def _find_piper_voice(self) -> Optional[str]:
        voices_dir = os.path.expanduser(app_config.voices_dir)
        for root, _dirs, files in os.walk(voices_dir):
            for f in files:
                if f.endswith(".onnx"):
                    return os.path.join(root, f)
        voice_name = os.getenv("PIPER_VOICE", "en_US-amy-medium")
        specific = os.path.join(voices_dir, f"{voice_name}.onnx")
        if os.path.exists(specific):
            return specific
        return None

    async def _try_termux_tts(self, text: str) -> bool:
        """Fallback: use termux-tts-speak."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-tts-speak",
                "-r", str(app_config.tts_rate),
                "-p", str(app_config.tts_pitch),
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def cancel(self) -> None:
        """Cancel current speech."""
        if self._speak_task and not self._speak_task.done():
            self._speak_task.cancel()
            try:
                await self._speak_task
            except (asyncio.CancelledError, Exception):
                pass
        self._speak_task = None
