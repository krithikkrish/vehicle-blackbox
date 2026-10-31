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
        GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    consecutive_hits = 0
    REQUIRED_HITS = 3
    raw_events = 0
    filtered_events = 0
    was_triggered = False

    try:
        while True:
            if HARDWARE:
                raw_val = GPIO.input(VIBRATION_PIN)
            else:
                raw_val = 0

            if raw_val == 1:
                consecutive_hits += 1
                raw_events += 1
            else:
                consecutive_hits = max(0, consecutive_hits - 1)

            is_impact = (consecutive_hits >= REQUIRED_HITS)
            if is_impact and not was_triggered:
                filtered_events += 1
            was_triggered = is_impact

            if is_impact:
                status = "💥 IMPACT DETECTED (Sustained >= 60ms)"
            elif raw_val == 1:
                status = "⚠️  MINOR JOLT (Filtered out / too brief)"
            else:
                status = "🟢 Resting / Stable"

            sys.stdout.write(
                f"\r[{time.strftime('%H:%M:%S')}] Pin 18: {raw_val} | Hits: {consecutive_hits:2d}/{REQUIRED_HITS} | "
                f"Status: {status:<40} | Impacts: {filtered_events} (Raw Spikes: {raw_events})"
            )
            sys.stdout.flush()

            time.sleep(0.02)  # 50 Hz matching sensor_manager.py

    except KeyboardInterrupt:
        print("\n\nExiting vibration test.")
    finally:
        if HARDWARE:
            GPIO.cleanup()


if __name__ == "__main__":
    main()
