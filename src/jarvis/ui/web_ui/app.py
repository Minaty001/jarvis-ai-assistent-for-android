"""Flask web UI serving the Jarvis assistant interface with live brain updates.
Crafted by Minaty001."""

from __future__ import annotations

import asyncio
import json
import math
import time
from typing import Any, Optional

from flask import Flask, jsonify, render_template, Response, request

from jarvis.ui.brain_renderer import COLORS, BrainRenderer, BrainState, RegionStatus
from jarvis.core.intent import classify_intent

app = Flask(__name__)

# In-memory engine reference (set externally)
_engine_ref: Any = None
_last_response: str = ""
_engine_loop: Optional[asyncio.AbstractEventLoop] = None


def set_engine(engine: Any) -> None:
    """Set the engine reference for live state reading."""
    global _engine_ref, _engine_loop
    _engine_ref = engine
    try:
        _engine_loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            _engine_loop = asyncio.get_event_loop()
        except RuntimeError:
            _engine_loop = None


def _build_state() -> BrainState:
    """Build current brain state from engine or simulated data."""
    state = BrainState()
    now = time.time()

    eng_state = "idle"
    if _engine_ref and hasattr(_engine_ref, 'state'):
        eng_state = str(_engine_ref.state)

    region_active = {
        "pfc": eng_state in ("processing", "listening", "speaking"),
        "auditory": eng_state in ("wake_word", "listening"),
        "wernicke": eng_state in ("processing",),
        "broca": eng_state in ("speaking",),
        "motor": eng_state in ("processing",),
        "hippocampus": True,
        "occipital": eng_state in ("processing",),
        "somatosensory": True,
        "defense": eng_state in ("processing",),
        "thalamus": eng_state in ("processing",),
        "cerebellum": True,
    }

    latencies = {
        "pfc": 5.0 + (2.0 * math.sin(now * 0.5)),
        "auditory": 120.0 if region_active["auditory"] else 0.0,
        "wernicke": 450.0 if region_active["wernicke"] else 0.0,
        "broca": 800.0 if region_active["broca"] else 0.0,
        "motor": 50.0 if region_active["motor"] else 0.0,
        "hippocampus": 3.0,
        "occipital": 150.0 if region_active["occipital"] else 0.0,
        "somatosensory": 10.0,
        "defense": 80.0 if region_active["defense"] else 0.0,
        "thalamus": 200.0 if region_active["thalamus"] else 0.0,
        "cerebellum": 5.0,
    }

    for key, info in COLORS.items():
        state.regions[key] = RegionStatus(
            name=info["name"],
            color_code=info["color"],
            label=info["label"],
            active=region_active.get(key, False),
            latency_ms=latencies.get(key, 0.0),
            health="active" if region_active.get(key, False) else "standby",
        )

    pathways = []
    if region_active["auditory"]:
        pathways.append(("Auditory", "Wernicke"))
    if region_active["wernicke"]:
        pathways.append(("Wernicke", "Broca"))
        pathways.append(("Wernicke", "Hippocampus"))
        pathways.append(("Wernicke", "Thalamus"))
    if region_active["motor"]:
        pathways.append(("PFC", "Motor"))
    if region_active["occipital"]:
        pathways.append(("Occipital", "PFC"))
    if region_active["defense"]:
        pathways.append(("PFC", "Defense"))
    state.active_pathways = pathways

    active_count = sum(1 for v in region_active.values() if v)
    state.neural_activity_pct = (active_count / 11) * 100
    state.cortex_health = "OPTIMAL" if active_count <= 8 else "HIGH LOAD"
    state.total_synapses = len(pathways)

    return state


@app.route("/")
def index() -> str:
    """Serve the main Jarvis interface page."""
    return render_template("index.html")


@app.route("/api/brain-state")
def brain_state() -> Response:
    """Return current brain state as JSON."""
    state = _build_state()
    data = BrainRenderer.build_web_data(state)
    return jsonify(data)


@app.route("/api/stream")
def stream() -> Response:
    """SSE stream of brain state updates."""
    def generate():
        while True:
            state = _build_state()
            data = BrainRenderer.build_web_data(state)
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/command", methods=["POST"])
def handle_command() -> Response:
    """Process a text command and return the response."""
    global _last_response
    data = request.get_json(silent=True) or {}
    command = data.get("command", "").strip()

    if not command:
        return jsonify({"response": "No command received."})

    if _engine_ref and hasattr(_engine_ref, 'process'):
        import asyncio
        try:
            target_loop = _engine_loop if (_engine_loop and _engine_loop.is_running()) else None
            if not target_loop:
                try:
                    target_loop = asyncio.get_running_loop()
                except RuntimeError:
                    target_loop = None

            if target_loop and target_loop.is_running():
                future = asyncio.run_coroutine_threadsafe(_engine_ref.process(command), target_loop)
                response = future.result(timeout=30)
            else:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    response = new_loop.run_until_complete(_engine_ref.process(command))
                finally:
                    new_loop.close()

            _last_response = response
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"response": f"Error: {e}"})

    # Fallback: classify and respond
    intent, params = classify_intent(command)
    return jsonify({"response": f"Intent recognized: {intent} — {params}"})


@app.route("/api/last-response")
def last_response() -> Response:
    """Return the last response text."""
    return jsonify({"response": _last_response})


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """Run the Flask web UI server."""
    app.run(host=host, port=port, debug=debug, threaded=True)
