"""Tests for Config dynamic environment variable loading."""

import pytest
from jarvis.core.config import Config


def test_config_dynamic_env_loading(monkeypatch):
    monkeypatch.setenv("SAMPLE_RATE", "22050")
    monkeypatch.setenv("LISTEN_TIMEOUT", "10.5")
    monkeypatch.setenv("GROQ_TIMEOUT", "45.0")

    cfg = Config()
    assert cfg.sample_rate == 22050
    assert cfg.listen_timeout == 10.5
    assert cfg.groq_timeout == 45.0
