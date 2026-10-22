#!/usr/bin/env python3
"""
test_hall.py
Comprehensive Diagnostic & Calibration Tool for Hall Effect Sensor on GPIO 22.

This script tests:
1. Raw physical GPIO 22 state (HIGH / LOW) in real-time.
2. Edge transitions when magnet approaches and leaves.
3. Pulse counting, live RPM, and speed conversion.
4. Troubleshoots stuck 0 RPM (Magnet polarity, wiring, potentiometer calibration).
"""

import time
import sys
import os

try:
    import RPi.GPIO as GPIO
    HARDWARE = True
except Exception as e:
    print(f"RPi.GPIO not available ({e}). Running in TEST mode.")
    HARDWARE = False

HALL_PIN = 22  # Physical Pin 15
PULSES_PER_REV = 1
WHEEL_CIRCUMFERENCE_M = 1.85  # ~59cm wheel diameter


def main():
    print("=" * 70)
    print(" ⚡ HALL EFFECT SENSOR DIAGNOSTIC & CALIBRATION (GPIO 22 / PIN 15)")
    print("=" * 70)
    print("WIRING VERIFICATION:")
    print("  • VCC  -> Pin 1 (3.3V) or Pin 2 (5V)")
    print("  • GND  -> Pin 6, 9, 14, 20, or 25 (GND)")
    print("  • DO   -> Pin 15 (BCM GPIO 22)  [Use DO, NOT AO!]")
    print("=" * 70)
    print("\nHOW TO USE THIS DIAGNOSTIC:")
    print("1. Watch the 'RAW PIN' value below (should be 1 or 0).")
    print("2. Wave a magnet directly across the front face of the Hall sensor:")
    print("   -> If RAW PIN flips (e.g. 1 -> 0): Sensor is WORKING!")
    print("   -> If RAW PIN NEVER CHANGES from 1:")
    print("      ⚠️  FLIP THE MAGNET 180°! Hall sensors only detect the SOUTH pole.")
    print("   -> If RAW PIN NEVER CHANGES and you have a 4-pin module with a blue box:")
    print("      ⚠️  Turn the tiny brass screw on the potentiometer until the LED toggles.")
    print("=" * 70)
    print("Press Ctrl + C to exit.\n")

    pulse_count = 0
    total_revolutions = 0

    if HARDWARE:
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.remove_event_detect(HALL_PIN)
        except Exception:
            pass

        # Use pull-up (standard for open-collector Hall sensors like A3144/KY-003)
        GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def _pulse_cb(channel):
            nonlocal pulse_count, total_revolutions
            pulse_count += 1
            total_revolutions += 1

        try:
            GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=_pulse_cb, bouncetime=10)
            print("✅ Interrupt edge detection registered successfully on GPIO 22.")
        except Exception as e:
            print(f"⚠️  Interrupt warning ({e}), falling back to direct pin sampling.")
    else:
        print("ℹ️  Running in mock simulation mode.")

    last_calc_time = time.time()
    last_pin_state = None
    transitions_seen = 0
    start_time = time.time()

    try:
        while True:
            time.sleep(0.02)  # 50 Hz sampling loop for high responsiveness
            now = time.time()

            if HARDWARE:
                raw_pin = GPIO.input(HALL_PIN)
            else:
                raw_pin = 1

            # Detect state transition via polling as fallback/confirmation
            if last_pin_state is not None and raw_pin != last_pin_state:
                transitions_seen += 1
                if raw_pin == 0:  # Active-low trigger
                    # If callback didn't catch it, fallback increments:
                    if pulse_count == 0:
                        pulse_count += 1
                        total_revolutions += 1

            last_pin_state = raw_pin

            # Every 1.0 second, compute and display RPM & Speed
            dt = now - last_calc_time
            if dt >= 1.0:
                pulses = pulse_count
                pulse_count = 0
                last_calc_time = now

                if pulses > 0:
                    revs = pulses / PULSES_PER_REV
                    rpm = round((revs / dt) * 60.0)
                    speed_ms = (revs * WHEEL_CIRCUMFERENCE_M) / dt
                    speed_kmh = round(speed_ms * 3.6, 1)
                    motion_tag = "⚡ SPINNING"
                else:
                    rpm = 0
                    speed_kmh = 0.0
                    motion_tag = "⏹️  STATIONARY"

                pin_desc = "HIGH (1) [No Mag]" if raw_pin == 1 else "LOW (0) [🧲 MAGNET!]"

                sys.stdout.write(
                    f"\r[{motion_tag}] Pin 22: {pin_desc:<20} | Pulses: {pulses:2d}/s | RPM: {rpm:4d} | Speed: {speed_kmh:5.1f} km/h | Total Revs: {total_revolutions:3d} "
                )
                sys.stdout.flush()

                # Periodic diagnostic tips if stationary for > 5 seconds
                elapsed = int(now - start_time)
                if total_revolutions == 0 and elapsed > 0 and elapsed % 8 == 0:
                    print(f"\n   [DIAGNOSTIC TIP @ {elapsed}s]")
                    if raw_pin == 1:
                        print("   👉 Pin is reading constant HIGH (1).")
                        print("      1. Flip your magnet 180° (use the South pole face).")
                        print("      2. Bring the magnet within 2mm to 4mm of the sensor.")
                        print("      3. If 4-pin module: turn the blue potentiometer screw clockwise.")
                    else:
                        print("   👉 Pin is reading constant LOW (0).")
                        print("      1. Check if DO wire is shorted to Ground.")
                        print("      2. If 4-pin module: turn the blue potentiometer counter-clockwise until LED goes off.")
                    print("-" * 70)

    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    finally:
        if HARDWARE:
            try:
                GPIO.cleanup(HALL_PIN)
            except Exception:
                pass
            print("GPIO cleaned up successfully.")


if __name__ == "__main__":
    main()
