"""
main.py — Smart Vehicle Black Box Unified Entrypoint
----------------------------------------------------
Starts the background sensor telemetry threads and serves the Flask web dashboard.

Supported Modes:
  • GPS_ONLY (default) : GPS satellite tracking active, GSM alerts disabled
  • GSM_ONLY           : SIM800L SMS alerts active, GPS disabled (free UART)
  • FULL               : Both GPS tracking and GSM SMS alerts active

Usage:
    python3 main.py                  # Default GPS_ONLY or reads BLACKBOX_MODE from env
    python3 main.py --mode full      # Run with all sensors, GPS & GSM active
    python3 main.py --mode gsm       # Run in GSM-only mode
    python3 main.py --mode gps       # Run in GPS-only mode

Dashboard:  http://blackbox.local:5000 (or http://localhost:5000)
"""

import argparse
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-10s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("blackbox.log"),
    ],
)
logger = logging.getLogger(__name__)


def run(mode: str = None, port: int = None):
    """
    Launch sensor background acquisition threads and start the Flask web dashboard.
    """
    # 1. Resolve operating mode
    if mode:
        mode_str = f"{mode.upper()}_ONLY" if mode.lower() in ("gps", "gsm") else mode.upper()
    else:
        mode_str = os.environ.get("BLACKBOX_MODE", "GPS_ONLY").upper()

    if mode_str not in ("GPS_ONLY", "GSM_ONLY", "FULL"):
        logger.warning("Unrecognized mode '%s'; falling back to GPS_ONLY", mode_str)
        mode_str = "GPS_ONLY"

    os.environ["BLACKBOX_MODE"] = mode_str

    # 2. Resolve port
    if port is None:
        port = int(os.environ.get("PORT", 5000))

    # 3. Safe fallback for emergency phone if not configured
    os.environ.setdefault("EMERGENCY_PHONE", "+91XXXXXXXXXX")

    # Import app and sensor_manager after environment is configured
    import sensor_manager
    from app import app

    banner_mode = {
        "GPS_ONLY": "GPS-ONLY DEPLOYMENT (No GSM)",
        "GSM_ONLY": "GSM-ONLY DEPLOYMENT (No GPS)",
        "FULL": "FULL DEPLOYMENT (GPS & GSM ACTIVE)",
    }.get(mode_str, mode_str)

    print("\n" + "=" * 65)
    print(f"  🛰️  SMART VEHICLE BLACK BOX — {banner_mode}")
    print(f"  • Operating Mode : {mode_str}")
    print(f"  • GPS Module     : {'ACTIVE' if mode_str in ('GPS_ONLY', 'FULL') else 'DISABLED'}")
    print(f"  • GSM Module     : {'ACTIVE' if mode_str in ('GSM_ONLY', 'FULL') else 'DISABLED'}")
    print(f"  • Emergency Num  : {os.environ.get('EMERGENCY_PHONE')}")
    print(f"  • Web UI         : http://localhost:{port} (or http://blackbox.local:{port})")
    print("=" * 65 + "\n")

    # Start sensor acquisition threads
    sensor_manager.start_all(mode=mode_str)
    app._sensors_started = True
    logger.info("Sensor threads launched in %s mode.", mode_str)

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    parser = argparse.ArgumentParser(description="Vehicle Black Box Dashboard & Telemetry System")
    parser.add_argument(
        "--mode",
        choices=["gps", "gsm", "full"],
        default=None,
        help="Operational mode: 'gps' (default), 'gsm', or 'full'",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Flask dashboard port (default: 5000 or $PORT)",
    )
    args, _ = parser.parse_known_args()
    run(mode=args.mode, port=args.port)


if __name__ == "__main__":
    main()
