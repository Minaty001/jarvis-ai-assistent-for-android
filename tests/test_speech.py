"""Tests for the Speech pipeline (Vosk STT)."""

import pytest
from jarvis.pipelines.speech import SpeechPipeline


@pytest.mark.asyncio
async def test_load_model_returns_false_without_vosk(monkeypatch):
    monkeypatch.setattr("jarvis.pipelines.speech.VoskModel", None)
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_load_model_returns_false_without_model_file(monkeypatch):
    # Simulate Vosk imported but model file missing
    class FakeVoskModel:
        def __init__(self, path):
            raise Exception("model not found")

    monkeypatch.setattr("jarvis.pipelines.speech.VoskModel", FakeVoskModel)
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_start_stop_without_model():
    pipeline = SpeechPipeline()
    await pipeline.start()  # Should not crash without model
    await pipeline.stop()


@pytest.mark.asyncio
async def test_listen_returns_none_after_timeout():
    pipeline = SpeechPipeline()
    result = await pipeline.listen(timeout=0.1)
    assert result is None
