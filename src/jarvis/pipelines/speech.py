"""Speech pipeline — Groq Whisper STT and wake word detection (Auditory Cortex).

Captures microphone audio via available methods (sounddevice, termux-microphone-record),
sends to Groq Whisper API for transcription, and detects wake words.
Gracefully degrades when no audio capture or API key is available.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any, Callable, Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log

try:
    import sounddevice as sd
    import numpy as np
except (ImportError, OSError):
    sd = None
    np = None


# Wake word detection runs on transcribed text, so we check if any
# configured wake word appears in the Whisper output.
WAKE_CHECK_INTERVAL = 2.5  # seconds of audio to capture per wake-word check
LISTEN_DURATION = 6.0  # seconds of audio to capture for a command


def _find_audio_capture() -> str | None:
    """Probe available audio capture methods.

    Returns a method name string or None if none found.
    """
    # 1. sounddevice (PortAudio) — desktop Linux, macOS, Windows
    if sd is not None:
        try:
            devices = sd.query_devices()
            if any(d.get("max_input_channels", 0) > 0 for d in devices):
                return "sounddevice"
        except Exception:
            pass

    for probe_name, probe_args in [
        ("termux-mic", ["termux-microphone-record", "--help"]),
        ("arecord", ["arecord", "--version"]),
    ]:
        try:
            proc = subprocess.run(probe_args, capture_output=True, timeout=3)
            if proc.returncode in (0, 1):
                return probe_name
        except Exception:
            pass

    return None


def _wav_bytes(raw_data: bytes, sample_rate: int, nchannels: int = 1, sampwidth: int = 2) -> bytes:
    """Wrap raw PCM bytes in WAV container, return WAV bytes."""
    buf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    filename = buf.name
    buf.close()
    try:
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(nchannels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_data)
        with open(filename, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(filename)
        except Exception:
            pass



def _record_sounddevice(duration: float, sample_rate: int = 16000) -> bytes | None:
    """Record audio using sounddevice, return WAV bytes."""
    if sd is None or np is None:
        return None
    try:
        frames = int(duration * sample_rate)
        recording = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
        return _wav_bytes(recording.tobytes(), sample_rate)
    except Exception as e:
        log.debug(f"sounddevice record failed: {e}")
        return None


def _record_termux_mic(duration: float, sample_rate: int = 16000) -> bytes | None:
    """Record audio using termux-microphone-record."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    try:
        proc = subprocess.run(
            ["termux-microphone-record", "-f", tmp.name, "-d", str(int(duration))],
            capture_output=True, timeout=int(duration) + 5,
        )
        if proc.returncode != 0:
            return None
        with open(tmp.name, "rb") as f:
            return f.read()
    except Exception as e:
        log.debug(f"termux-mic record failed: {e}")
        return None
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def _record_arecord(duration: float, sample_rate: int = 16000) -> bytes | None:
    """Record audio using arecord (ALSA)."""
    frames = int(duration * sample_rate)
    try:
        proc = subprocess.run(
            ["arecord", "-t", "raw", "-f", "S16_LE", "-r", str(sample_rate),
             "-c", "1", "-d", str(int(duration))],
            capture_output=True, timeout=int(duration) + 5,
        )
        if proc.returncode != 0:
            return None
        return _wav_bytes(proc.stdout, sample_rate)
    except Exception as e:
        log.debug(f"arecord failed: {e}")
        return None


_RECORDERS = {
    "sounddevice": _record_sounddevice,
    "termux-mic": _record_termux_mic,
    "arecord": _record_arecord,
}


def _transcribe(audio_bytes: bytes, api_key: str) -> str | None:
    """Send WAV audio bytes to Groq Whisper API and return transcribed text."""
    try:
        import httpx
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": ("audio.wav", audio_bytes, "audio/wav")},
                data={"model": "whisper-large-v3", "language": "en"},
            )
            if resp.status_code != 200:
                log.warning(f"Whisper API error {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            return data.get("text", "").strip().lower()
    except Exception as e:
        log.debug(f"Whisper transcription failed: {e}")
        return None


class SpeechPipeline:
    """Async speech recognition with wake word detection via Groq Whisper API."""

    def __init__(self) -> None:
        self.model: Any = None  # Kept for engine compatibility checks
        self.recognizer: Any = None
        self.stt_queue: asyncio.Queue[str] = asyncio.Queue()
        self.wake_event = asyncio.Event()
        self._stream: Any = None
        self._running = False
        self._wake_words = app_config.wake_words
        self._capture_method: str | None = None
        self._api_key: str = ""
        self._on_utterance: Optional[Callable] = None

    def set_on_speech_detected(self, callback: Callable) -> None:
        """Register callback for speech detection (used for TTS interrupt)."""
        self._on_utterance = callback

    async def load_model(self) -> bool:
        """Check availability of Groq API key and audio capture.

        Returns True if STT is usable (both API key and audio capture available).
        """
        self._api_key = app_config.groq_api_key or os.getenv("GROQ_API_KEY", "")
        if not self._api_key:
            log.warning("GROQ_API_KEY not set. STT unavailable.")
            return False

        # Probe audio capture methods in a thread to avoid blocking
        loop = asyncio.get_running_loop()
        method = await loop.run_in_executor(None, _find_audio_capture)
        if method is None:
            log.warning("No microphone capture method found. STT unavailable.")
            return False

        self._capture_method = method
        log.info(f"STT ready — using '{method}' capture + Groq Whisper API.")
        self.model = True  # Signal to engine that speech is available
        return True

    async def start(self) -> None:
        """Start listening (capture method selected during load_model)."""
        if self._capture_method is None:
            log.warning("STT not available (no audio capture).")
            return
        self._running = True
        log.info(f"Microphone ready ({self._capture_method}). Listening...")

    def _detect_wake_word(self, text: str) -> bool:
        """Check if any configured wake word appears as a word in the transcribed text."""
        import re
        for ww in self._wake_words:
            if re.search(r"\b" + re.escape(ww) + r"\b", text, re.IGNORECASE):
                return True
        return False

    async def _capture_and_transcribe(self, duration: float) -> str | None:
        """Record audio and transcribe via Whisper. Returns lowercase text or None."""
        recorder = _RECORDERS.get(self._capture_method)
        if recorder is None:
            return None

        try:
            loop = asyncio.get_running_loop()
            audio = await loop.run_in_executor(None, recorder, duration, app_config.sample_rate)
            if audio is None:
                return None

            text = await loop.run_in_executor(None, _transcribe, audio, self._api_key)
            return text
        except Exception as e:
            log.debug(f"Audio capture/transcription error: {e}")
            return None

    async def wait_for_wake(self) -> bool:
        """Loop: capture short audio chunks and check for wake word.

        Returns True when a wake word is detected, False if cancelled.
        """
        self.wake_event.clear()
        log.debug("Waiting for wake word...")

        while self._running:
            text = await self._capture_and_transcribe(WAKE_CHECK_INTERVAL)
            if text and self._detect_wake_word(text):
                log.info(f"Wake word detected — '{text}'")
                self.wake_event.set()
                return True
            # Small yield so cancellation can be caught
            await asyncio.sleep(0.1)

        return False

    async def listen(self, timeout: float | None = None) -> Optional[str]:
        """Capture audio and return transcribed text.

        Args:
            timeout: Maximum seconds to wait for speech.
                     Falls back to app_config.listen_timeout when None.

        Returns:
            Transcribed text string, or None on timeout/failure.
        """
        duration = timeout or app_config.listen_timeout
        text = await self._capture_and_transcribe(duration)

        if text:
            log.debug(f"STT result: {text}")
            if self._on_utterance:
                asyncio.create_task(self._on_utterance(text))
            return text

        return None

    async def stop(self) -> None:
        """Stop listening."""
        self._running = False
        log.debug("Speech pipeline stopped.")
