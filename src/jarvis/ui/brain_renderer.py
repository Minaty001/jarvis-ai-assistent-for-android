"""Brain Renderer — visualizes the cortical network of pipelines.

Renders a 6-region cortical map showing pipeline status, neural pathways,
and real-time activity metrics. Used by both terminal TUI and web UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ANSI color codes matching the cortical region palette
COLORS = {
    "pfc": {"name": "PFC", "color": "\033[38;2;255;170;0m", "hex": "#ffaa00", "label": "Executive"},
    "auditory": {"name": "Auditory", "color": "\033[38;2;0;240;255m", "hex": "#00f0ff", "label": "STT"},
    "wernicke": {"name": "Wernicke", "color": "\033[38;2;0;255;136m", "hex": "#00ff88", "label": "LLM"},
    "broca": {"name": "Broca", "color": "\033[38;2;136;68;255m", "hex": "#8844ff", "label": "TTS"},
    "motor": {"name": "Motor", "color": "\033[38;2;255;51;102m", "hex": "#ff3366", "label": "Device"},
    "hippocampus": {"name": "Hippocampus", "color": "\033[38;2;0;102;255m", "hex": "#0066ff", "label": "Memory"},
    "occipital": {"name": "Occipital", "color": "\033[38;2;255;0;255m", "hex": "#ff00ff", "label": "Vision"},
    "somatosensory": {"name": "Somatosensory", "color": "\033[38;2;0;255;204m", "hex": "#00ffcc", "label": "Telemetry"},
    "defense": {"name": "Defense", "color": "\033[38;2;255;51;0m", "hex": "#ff3300", "label": "Protocol"},
    "thalamus": {"name": "Thalamus", "color": "\033[38;2;255;255;0m", "hex": "#ffff00", "label": "Search"},
    "cerebellum": {"name": "Cerebellum", "color": "\033[38;2;170;255;0m", "hex": "#aaff00", "label": "Scheduler"},
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


@dataclass
class RegionStatus:
    """Status of a single cortical region / pipeline."""
    name: str
    color_code: str
    label: str
    active: bool = False
    latency_ms: float = 0.0
    health: str = "optimal"


@dataclass
class BrainState:
    """Complete snapshot of the brain's neural state."""
    regions: dict[str, RegionStatus] = field(default_factory=dict)
    active_pathways: list[tuple[str, str]] = field(default_factory=list)
    cortex_health: str = "OPTIMAL"
    neural_activity_pct: float = 0.0
    total_synapses: int = 10


class BrainRenderer:
    """Generates brain visualization string for terminal display."""

    @staticmethod
    def build_region_map(state: BrainState) -> str:
        """Render the 6-region cortical brain map as styled ASCII.

        Args:
            state: Current brain state snapshot.

        Returns:
            Multi-line string with colorized brain visualization.
        """
        lines = [
            f"{BOLD}{'=' * 50}{RESET}",
            f"{BOLD}   JARVIS CORTICAL NETWORK{RESET}",
            f"{BOLD}{'=' * 50}{RESET}",
            "",
        ]

        # PFC — top center
        pfc = state.regions.get("pfc")
        if pfc:
            act = "●" if pfc.active else "○"
            clr = pfc.color_code
            lines.append(f"          {clr}┌──────────────┐{RESET}")
            lines.append(f"          {clr}│ {act} PFC           │{RESET}")
            lines.append(f"          {clr}│   Executive    │{RESET}")
            lines.append(f"          {clr}└──────────────┘{RESET}")

        # Left regions (Auditory) — Right regions (Motor)
        auditory = state.regions.get("auditory")
        motor = state.regions.get("motor")
        if auditory and motor:
            a_act = "●" if auditory.active else "○"
            m_act = "●" if motor.active else "○"
            a_clr = auditory.color_code
            m_clr = motor.color_code
            blank = " " * 10
            lines.append(f"{a_clr}┌──────────┐{blank}{m_clr}┌──────────┐{RESET}")
            lines.append(f"{a_clr}│ {a_act} Auditory│{blank}{m_clr}│ {m_act} Motor   │{RESET}")
            lines.append(f"{a_clr}│   STT    │{blank}{m_clr}│  Device  │{RESET}")
            lines.append(f"{a_clr}└──────────┘{blank}{m_clr}└──────────┘{RESET}")

        # Center regions (Wernicke's + Broca's)
        wern = state.regions.get("wernicke")
        broc = state.regions.get("broca")
        if wern and broc:
            w_act = "●" if wern.active else "○"
            b_act = "●" if broc.active else "○"
            w_clr = wern.color_code
            b_clr = broc.color_code
            gap = " " * 6
            lines.append(f"     {w_clr}┌──────────┐{gap}{b_clr}┌──────────┐{RESET}")
            lines.append(f"     {w_clr}│ {w_act} Wernicke│{gap}{b_clr}│ {b_act} Broca  │{RESET}")
            lines.append(f"     {w_clr}│   LLM    │{gap}{b_clr}│  TTS    │{RESET}")
            lines.append(f"     {w_clr}└──────────┘{gap}{b_clr}└──────────┘{RESET}")

        # Hippocampus — bottom center (connections to Wernicke's)
        hipp = state.regions.get("hippocampus")
        if hipp:
            h_act = "●" if hipp.active else "○"
            h_clr = hipp.color_code
            lines.append(f"          {h_clr}┌──────────────┐{RESET}")
            lines.append(f"          {h_clr}│ {h_act} Hippocampus │{RESET}")
            lines.append(f"          {h_clr}│   Memory     │{RESET}")
            lines.append(f"          {h_clr}└──────────────┘{RESET}")

        # Neural pathways
        lines.append("")
        lines.append(f"{DIM}── Neural Pathways ──{RESET}")
        for src, dst in state.active_pathways:
            lines.append(f"  {DIM}{src} → {dst}{RESET}")
        if not state.active_pathways:
            lines.append(f"  {DIM}(idle){RESET}")

        # Metrics bar
        lines.append("")
        lines.append(f"{DIM}── Metrics ──{RESET}")
        lines.append(f"  Activity:  {state.neural_activity_pct:>5.1f}%")
        lines.append(f"  Synapses:  {state.total_synapses}")
        lines.append(f"  Cortex:    {state.cortex_health}")

        # Per-region latency
        lines.append(f"{DIM}── Latency ──{RESET}")
        for key, region in state.regions.items():
            act_mark = "●" if region.active else "○"
            lines.append(
                f"  {region.color_code}{act_mark}{RESET} "
                f"{region.name:<12} "
                f"{region.latency_ms:>6.1f}ms  "
                f"{region.health}"
            )

        lines.append("")
        lines.append(f"{DIM}── Creator ──{RESET}")
        lines.append(f"  {DIM}Crafted by Minaty001{RESET}")

        return "\n".join(lines)

    @staticmethod
    def build_web_data(state: BrainState) -> dict:
        """Build JSON-serializable brain state for web UI consumption.

        Args:
            state: Current brain state.

        Returns:
            Dict with region statuses and metrics for JSON serialization.
        """
        # Use hex color for web, fallback to ANSI if no hex available
        def _web_color(name_lower: str, region_color_code: str) -> str:
            info = COLORS.get(name_lower, {})
            return info.get("hex", region_color_code)

        return {
            "regions": {
                key: {
                    "name": r.name,
                    "color": _web_color(key, r.color_code),
                    "active": r.active,
                    "latency_ms": r.latency_ms,
                    "health": r.health,
                }
                for key, r in state.regions.items()
            },
            "active_pathways": state.active_pathways,
            "cortex_health": state.cortex_health,
            "neural_activity_pct": state.neural_activity_pct,
            "total_synapses": state.total_synapses,
        }


