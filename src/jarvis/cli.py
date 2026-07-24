"""CLI entry point for Jarvis AI Assistant."""

from __future__ import annotations

import argparse
import asyncio
import sys

from jarvis.core.config import config
from jarvis.core.engine import Engine
from jarvis.utils.logging import log


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Jarvis AI Assistant for Android — voice-controlled assistant"
    )
    parser.add_argument(
        "--text",
        "-t",
        action="store_true",
        help="Text-only mode (no voice/stt)",
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable TTS output",
    )
    parser.add_argument(
        "--once",
        "-o",
        type=str,
        metavar="QUERY",
        help="Process a single query and exit",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version and exit",
    )
    return parser


async def run_once(query: str) -> None:
    """Process a single query and print the response."""
    engine = Engine()
    await engine.initialize()
    try:
        response = await engine.process(query)
        print(f"\nJARVIS: {response}")
    finally:
        await engine.shutdown()


async def run_interactive(text_only: bool = False, no_voice: bool = False) -> None:
    """Run the interactive assistant loop."""
    if text_only:
        log.info("Starting in text-only mode.")
    if no_voice:
        log.info("Voice output disabled.")

    engine = Engine()
    await engine.initialize()

    try:
        if text_only or not engine.speech or not engine.speech.model:
            # Text-only interactive mode
            print("Jarvis AI Assistant (text mode). Type 'exit' to quit.")
            while True:
                try:
                    text = await asyncio.get_running_loop().run_in_executor(
                        None, lambda: input("\nYou: ")
                    )
                    if text.strip().lower() in ("exit", "quit", "bye"):
                        print("Goodbye!")
                        break
                    response = await engine.process(text)
                    print(f"JARVIS: {response}")
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break
        else:
            # Voice mode with wake word
            print("Jarvis AI Assistant. Say the wake word to activate.")
            await engine.run()
    finally:
        await engine.shutdown()


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        from jarvis import __version__
        print(f"Jarvis AI Assistant v{__version__}")
        sys.exit(0)

    if args.once:
        asyncio.run(run_once(args.once))
    else:
        asyncio.run(run_interactive(
            text_only=args.text,
            no_voice=args.no_voice,
        ))


if __name__ == "__main__":
    main()
