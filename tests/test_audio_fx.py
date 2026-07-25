import os
import pytest
from jarvis.pipelines.audio_fx import AudioFXPipeline


def test_generate_sound_effects(tmp_path):
    fx = AudioFXPipeline(cache_dir=str(tmp_path))

    wake_file = fx.get_sound_effect("wake")
    assert os.path.exists(wake_file)

    proto_file = fx.get_sound_effect("protocol")
    assert os.path.exists(proto_file)

    succ_file = fx.get_sound_effect("success")
    assert os.path.exists(succ_file)

    warn_file = fx.get_sound_effect("warning")
    assert os.path.exists(warn_file)


@pytest.mark.asyncio
async def test_play_fx_graceful(tmp_path):
    fx = AudioFXPipeline(cache_dir=str(tmp_path))
    # Should complete gracefully without raising uncaught exceptions
    res = await fx.play_fx("wake")
    assert isinstance(res, bool)
