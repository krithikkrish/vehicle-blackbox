#!/usr/bin/env python3
"""
tests/test_motors.py
Diagnostic tool for L298N Motor Driver and DC Motors.
Tests left motor, right motor, direction control, and PWM speed ramps.

Pinout (BCM):
  - Left Motor PWM (ENA)  : GPIO 12 (Pin 32)
  - Left Motor Dir (IN1)  : GPIO 23 (Pin 16)
  - Left Motor Dir (IN2)  : GPIO 24 (Pin 18)
  - Right Motor Dir (IN3) : GPIO 27 (Pin 13)
  - Right Motor Dir (IN4) : GPIO 25 (Pin 22)
  - Right Motor PWM (ENB) : GPIO 13 (Pin 33)
"""

import sys
import time

try:
    import RPi.GPIO as GPIO
    HARDWARE = True
except (ImportError, RuntimeError) as e:
    print(f"RPi.GPIO not available ({e}). Running in MOCK mode.")
    HARDWARE = False
    GPIO = None

# Motor Pin Configuration (BCM)
ENA = 12  # Pin 32
IN1 = 23  # Pin 16
IN2 = 24  # Pin 18
IN3 = 27  # Pin 13
IN4 = 25  # Pin 22
ENB = 13  # Pin 33

pwm_a = None
pwm_b = None


def setup_pins():
    global pwm_a, pwm_b
    if not HARDWARE or not GPIO:
        print("[MOCK] Initialized motor pins in simulation mode.")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for pin in (ENA, IN1, IN2, IN3, IN4, ENB):
        GPIO.setup(pin, GPIO.OUT)

    pwm_a = GPIO.PWM(ENA, 100)
    pwm_b = GPIO.PWM(ENB, 100)
    pwm_a.start(0)
    pwm_b.start(0)
    stop()


def stop():
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        if pwm_a and pwm_b:
            pwm_a.ChangeDutyCycle(0)
            pwm_b.ChangeDutyCycle(0)


def left_motor(forward=True, speed=80):
    if HARDWARE and GPIO:
        pwm_a.ChangeDutyCycle(speed)
        GPIO.output(IN1, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW if forward else GPIO.HIGH)


def right_motor(forward=True, speed=80):
    if HARDWARE and GPIO:
        pwm_b.ChangeDutyCycle(speed)
        GPIO.output(IN3, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW if forward else GPIO.HIGH)


def cleanup():
    stop()
    if HARDWARE and GPIO:
        if pwm_a:
            pwm_a.stop()
        if pwm_b:
            pwm_b.stop()
        GPIO.cleanup()
    print("[INFO] Cleanup complete.")


def main():
    print("=" * 65)
    print(" 🚗 L298N Motor Driver Diagnostic & Verification Suite")
    print("=" * 65)
    print(f" Left Motor Pins  : ENA=GPIO {ENA} (Pin 32), IN1=GPIO {IN1}, IN2=GPIO {IN2}")
    print(f" Right Motor Pins : ENB=GPIO {ENB} (Pin 33), IN3=GPIO {IN3}, IN4=GPIO {IN4}")
    print("=" * 65)
    print(" SAFETY NOTICE:")
    print(" Elevate the vehicle so wheels spin freely in the air.")
    print(" Ensure Battery Pack GND is connected to Raspberry Pi GND.")
    print("=" * 65)
    input("Press ENTER to begin motor diagnostics (Ctrl+C to abort)...")

    setup_pins()

    try:
        # Step 1: Left Motor Forward
        print("\n[STEP 1/7] Testing LEFT MOTOR FORWARD (Speed: 70%, 2 sec)...")
        left_motor(forward=True, speed=70)
        time.sleep(2)
        stop()
        time.sleep(0.5)

        # Step 2: Left Motor Backward
        print("[STEP 2/7] Testing LEFT MOTOR BACKWARD (Speed: 70%, 2 sec)...")
        left_motor(forward=False, speed=70)
        time.sleep(2)
        stop()
        time.sleep(0.5)

        # Step 3: Right Motor Forward
        print("[STEP 3/7] Testing RIGHT MOTOR FORWARD (Speed: 70%, 2 sec)...")
        right_motor(forward=True, speed=70)
        time.sleep(2)
        stop()
        time.sleep(0.5)

        # Step 4: Right Motor Backward
        print("[STEP 4/7] Testing RIGHT MOTOR BACKWARD (Speed: 70%, 2 sec)...")
        right_motor(forward=False, speed=70)
        time.sleep(2)
        stop()
        time.sleep(0.5)

        # Step 5: Both Motors Forward
        print("[STEP 5/7] Testing DUAL MOTORS FORWARD (Speed: 75%, 2 sec)...")
        left_motor(forward=True, speed=75)
        right_motor(forward=True, speed=75)
        time.sleep(2)
        stop()
        time.sleep(0.5)

        # Step 6: PWM Speed Acceleration Ramp
        print("[STEP 6/7] Testing PWM SPEED RAMP (40% -> 70% -> 100%)...")
        for spd in [40, 70, 100]:
            print(f"  -> Ramping to {spd}% duty cycle...")
            left_motor(forward=True, speed=spd)
            right_motor(forward=True, speed=spd)
            time.sleep(1)
        stop()
        time.sleep(0.5)

        # Step 7: Steering Rotation Test
        print("[STEP 7/7] Testing ROTATIONAL STEERING...")
        print("  -> Pivot Turn Left (1.5 sec)...")
        left_motor(forward=False, speed=70)
        right_motor(forward=True, speed=70)
        time.sleep(1.5)
        stop()
        time.sleep(0.5)

        print("  -> Pivot Turn Right (1.5 sec)...")
        left_motor(forward=True, speed=70)
        right_motor(forward=False, speed=70)
        time.sleep(1.5)
        stop()

        print("\n" + "=" * 65)
        print(" ✅ ALL MOTOR DIAGNOSTIC CHECKS COMPLETED SUCCESSFULLY!")
        print("=" * 65)

    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
