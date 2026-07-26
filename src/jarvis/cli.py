"""CLI entry point for Jarvis AI Assistant. Crafted by Minaty001."""

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
        "--tui",
        action="store_true",
        help="Launch terminal UI (brain network monitor)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch Web UI server (http://0.0.0.0:5000)",
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
    await engine.initialize(silent_boot=True)
    try:
        response = await engine.process(query)
        print(f"JARVIS: {response}")
    finally:
        await engine.shutdown()


async def run_interactive(
    text_only: bool = False,
    no_voice: bool = False,
    use_tui: bool = False,
    use_web: bool = False,
) -> None:
    """Run the interactive assistant loop."""
    if text_only:
        log.info("Starting in text-only mode.")
    if no_voice:
        log.info("Voice output disabled by user request.")

    engine = Engine()
    await engine.initialize(no_voice=no_voice)

    tui_task = None
    if use_tui:
        try:
            from jarvis.ui.tui import TUI
            tui = TUI(engine)
            tui_task = asyncio.create_task(tui.start())
            log.info("Terminal UI started.")
        except Exception as e:
            log.warning(f"Could not launch Terminal UI: {e}")

    if use_web:
        try:
            import threading
            from jarvis.ui.web_ui.app import set_engine, run_server
            set_engine(engine)
            web_thread = threading.Thread(
                target=run_server,
                kwargs={"host": "0.0.0.0", "port": 5000, "debug": False},
                daemon=True,
            )
            web_thread.start()
            log.info("Web UI server running at http://0.0.0.0:5000")
        except Exception as e:
            log.warning(f"Could not launch Web UI: {e}")

    try:
        if text_only or not engine.speech or not engine.speech.model:
            # Text-only interactive mode
            if not use_tui:
                print("\nJARVIS text interface online. Type 'exit' to power down.")
            while True:
                try:
                    text = await asyncio.get_running_loop().run_in_executor(
                        None, lambda: input("\nYou: ")
                    )
                    if text.strip().lower() in ("exit", "quit", "bye"):
                        print("JARVIS: Powering down. It has been a pleasure, sir.")
                        break
                    response = await engine.process(text)
                    print(f"JARVIS: {response}")
                except (EOFError, KeyboardInterrupt):
                    print("\nJARVIS: Goodbye, sir.")
                    break
        else:
            # Voice mode with wake word
            if not use_tui:
                print("JARVIS online. Say the wake word to activate, sir.")
            await engine.run()
    finally:
        if tui_task:
            tui_task.cancel()
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
            use_tui=args.tui,
            use_web=args.web,
        ))


if __name__ == "__main__":
    main()
