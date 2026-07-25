"""Audio FX Pipeline — Multi-Modal Stark Audio Sound Effects.

Synthesizes sci-fi HUD sound effects (activation chimes, protocol pulses, confirmation beeps).
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import math
import os
import struct
import wave
from typing import Optional
from jarvis.utils.logging import log


class AudioFXPipeline:
    """Synthesizer and player for Stark HUD audio feedback."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        self.cache_dir = cache_dir or "/tmp/jarvis_audio_fx"
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_sine_wave(
        self,
        filepath: str,
        frequencies: list[float],
        duration_sec: float = 0.15,
        sample_rate: int = 22050,
        amplitude: float = 0.3,
    ) -> str:
        """Generate a WAV file containing synthesized tone sequence."""
        if os.path.exists(filepath):
            return filepath

        n_samples = int(sample_rate * duration_sec)
        num_freqs = len(frequencies)
        samples_per_freq = n_samples // max(1, num_freqs)

        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            for idx, freq in enumerate(frequencies):
                for i in range(samples_per_freq):
                    t = float(i) / sample_rate
                    # Fade envelope
                    envelope = math.sin(math.pi * i / samples_per_freq)
                    value = int(32767 * amplitude * envelope * math.sin(2.0 * math.pi * freq * t))
                    data = struct.pack("<h", value)
                    wav_file.writeframesraw(data)

        return filepath

    def get_sound_effect(self, fx_type: str) -> str:
        """Get or generate the WAV file path for a sound effect type.

        Supported fx_types: 'wake', 'protocol', 'success', 'warning', 'confirm'
        """
        fx_type = fx_type.lower()
        if fx_type == "wake":
            # Rising futuristic double tone (880Hz -> 1760Hz)
            path = os.path.join(self.cache_dir, "fx_wake.wav")
            return self._generate_sine_wave(path, [880.0, 1760.0], duration_sec=0.18)
        elif fx_type == "protocol":
            # Stark HUD security pulse (523Hz -> 659Hz -> 783Hz -> 1046Hz)
            path = os.path.join(self.cache_dir, "fx_protocol.wav")
            return self._generate_sine_wave(path, [523.25, 659.25, 783.99, 1046.50], duration_sec=0.25)
        elif fx_type == "success":
            # Confirmation chime (1046Hz -> 1318Hz)
            path = os.path.join(self.cache_dir, "fx_success.wav")
            return self._generate_sine_wave(path, [1046.50, 1318.51], duration_sec=0.12)
        elif fx_type == "warning":
            # Low frequency warning buzz (220Hz -> 180Hz)
            path = os.path.join(self.cache_dir, "fx_warning.wav")
            return self._generate_sine_wave(path, [220.0, 180.0], duration_sec=0.25)
        else:
            # Default blip (1000Hz)
            path = os.path.join(self.cache_dir, "fx_confirm.wav")
            return self._generate_sine_wave(path, [1000.0], duration_sec=0.1)

    async def play_fx(self, fx_type: str) -> bool:
        """Asynchronously play a sound effect using available system tools."""
        sound_path = self.get_sound_effect(fx_type)
        if not sound_path or not os.path.exists(sound_path):
            return False

        # Try termux-media-player, paplay, aplay, or play
        players = [
            ("termux-media-player", ["play", sound_path]),
            ("paplay", [sound_path]),
            ("aplay", [sound_path]),
            ("play", [sound_path]),
        ]

        for cmd, args in players:
            try:
                proc = await asyncio.create_subprocess_exec(
                    cmd, *args,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await proc.wait()
                if proc.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
            except Exception as e:
                log.debug(f"Audio player {cmd} failed: {e}")
                continue

        log.debug(f"No audio player available to play sound effect '{fx_type}'.")
        return False
