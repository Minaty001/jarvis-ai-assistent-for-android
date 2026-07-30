"""Audio FX — pre-synthesized WAV bytes for Stark HUD sounds.

Pure-data: sine tones synthesized once at import time into bytes constants.
"""

from __future__ import annotations

import asyncio
import io
import struct
import wave
from typing import Optional

from jarvis.core.config import Config
from jarvis.services.base import AsyncPipeline
from jarvis.utils.logging import log


def _make_wav(freqs: list[float], dur: float = 0.15, sr: int = 22050, amp: float = 0.3) -> bytes:
    """Synthesise a WAV as bytes.  No disk IO."""
    n = int(sr * dur)
    spp = n // max(1, len(freqs))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for idx, f in enumerate(freqs):
            for i in range(spp):
                t = i / sr
                env = __import__("math").sin(3.14159 * i / spp)
                val = int(32767 * amp * env * __import__("math").sin(6.2832 * f * t))
                w.writeframesraw(struct.pack("<h", val))
    return buf.getvalue()


# Six canned sound effects — built once at module load
_FX: dict[str, bytes] = {
    "wake":     _make_wav([880.0, 1760.0], dur=0.18),
    "protocol": _make_wav([523.25, 659.25, 783.99, 1046.50], dur=0.25),
    "success":  _make_wav([1046.50, 1318.51], dur=0.12),
    "warning":  _make_wav([220.0, 180.0], dur=0.25),
    "confirm":  _make_wav([1000.0], dur=0.10),
}


class AudioFXPipeline(AsyncPipeline):
    """Play pre-synthesized sound effects via any available audio player."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def play_fx(self, fx_type: str) -> bool:
        data = _FX.get(fx_type.lower())
        if data is None:
            return False

        path = None
        try:
            import tempfile
            import os
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.write(fd, data)
            os.close(fd)

            for cmd, args in [
                ("termux-media-player", ["play", path]),
                ("paplay", [path]),
                ("aplay", [path]),
                ("play", [path]),
            ]:
                try:
                    p = await asyncio.create_subprocess_exec(
                        cmd, *args, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                    )
                    await p.wait()
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
                except Exception as e:
                    log.debug(f"audio player {cmd} failed: {e}")
            return False
        finally:
            if path:
                try:
                    __import__("os").unlink(path)
                except Exception:
                    pass
