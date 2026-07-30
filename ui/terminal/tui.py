"""Terminal UI — curses-based brain visualization.

Displays the 6-region cortical map with real-time activity,
neural pathway animation, and metrics.
"""

from __future__ import annotations

import asyncio
import curses
import math
import time
from typing import Any, Optional

from ui.brain_renderer import (
    COLORS,
    RESET,
    BOLD,
    DIM,
    BrainRenderer,
)
from shared.logger import log


class TUI:
    """Curses-based terminal UI showing the brain's neural network."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self._running = False
        self._stdscr: Any = None
        self._last_update = 0.0
        self._update_interval = 0.2  # 5 fps

    def _init_colors(self) -> None:
        """Initialize curses color pairs."""
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)   # PFC
        curses.init_pair(2, curses.COLOR_CYAN, -1)      # Auditory
        curses.init_pair(3, curses.COLOR_GREEN, -1)     # Wernicke
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)   # Broca
        curses.init_pair(5, curses.COLOR_RED, -1)       # Motor
        curses.init_pair(6, curses.COLOR_BLUE, -1)      # Hippocampus
        curses.init_pair(7, curses.COLOR_WHITE, -1)     # Default

    async def _draw(self) -> None:
        """Draw the brain visualization on the curses screen."""
        if not self._stdscr:
            return

        try:
            self._stdscr.clear()
            height, width = self._stdscr.getmaxyx()

            # Title
            title = "JARVIS CORTICAL NETWORK — Neural Activity Monitor"
            x = max(0, (width - len(title)) // 2)
            try:
                self._stdscr.addstr(0, x, title, curses.A_BOLD | curses.color_pair(7))
            except curses.error:
                pass

            # Build and render brain state
            state = BrainRenderer.build_state(self.engine)
            brain_str = BrainRenderer.build_region_map(state)

            # Split into lines and draw
            for i, line in enumerate(brain_str.split("\n")):
                if i + 2 >= height - 2:
                    break
                # Strip ANSI codes for curses rendering
                clean = line
                for code in [
                    "\033[38;2;255;170;0m",   # PFC amber
                    "\033[38;2;0;240;255m",   # Auditory cyan
                    "\033[38;2;0;255;136m",   # Wernicke green
                    "\033[38;2;136;68;255m",  # Broca purple
                    "\033[38;2;255;51;102m",  # Motor red
                    "\033[38;2;0;102;255m",   # Hippocampus blue
                    "\033[38;2;255;0;255m",   # Occipital magenta
                    "\033[38;2;0;255;204m",   # Somatosensory teal
                    "\033[38;2;255;51;0m",    # Defense bright red
                    "\033[38;2;255;255;0m",   # Thalamus yellow
                    "\033[38;2;170;255;0m",   # Cerebellum lime
                    RESET, BOLD, DIM,
                ]:
                    clean = clean.replace(code, "")
                try:
                    self._stdscr.addstr(i + 2, 2, clean[:width - 4])
                except curses.error:
                    pass

            # Footer
            footer = f"Crafted by Minaty001 | State: {self.engine.state.value if hasattr(self.engine, 'state') else 'N/A'} | Ctrl+C to exit"
            try:
                self._stdscr.addstr(height - 1, 0, footer[:width - 1], curses.A_DIM)
            except curses.error:
                pass

            self._stdscr.refresh()
        except curses.error:
            pass

    async def start(self) -> None:
        """Start the curses TUI and begin rendering."""
        self._running = True

        try:
            self._stdscr = curses.initscr()
            curses.cbreak()
            curses.noecho()
            curses.curs_set(0)
            self._stdscr.nodelay(1)
            self._init_colors()

            while self._running:
                # Check for 'q' or ESC to quit
                key = self._stdscr.getch()
                if key in (ord('q'), 27):  # 'q' or ESC
                    break

                now = time.time()
                if now - self._last_update >= self._update_interval:
                    await self._draw()
                    self._last_update = now

                await asyncio.sleep(0.05)  # 50ms poll
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the TUI and restore terminal settings."""
        self._running = False
        if self._stdscr:
            try:
                curses.nocbreak()
                self._stdscr.keypad(False)
                curses.echo()
                curses.curs_set(1)
                curses.endwin()
            except curses.error:
                pass
            self._stdscr = None
