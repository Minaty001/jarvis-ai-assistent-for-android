"""Tests for the Voice pipeline (Piper TTS)."""

import os
from pathlib import Path
import subprocess
import sys

import pytest
from jarvis.pipelines.voice import VoicePipeline


def test_voice_pipeline_imports_when_edge_tts_is_missing():
    """Missing edge-tts should not prevent the Android TTS fallback from loading."""
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(repo_root / "src"), env.get("PYTHONPATH", "")]
    )
    code = """
import builtins
real_import = builtins.__import__

def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "edge_tts":
        raise ImportError("simulated missing edge_tts")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = fake_import
import jarvis.pipelines.voice as voice
assert voice.edge_tts is None
assert voice.VoicePipeline is not None
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr


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
