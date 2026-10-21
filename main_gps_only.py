"""
main_gps_only.py — Vehicle Black Box (Version 2: GPS ONLY, No GSM)
-----------------------------------------------------------------
GPS-only entrypoint:
- GPS Module  : ENABLED (NEO-6M NMEA parser active on /dev/ttyAMA0, 9600 baud)
- GSM Alerts  : DISABLED (No SMS transmission attempts, avoiding port conflicts)

Run on Pi:
    python3 main_gps_only.py

Dashboard:  http://blackbox.local:5000
"""

import os
import sys

# Force GPS_ONLY mode before importing sensor_manager and app
os.environ["BLACKBOX_MODE"] = "GPS_ONLY"

import logging
import sensor_manager
from app import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-10s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("blackbox.log"),
    ],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  🛰️ VEHICLE BLACK BOX — VERSION 2: GPS ONLY (NO GSM)")
    print("  • GPS Module : ACTIVE (NEO-6M on /dev/ttyAMA0 @ 9600 baud)")
    print("  • GSM Alerts : DISABLED (No SMS alerts dispatched)")
    print("  • Sensors    : SW-420 (Vibration), ADS1115 (MQ-3, LM35), Hall, GPS")
    print("  • Web UI     : http://blackbox.local:5000")
    print("=" * 65 + "\n")

    # Start sensor acquisition threads in GPS_ONLY mode
    sensor_manager.start_all(mode="GPS_ONLY")
    logger.info("Sensor threads launched in GPS_ONLY mode.")

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://blackbox.local:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
