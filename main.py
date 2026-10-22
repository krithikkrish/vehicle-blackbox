"""
main.py — Vehicle Black Box (Version 1: GSM ONLY, No GPS)
---------------------------------------------------------
Default entrypoint:
- GSM Alerts  : ENABLED (Sends crash/alcohol SOS SMS via SIM800L on /dev/ttyUSB0 or simulation)
- GPS Module  : DISABLED (UART /dev/ttyAMA0 thread omitted, serial port free)

Run on Pi:
    python3 main.py

Dashboard:  http://blackbox.local:5000
"""

import os
import sys

# Force GSM_ONLY mode before importing sensor_manager and app
os.environ["BLACKBOX_MODE"] = "GSM_ONLY"
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
    print("  🚗 VEHICLE BLACK BOX — VERSION 1: GSM ONLY (NO GPS)")
    print("  • GSM Alerts : ACTIVE (SIM800L / SMS alerts on impact)")
    print("  • GPS Module : DISABLED (No GPS UART thread running)")
    print("  • Sensors    : SW-420 (Vibration), ADS1115 (MQ-3, LM35), Hall")
    print("  • Web UI     : http://blackbox.local:5000")
    print("=" * 65 + "\n")

    # Start sensor acquisition threads in GSM_ONLY mode
    sensor_manager.start_all(mode="GSM_ONLY")
    logger.info("Sensor threads launched in GSM_ONLY mode.")

    # Start Flask (blocking)
    logger.info("Flask dashboard → http://blackbox.local:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
