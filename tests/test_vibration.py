#!/usr/bin/env python3
"""
test_vibration.py
Diagnostic tool for SW-420 vibration sensor on GPIO 18 (Pin 12).
Displays raw GPIO state (0 or 1) in real-time to help calibrate
the potentiometer and determine if the module is Active-HIGH or Active-LOW.
"""

import time
import sys

try:
    import RPi.GPIO as GPIO
    HARDWARE = True
except Exception as e:
    print(f"RPi.GPIO not available ({e}). Running in MOCK mode.")
    HARDWARE = False
    import random

VIBRATION_PIN = 18  # Pin 12


def main():
    print("=" * 60)
    print(" SW-420 Vibration Sensor Diagnostic & Calibration")
    print(f" GPIO Pin: BCM {VIBRATION_PIN} (Physical Pin 12)")
    print("=" * 60)
    print("CALIBRATION INSTRUCTIONS:")
    print("1. Keep the sensor completely still on the table.")
    print("2. Look at the raw pin value below (0 or 1).")
    print("3. Tap the sensor/table firmly.")
    print("   - If resting is 0 and tapping gives 1 -> Sensor is Active-HIGH")
    print("   - If resting is 1 and tapping gives 0 -> Sensor is Active-LOW")
    print("4. If the value NEVER changes when tapped, turn the small brass screw")
    print("   on the blue potentiometer with a screwdriver until it becomes sensitive.")
    print("=" * 60)
    print("Press Ctrl + C to exit.\n")

    if HARDWARE:
        GPIO.setmode(GPIO.BCM)
        # Try with no pull to see raw module output
        GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

    last_val = None
    change_count = 0

    try:
        while True:
            if HARDWARE:
                raw_val = GPIO.input(VIBRATION_PIN)
            else:
                raw_val = 1  # Mock fixed high to simulate user's condition

            # Detect state flip
            if last_val is not None and raw_val != last_val:
                change_count += 1
                status = "💥 STATE CHANGED (VIBRATION DETECTED!)"
            else:
                status = "Still / Resting"

            sys.stdout.write(f"\r[{time.strftime('%H:%M:%S')}] Raw GPIO 18 = {raw_val} | Status: {status:<40} (Events: {change_count})")
            sys.stdout.flush()

            last_val = raw_val
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\nExiting vibration test.")
    finally:
        if HARDWARE:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
