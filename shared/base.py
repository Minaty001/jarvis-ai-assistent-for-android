"""Abstract base class for all Jarvis pipelines.

Defines a minimal lifecycle contract: initialize / stop.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from config.settings import Config, config as app_config


class AsyncPipeline(ABC):
    """Minimal async lifecycle for cortical pipeline modules."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or app_config

    async def initialize(self) -> None:
        """Allocate resources, open connections, load models."""

    async def start(self) -> None:
        """Begin background work."""

    async def stop(self) -> None:
        """Halt background work and release resources."""
