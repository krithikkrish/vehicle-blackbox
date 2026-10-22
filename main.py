"""
main.py — Smart Vehicle Black Box (GPS-Only System)
----------------------------------------------------
Calibrated for standalone GPS blackbox deployment without GSM:
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : DISABLED (No SIM module required / not in use)
- Sensors     : SW-420 (Vibration), ADS1115 (MQ-3, LM35), Hall (Speed), NEO-6M (GPS)
- Dashboard   : Clean live cards + OpenStreetMap widget (No speed graph)

Run on Pi:
    python3 main.py

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
    print("  🛰️  SMART VEHICLE BLACK BOX — GPS-ONLY DEPLOYMENT")
    print("  • GPS Module : ACTIVE (NEO-6M on /dev/ttyAMA0 @ 9600 baud)")
    print("  • GSM Module : DISABLED (Not required / Not in use)")
    print("  • Telemetry  : Live GPS Map + Speed + Alcohol + Temp + Crash Log")
    print("  • Web UI     : http://blackbox.local:5000")
    print("=" * 65 + "\n")

    # Start sensor acquisition threads in GPS_ONLY mode
    sensor_manager.start_all(mode="GPS_ONLY")
    logger.info("Sensor threads launched in GPS_ONLY mode.")

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://blackbox.local:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
