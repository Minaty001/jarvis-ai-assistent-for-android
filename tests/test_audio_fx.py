import os
import pytest
from jarvis.pipelines.audio_fx import AudioFXPipeline, _FX


def test_sound_effects_are_prebuilt():
    assert "wake" in _FX
    assert "protocol" in _FX
    assert "success" in _FX
    assert "warning" in _FX
    assert "confirm" in _FX
    assert all(isinstance(v, bytes) and len(v) > 100 for v in _FX.values())


@pytest.mark.asyncio
async def test_play_fx_graceful():
    fx = AudioFXPipeline()
    res = await fx.play_fx("wake")
    assert isinstance(res, bool)
