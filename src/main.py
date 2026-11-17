#!/usr/bin/env python3
"""
src/main.py — Vehicle Black Box Headless CLI Entrypoint
-------------------------------------------------------
Runs the 10Hz sampling loop in the terminal without starting the web server.

Modes:
  • GPS_ONLY (default) : GPS satellite tracking active, GSM alerts disabled
  • GSM_ONLY           : SIM800L SMS alerts active, GPS disabled
  • FULL               : Both GPS tracking and GSM SMS alerts active

Usage:
    python3 src/main.py
    python3 src/main.py --mode full
    python3 src/main.py --mode gsm
"""

import argparse
import os
import sys
import time

# Ensure local imports work when running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from alerts import AlertSystem
from buffer import CircularBuffer, CSVLogger
from crash_logic import CrashDetector
from sensors import SensorInterface

LOOP_DELAY_SEC = 0.1  # 10Hz sampling


def run_cli(mode: str = "GPS_ONLY"):
    mode_clean = (mode or os.environ.get("BLACKBOX_MODE", "GPS_ONLY")).strip().upper()
    enable_gps = mode_clean in ("GPS", "GPS_ONLY", "FULL")
    enable_gsm = mode_clean in ("GSM", "GSM_ONLY", "FULL")
    emergency_phone = os.environ.get("EMERGENCY_PHONE", "+91XXXXXXXXXX")

    banner_mode = {
        "GPS_ONLY": "CLI VERSION 2: GPS ONLY (NO GSM)",
        "GSM_ONLY": "CLI VERSION 1: GSM ONLY (NO GPS)",
        "FULL": "CLI VERSION 3: BOTH GPS & GSM ACTIVE",
    }.get(mode_clean, f"CLI: {mode_clean}")

    print("\n" + "=" * 65)
    print(f"  🛰️ SMART VEHICLE BLACK BOX — {banner_mode}")
    print(f"  • GPS Sensor : {'ACTIVE (NEO-6M on UART @ 9600 baud)' if enable_gps else 'DISABLED'}")
    print(f"  • GSM Alerts : {'ACTIVE (SIM800L SMS alert sender)' if enable_gsm else 'DISABLED'}")
    print(f"  • Emergency  : {emergency_phone}")
    print("=" * 65 + "\n")

    # Initialize modules
    buffer = CircularBuffer(max_seconds=10, sample_rate_hz=10)
    csv_logger = CSVLogger("continuous_log.csv")
    sensors = SensorInterface(enable_gps=enable_gps)
    alerts = AlertSystem(phone_number=emergency_phone, enable_gsm=enable_gsm)
    crash_detector = CrashDetector()

    crash_handled = False

    try:
        while True:
            # 1. Read all sensors
            reading = sensors.read_all()

            # 2. Log to continuous CSV and store in circular buffer
            csv_logger.log_reading(reading)
            buffer.add_reading(reading)

            # 3. Check for routine safety violations (Alcohol)
            if reading.get("alcohol_detected"):
                alerts.trigger_local_alarm("Driver Alcohol Detected!")

            # 4. Check for Crash Event
            if not crash_handled and crash_detector.evaluate(reading):
                print("\n!!! EXECUTING EMERGENCY PROTOCOL !!!")

                # Dump the last 10 seconds of data (JSON format)
                dump_file = buffer.dump_to_file("crash_log.json")

                # Trigger local LED alarm and Send SOS SMS
                alerts.trigger_local_alarm("CRASH!")
                if enable_gsm:
                    alerts.send_emergency_sms(location_data=reading.get("gps"))

                crash_handled = True
                print("Emergency protocols completed. Continuing to log...\n")

            # Sleep to maintain 10Hz loop
            time.sleep(LOOP_DELAY_SEC)

    except KeyboardInterrupt:
        print("\nShutting down Black Box CLI...")
    finally:
        sensors.cleanup()


def main():
    parser = argparse.ArgumentParser(description="Vehicle Black Box Headless CLI")
    parser.add_argument(
        "--mode",
        choices=["gps", "gsm", "full"],
        default=None,
        help="Operational mode: 'gps' (default), 'gsm', or 'full'",
    )
    args, _ = parser.parse_known_args()
    mode_str = f"{args.mode.upper()}_ONLY" if args.mode in ("gps", "gsm") else (args.mode.upper() if args.mode else "GPS_ONLY")
    run_cli(mode=mode_str)


if __name__ == "__main__":
    main()
