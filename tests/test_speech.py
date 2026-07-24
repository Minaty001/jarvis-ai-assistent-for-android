"""Tests for the Speech pipeline (Groq Whisper STT)."""

import pytest
from jarvis.pipelines.speech import SpeechPipeline
from jarvis.core.config import config


@pytest.mark.asyncio
async def test_load_model_returns_false_without_api_key(monkeypatch):
    monkeypatch.setattr(config, "groq_api_key", "")
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_load_model_returns_false_without_capture(monkeypatch):
    monkeypatch.setattr(config, "groq_api_key", "test-key")
    monkeypatch.setattr("jarvis.pipelines.speech._find_audio_capture", lambda: None)
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_start_stop_without_model():
    pipeline = SpeechPipeline()
    await pipeline.start()  # Should not crash without model
    await pipeline.stop()


@pytest.mark.asyncio
async def test_listen_returns_none_without_capture():
    pipeline = SpeechPipeline()
    result = await pipeline.listen(timeout=0.1)
    assert result is None
