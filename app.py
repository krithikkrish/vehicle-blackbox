"""
app.py
Flask web dashboard for the Vehicle Black Box System.
Run: python app.py  →  http://blackbox.local:5000
"""

import logging
import os
from flask import Flask, jsonify, render_template, abort

import sensor_manager
import data_logger
import circular_buffer

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)


# ── Start sensor threads when app starts ─────────────────────────────────────
@app.before_request
def startup():
    # Only start once (guarded by a flag on the app object)
    if not getattr(app, "_sensors_started", False):
        app._sensors_started = True
        mode = os.environ.get("BLACKBOX_MODE", "GPS_ONLY")
        sensor_manager.start_all(mode=mode)


# ─────────────────────────────────────────────────────────────────────────────
# HTML Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Main live dashboard."""
    return render_template("dashboard.html")


@app.route("/logs")
def logs_page():
    """Crash log listing page."""
    logs = data_logger.list_crash_logs()
    return render_template("logs.html", logs=logs)


@app.route("/logs/<filename>")
def log_detail(filename: str):
    """Detail view for a single crash log."""
    # Safety: only allow filenames, no path traversal
    if "/" in filename or ".." in filename:
        abort(400)
    log = data_logger.load_crash_log(filename)
    if log is None:
        abort(404)
    return render_template("log_detail.html", log=log, filename=filename)


# ─────────────────────────────────────────────────────────────────────────────
# JSON API Routes (polled by dashboard JS every second)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/live")
def api_live():
    """Latest sensor snapshot."""
    return jsonify(sensor_manager.get_state())


@app.route("/api/history")
def api_history():
    """Last N entries from the circular buffer (for mini chart)."""
    entries = circular_buffer.get_all()
    # Return last 60 for chart (last ~6 seconds at 10 Hz)
    return jsonify(entries[-60:])


@app.route("/api/logs")
def api_logs():
    """List of crash log files as JSON."""
    return jsonify(data_logger.list_crash_logs())


@app.route("/api/logs/<filename>")
def api_log_detail(filename: str):
    if "/" in filename or ".." in filename:
        abort(400)
    log = data_logger.load_crash_log(filename)
    if log is None:
        abort(404)
    return jsonify(log)


@app.route("/api/reset_crash", methods=["POST", "GET"])
def api_reset_crash():
    """Acknowledge and reset the crash alert state."""
    sensor_manager.reset_crash_state()
    return jsonify({"status": "ok", "message": "Crash alarm reset"})



# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting Vehicle Black Box Flask server …")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
