#!/usr/bin/env python3
"""
src/main.py — Vehicle Black Box CLI (Version 1: GSM ONLY, No GPS)
-----------------------------------------------------------------
CLI entrypoint:
- GSM Alerts  : ENABLED (SMS on crash/alcohol via SIM800L or simulation)
- GPS Module  : DISABLED (UART port not initialized)
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
EMERGENCY_PHONE = "+91XXXXXXXXXX"  # Replace with real number
LOOP_DELAY_SEC = 0.1              # 10Hz sampling


def main():
    print("\n" + "=" * 65)
    print("  🚗 SMART VEHICLE BLACK BOX — CLI VERSION 1: GSM ONLY (NO GPS)")
    print("  • GSM Alerts : ACTIVE (SIM800L SMS on crash)")
    print("  • GPS Sensor : DISABLED (UART port free)")
    print("=" * 65 + "\n")

    # Initialize modules in GSM-only mode (enable_gps=False, enable_gsm=True)
    buffer = CircularBuffer(max_seconds=10, sample_rate_hz=10)
    csv_logger = CSVLogger("continuous_log.csv")
    sensors = SensorInterface(enable_gps=False)
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

                # Trigger local LED alarm and Send SOS SMS
                alerts.trigger_local_alarm("CRASH!")
                alerts.send_emergency_sms(location_data=reading.get("gps", {}).get("location", "N/A (GPS Disabled)"))

                crash_handled = True  # Prevent sending duplicate SMS messages
                print("Emergency protocols completed. Continuing to log...\n")

            # Sleep to maintain 10Hz loop
            time.sleep(LOOP_DELAY_SEC)

    except KeyboardInterrupt:
        print("\nShutting down Black Box CLI...")
    finally:
        sensors.cleanup()


if __name__ == "__main__":
    main()
