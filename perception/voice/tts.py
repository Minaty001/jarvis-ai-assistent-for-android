"""Voice pipeline — Text-to-Speech (Broca's Area).

Primary: Piper TTS (local, low-latency).
Fallback: edge-tts (Microsoft Edge free cloud TTS).
Fallback: termux-tts-speak (Android TTS engine).
Cross-platform audio player support for Android Termux, Linux, and Windows.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import os
import sys
import shutil
import subprocess
import tempfile
from typing import Optional

from config.settings import Config, config as app_config
from shared.base import AsyncPipeline
from shared.logger import log


class VoicePipeline(AsyncPipeline):
    """Async TTS with Piper, edge-tts, termux-tts-speak, and cross-platform player fallbacks."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)
        self._speak_task: Optional[asyncio.Task] = None

    async def speak(self, text: str) -> None:
        """Speak text. Cancels any current speech first (interrupt behavior)."""
        await self.cancel()
        if not text.strip():
            return
        log.info(f"JARVIS: {text}")
        self._speak_task = asyncio.create_task(self._do_speak(text))

    async def _do_speak(self, text: str) -> None:
        """Internal: try Piper, then edge-tts, then termux-tts-speak, then log-only."""
        if await self._try_piper(text):
            return
        if await self._try_edge_tts(text):
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

        output_path = None
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
        finally:
            if output_path and os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception:
                    pass

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

    async def _try_edge_tts(self, text: str) -> bool:
        """Fallback: use edge-tts (Microsoft Edge free TTS)."""
        try:
            import edge_tts
        except ImportError:
            log.debug("edge_tts not installed — skipping cloud TTS fallback.")
            return False

        output_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                output_path = tmp.name
            await edge_tts.Communicate(text, voice="en-US-AriaNeural").save(output_path)
            loop = asyncio.get_running_loop()
            played = await loop.run_in_executor(None, self._play_audio_file, output_path)
            return played
        except Exception as e:
            log.debug(f"edge-tts failed: {e}")
            return False
        finally:
            if output_path and os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception:
                    pass

    def _play_wav_sync(self, path: str) -> bool:
        return self._play_audio_file(path)

    def _play_audio_file(self, path: str) -> bool:
        """Play audio file across Termux, Linux, and Windows."""
        players = [
            ["termux-media-player", "play", path],
            ["paplay", path],
            ["aplay", path],
            ["pw-play", path],
            ["ffplay", "-nodisp", "-autoexit", path],
        ]
        if sys.platform.startswith("win"):
            players.append(["powershell", "-c", f"(New-Object Media.SoundPlayer '{path}').PlaySync()"])

        for cmd in players:
            bin_name = cmd[0]
            if shutil.which(bin_name):
                try:
                    res = subprocess.run(cmd, capture_output=True, timeout=15)
                    if res.returncode == 0:
                        return True
                except Exception:
                    pass
        return False

    def _find_piper(self) -> Optional[str]:
        candidates = ["piper", os.path.expanduser("~/.local/bin/piper")]
        for c in candidates:
            found = shutil.which(c)
            if found:
                return found
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
        """Fallback: use termux-tts-speak on Android Termux."""
        if not shutil.which("termux-tts-speak"):
            return False
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
