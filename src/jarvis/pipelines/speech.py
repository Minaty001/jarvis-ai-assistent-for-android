"""Speech pipeline — Vosk STT and wake word detection (Auditory Cortex).

Captures microphone audio, performs speech-to-text via Vosk,
and detects wake words for hands-free activation.
"""

from __future__ import annotations

import asyncio
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log

try:
    import numpy as np
    import sounddevice as sd
except (ImportError, OSError):
    np = None
    sd = None

try:
    from vosk import Model as VoskModel, KaldiRecognizer
except ImportError:
    VoskModel = None
    KaldiRecognizer = None

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR_NAME = "vosk-model-small-en-us-0.15"


class SpeechPipeline:
    """Async speech recognition with wake word detection."""

    def __init__(self) -> None:
        self.model_path = Path(app_config.models_dir) / VOSK_MODEL_DIR_NAME
        self.model: Any = None
        self.recognizer: Any = None
        self.stt_queue: asyncio.Queue[str] = asyncio.Queue()
        self.wake_event = asyncio.Event()
        self._stream: Any = None
        self._running = False
        self._wake_words = app_config.wake_words
        self._on_utterance: Optional[Callable] = None

    def set_on_speech_detected(self, callback: Callable) -> None:
        """Register callback for speech detection during TTS (interrupt)."""
        self._on_utterance = callback

    async def load_model(self) -> bool:
        """Load Vosk model. Returns True if successful."""
        if VoskModel is None:
            log.warning("Vosk not installed. STT unavailable.")
            return False

        if not self.model_path.exists():
            log.info("Vosk model not found. Downloading...")
            return await self._download_model()

        try:
            self.model = VoskModel(str(self.model_path))
            log.info("Vosk model loaded successfully.")
            return True
        except Exception as e:
            log.error(f"Failed to load Vosk model: {e}")
            return False

    async def _download_model(self) -> bool:
        """Download and extract Vosk model."""
        zip_path = Path(app_config.models_dir) / f"{VOSK_MODEL_DIR_NAME}.zip"
        try:
            def _dl():
                urllib.request.urlretrieve(VOSK_MODEL_URL, zip_path)
            await asyncio.get_running_loop().run_in_executor(None, _dl)
            log.info("Downloaded Vosk model. Extracting...")

            def _extract():
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(app_config.models_dir)
                zip_path.unlink()
            await asyncio.get_running_loop().run_in_executor(None, _extract)
            log.info("Vosk model extracted.")
            return await self.load_model()
        except Exception as e:
            log.error(f"Failed to download Vosk model: {e}")
            return False

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """sounddevice callback — feeds audio to Vosk recognizer."""
        if status:
            log.debug(f"Audio status: {status}")
        if self.recognizer is None:
            return

        data = indata.copy()
        if data.dtype != np.int16:
            data = (data * 32767).astype(np.int16)
        audio_bytes = data.tobytes()

        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip().lower()
            if text:
                log.debug(f"STT final: {text}")
                asyncio.run_coroutine_threadsafe(
                    self.stt_queue.put(text), asyncio.get_running_loop()
                )
                if self._on_utterance:
                    asyncio.run_coroutine_threadsafe(
                        self._on_utterance(text), asyncio.get_running_loop()
                    )
        else:
            partial = json.loads(self.recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip().lower()
            if partial_text and any(w in partial_text for w in self._wake_words):
                if not self.wake_event.is_set():
                    log.info(f"Wake word detected in: '{partial_text}'")
                    asyncio.run_coroutine_threadsafe(
                        self.wake_event.set(), asyncio.get_running_loop()
                    )

    async def start(self) -> None:
        """Start microphone capture and recognition."""
        if self.model is None or sd is None:
            log.warning("STT not available (model or sounddevice missing).")
            return

        try:
            self.recognizer = KaldiRecognizer(self.model, app_config.sample_rate)
            self.recognizer.SetWords(False)
            self._running = True

            def _open_stream():
                self._stream = sd.InputStream(
                    samplerate=app_config.sample_rate,
                    channels=1,
                    dtype="int16",
                    callback=self._audio_callback,
                    blocksize=8000,
                )
                self._stream.start()

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _open_stream)
            log.info("Microphone started. Listening...")
        except Exception as e:
            log.error(f"Failed to start microphone: {e}")
            self._running = False

    async def stop(self) -> None:
        """Stop microphone capture."""
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    async def wait_for_wake(self) -> bool:
        """Wait until wake word is detected. Returns True if triggered."""
        self.wake_event.clear()
        try:
            await asyncio.wait_for(self.wake_event.wait(), timeout=None)
            return True
        except asyncio.CancelledError:
            return False

    async def listen(self, timeout: float | None = None) -> Optional[str]:
        """Wait for a spoken command with timeout. Returns text or None."""
        try:
            text = await asyncio.wait_for(
                self.stt_queue.get(), timeout=timeout or app_config.listen_timeout
            )
            return text
        except asyncio.TimeoutError:
            return None
