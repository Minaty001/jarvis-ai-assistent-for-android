"""Logging setup for Jarvis."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from jarvis.core.config import config


def setup_logger(name: str = "jarvis") -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Logger name (default 'jarvis').

    Returns:
        Configured logger with file + console handlers.
    """
    log_file = Path(config.logs_dir) / f"{name}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


log = setup_logger()
