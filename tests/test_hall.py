#!/usr/bin/env python3
"""
test_hall.py
Diagnostic tool for Hall Effect speed sensor on GPIO 22 (Physical Pin 15).
Calculates real-time Pulses, Wheel RPM, and Converted Speed (km/h).
Takes ONLY physical pulse inputs: 0 pulses = 0 RPM = 0.0 km/h.
"""

import time
import sys

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
    print("=" * 65)
    print(" ⚡ Hall Effect Sensor Diagnostic & Calibration Tool")
    print(f" GPIO Pin: BCM {HALL_PIN} (Physical Pin 15)")
    print(f" Wheel Circumference: {WHEEL_CIRCUMFERENCE_M} m | Pulses/Rev: {PULSES_PER_REV}")
    print("=" * 65)
    print("WIRING CHECK:")
    print("  • VCC  -> 3.3V (Pin 1) or 5V (Pin 2)")
    print("  • GND  -> Raspberry Pi Ground (Pin 6, 9, 14, etc.)")
    print("  • DO   -> GPIO 22 (Physical Pin 15)")
    print("\nTEST PROCEDURE:")
    print("1. Keep wheel / magnet completely still.")
    print("   -> Pulses should be 0, RPM should be 0, Speed should be 0.0 km/h.")
    print("2. Wave a magnet past the sensor or spin the wheel.")
    print("   -> LED on the Hall module will blink.")
    print("   -> Live pulses, RPM, and km/h will update immediately.")
    print("=" * 65)
    print("Press Ctrl + C to exit.\n")

    pulse_count = 0

    def _pulse_callback(channel):
        nonlocal pulse_count
        pulse_count += 1

    if HARDWARE:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=_pulse_callback, bouncetime=15)
        print("GPIO 22 initialized with PUD_UP. Listening for falling edge pulses...\n")
    else:
        print("Running in simulation mode without Pi GPIO hardware.\n")

    last_tick = time.time()
    total_revolutions = 0

    try:
        while True:
            time.sleep(1.0)
            now = time.time()
            dt = max(0.1, now - last_tick)
            last_tick = now

            pulses = pulse_count
            pulse_count = 0
            total_revolutions += pulses

            if pulses > 0:
                revs = pulses / PULSES_PER_REV
                rpm = round((revs / dt) * 60.0)
                speed_ms = (revs * WHEEL_CIRCUMFERENCE_M) / dt
                speed_kmh = round(speed_ms * 3.6, 1)
                status = "⚡ SPINNING"
            else:
                rpm = 0
                speed_kmh = 0.0
                status = "⏹️  STATIONARY"

            sys.stdout.write(
                f"\r[{status}] Pulses/sec: {pulses:2d} | RPM: {rpm:4d} | Speed: {speed_kmh:5.1f} km/h | Total Revs: {total_revolutions:4d} "
            )
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    finally:
        if HARDWARE:
            GPIO.cleanup(HALL_PIN)
            print("GPIO cleaned up successfully.")


if __name__ == "__main__":
    main()
