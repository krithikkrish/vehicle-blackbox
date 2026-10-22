"""
main_full.py — Vehicle Black Box (Version 3: BOTH GPS & GSM ACTIVE)
------------------------------------------------------------------
Full dual-module entrypoint:
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : ENABLED (SIM800L SMS alert sender on /dev/ttyUSB0)

Run on Pi:
    python3 main_full.py

Dashboard:  http://blackbox.local:5000
"""

import os
import sys

# Force FULL mode before importing sensor_manager and app
os.environ["BLACKBOX_MODE"] = "FULL"
os.environ["EMERGENCY_PHONE"] = "+919555890832"
EMERGENCY_NUM = "+919555890832"

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
    print("  🚨 VEHICLE BLACK BOX — VERSION 3: BOTH GPS & GSM ACTIVE")
    print("  • GPS Module : ACTIVE (NEO-6M on /dev/ttyAMA0 @ 9600 baud)")
    print("  • GSM Alerts : ACTIVE (SIM800L / SMS on crash with live GPS coordinates)")
    print("  • Sensors    : All sensors active (Vib, MQ-3, LM35, Hall, GPS, GSM)")
    print("  • Web UI     : http://blackbox.local:5000")
    print("=" * 65 + "\n")

    # Start sensor acquisition threads in FULL mode
    sensor_manager.start_all(mode="FULL")
    app._sensors_started = True
    logger.info("Sensor threads launched in FULL mode.")

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://blackbox.local:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
