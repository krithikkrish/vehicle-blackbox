#!/usr/bin/env python3
"""
src/main_full.py — Vehicle Black Box CLI (Version 3: BOTH GPS & GSM ACTIVE)
--------------------------------------------------------------------------
CLI entrypoint:
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : ENABLED (SIM800L SMS on crash with live coordinates)
"""

import time
import os
import sys

# Ensure local imports work when running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from buffer import CircularBuffer, CSVLogger
from sensors import SensorInterface
from alerts import AlertSystem
from crash_logic import CrashDetector

# Configurations
EMERGENCY_PHONE = os.environ.get("EMERGENCY_PHONE", os.environ.get("EMERGENCY_NUM", "+91XXXXXXXXXX"))  # Replace with real number
LOOP_DELAY_SEC = 0.1  # 10Hz sampling


def main():
    print("\n" + "=" * 65)
    print("  🚨 SMART VEHICLE BLACK BOX — CLI VERSION 3: BOTH GPS & GSM ACTIVE")
    print("  • GPS Sensor : ACTIVE (NEO-6M on UART @ 9600 baud)")
    print("  • GSM Alerts : ACTIVE (SIM800L SMS alert sender)")
    print("=" * 65 + "\n")

    # Initialize modules in full mode (enable_gps=True, enable_gsm=True)
    buffer = CircularBuffer(max_seconds=10, sample_rate_hz=10)
    csv_logger = CSVLogger("continuous_log.csv")
    sensors = SensorInterface(enable_gps=True)
    alerts = AlertSystem(phone_number=EMERGENCY_PHONE, enable_gsm=True)
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

                # Trigger local LED alarm and Send SOS SMS with live GPS
                alerts.trigger_local_alarm("CRASH!")
                alerts.send_emergency_sms(location_data=reading.get("gps"))

                crash_handled = True
                print("Emergency protocols completed. Continuing to log...\n")

            # Sleep to maintain 10Hz loop
            time.sleep(LOOP_DELAY_SEC)

    except KeyboardInterrupt:
        print("\nShutting down Black Box CLI...")
    finally:
        sensors.cleanup()


if __name__ == "__main__":
    main()
