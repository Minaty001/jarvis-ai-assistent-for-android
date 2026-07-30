"""Flask web UI serving the Jarvis assistant interface with live brain updates.
Crafted by Minaty001."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Optional

from flask import Flask, jsonify, render_template, Response, request

from jarvis.ui.brain_renderer import BrainRenderer

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


def _run_async(coro: Any) -> Any:
    """Run an async coroutine, preferring the engine's event loop."""
    target = _engine_loop if (_engine_loop and _engine_loop.is_running()) else None
    if target is None:
        try:
            target = asyncio.get_running_loop()
        except RuntimeError:
            target = None

    if target and target.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, target)
        return future.result(timeout=30)

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        return new_loop.run_until_complete(coro)
    finally:
        new_loop.close()


@app.route("/")
def index() -> str:
    """Serve the main Jarvis interface page."""
    return render_template("index.html")


@app.route("/api/brain-state")
def brain_state() -> Response:
    """Return current brain state as JSON."""
    state = BrainRenderer.build_state(_engine_ref)
    data = BrainRenderer.build_web_data(state)
    return jsonify(data)


@app.route("/api/stream")
def stream() -> Response:
    """SSE stream of brain state updates."""
    def generate():
        while True:
            state = BrainRenderer.build_state(_engine_ref)
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
        try:
            response = _run_async(_engine_ref.process(command))
            _last_response = response
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"response": f"Error: {e}"})

    return jsonify({"response": "Engine not initialized."})


@app.route("/api/last-response")
def last_response() -> Response:
    """Return the last response text."""
    return jsonify({"response": _last_response})


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """Run the Flask web UI server."""
    app.run(host=host, port=port, debug=debug, threaded=True)
