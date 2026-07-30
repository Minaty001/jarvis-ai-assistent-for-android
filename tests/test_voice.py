"""Tests for the Voice pipeline (Piper TTS)."""

import pytest
from perception.voice.tts import VoicePipeline


@pytest.mark.asyncio
async def test_speak_empty_text_is_noop():
    pipeline = VoicePipeline()
    await pipeline.speak("")  # Should not raise
    await pipeline.cancel()


@pytest.mark.asyncio
async def test_speak_then_cancel():
    pipeline = VoicePipeline()
    await pipeline.speak("hello world")
    await pipeline.cancel()  # Should not raise
    # After cancel, speaking again should work
    await pipeline.speak("another message")
    await pipeline.cancel()


@pytest.mark.asyncio
async def test_double_cancel_is_safe():
    pipeline = VoicePipeline()
    await pipeline.cancel()
    await pipeline.cancel()  # Second cancel should be safe
