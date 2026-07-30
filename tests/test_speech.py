"""Tests for the Speech pipeline (Groq Whisper STT)."""

import pytest
from jarvis.services.stt import SpeechPipeline
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
    monkeypatch.setattr("jarvis.services.stt._find_audio_capture", lambda: None)
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


def test_detect_wake_word():
    pipeline = SpeechPipeline()
    pipeline._wake_words = ["jarvis", "boss"]
    assert pipeline._detect_wake_word("hello jarvis, how are you") is True
    assert pipeline._detect_wake_word("yes boss") is True
    assert pipeline._detect_wake_word("glossary is here") is False  # 'gloss' should not trigger 'boss'
    assert pipeline._detect_wake_word("emboss the text") is False
