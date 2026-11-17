#!/usr/bin/env python3
"""
scripts/bt_car.py — Raspberry Pi Bluetooth Controlled Car Module
Receives commands ('F', 'B', 'L', 'R', 'S', '0'-'9', 'q') from a mobile phone via Bluetooth RFCOMM.
Compatible with standard apps:
  - "Arduino Bluetooth RC Car"
  - "Bluetooth RC Controller"
  - "Serial Bluetooth Terminal"

Wiring (L298N to Raspberry Pi 4B):
  ENA -> GPIO 12 (Pin 32) [PWM Left Speed]
  IN1 -> GPIO 23 (Pin 16) [Left Motor Forward]
  IN2 -> GPIO 24 (Pin 18) [Left Motor Reverse]
  IN3 -> GPIO 27 (Pin 13) [Right Motor Forward - conflict-free with Hall Sensor on GPIO 22]
  IN4 -> GPIO 25 (Pin 22) [Right Motor Reverse]
  ENB -> GPIO 13 (Pin 33) [PWM Right Speed]
  GND -> Common Ground with Pi & Battery Pack

Usage:
  python3 scripts/bt_car.py          # Run Bluetooth RFCOMM server
  python3 scripts/bt_car.py --test   # Run automated motor diagnostic self-test
  python3 scripts/bt_car.py --cli    # Interactive keyboard control (W, A, S, D, Space)
"""

import sys
import time
import os
import argparse

try:
    import RPi.GPIO as GPIO
    HARDWARE = True
except (ImportError, RuntimeError) as err:
    print(f"[WARN] RPi.GPIO not available ({err}). Running in SIMULATION/MOCK mode.")
    GPIO = None
    HARDWARE = False

# ── Pin Configuration (BCM numbering) ──────────────────────────
# Carefully mapped to avoid conflicts with I2C (GPIO 2,3), UART (GPIO 14,15),
# Status LED (GPIO 17), SW-420 Vibration (GPIO 18), and Hall Effect (GPIO 22).
ENA = 12  # Left motor PWM speed (Physical Pin 32)
IN1 = 23  # Left motor Forward   (Physical Pin 16)
IN2 = 24  # Left motor Reverse   (Physical Pin 18)
IN3 = 27  # Right motor Forward  (Physical Pin 13)
IN4 = 25  # Right motor Reverse  (Physical Pin 22)
ENB = 13  # Right motor PWM speed(Physical Pin 33)

pwm_a = None
pwm_b = None
current_speed = 80  # Default speed percentage (0-100)


def setup_gpio():
    """Initializes motor GPIO pins and PWM frequency."""
    global pwm_a, pwm_b
    if not HARDWARE or not GPIO:
        print("[MOCK] GPIO initialized in software simulation mode.")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for pin in (ENA, IN1, IN2, IN3, IN4, ENB):
        GPIO.setup(pin, GPIO.OUT)

    # 100 Hz PWM frequency for smooth DC motor speed control
    pwm_a = GPIO.PWM(ENA, 100)
    pwm_b = GPIO.PWM(ENB, 100)
    pwm_a.start(current_speed)
    pwm_b.start(current_speed)
    stop_car()
    print("[INFO] Hardware GPIO and PWM successfully initialized.")


# ── Motor Driving Primitives ───────────────────────────────────
def set_speed(speed_percent: int):
    """Sets motor speed from 0% to 100% duty cycle."""
    global current_speed
    current_speed = max(0, min(100, int(speed_percent)))
    if HARDWARE and GPIO and pwm_a and pwm_b:
        pwm_a.ChangeDutyCycle(current_speed)
        pwm_b.ChangeDutyCycle(current_speed)
    print(f"[MOTOR] Speed adjusted to {current_speed}%")


def forward():
    """Drive all wheels forward."""
    print(f"[MOTOR] FORWARD ({current_speed}%)")
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)


def backward():
    """Drive all wheels backward."""
    print(f"[MOTOR] BACKWARD ({current_speed}%)")
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)


def turn_left():
    """Pivot turn left (Left wheels reverse, Right wheels forward)."""
    print(f"[MOTOR] TURN LEFT ({current_speed}%)")
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)


def turn_right():
    """Pivot turn right (Left wheels forward, Right wheels reverse)."""
    print(f"[MOTOR] TURN RIGHT ({current_speed}%)")
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)


def stop_car():
    """Immediately stop all motor outputs."""
    print("[MOTOR] STOP (Neutral)")
    if HARDWARE and GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)


def cleanup():
    """Stops motors, stops PWM, and resets GPIO state."""
    stop_car()
    if HARDWARE and GPIO and pwm_a and pwm_b:
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()
    print("[INFO] Motor GPIO cleanup complete.")


# ── Command Processing ─────────────────────────────────────────
def process_command(cmd: str):
    """Parses standard RC car protocol commands."""
    if not cmd:
        return

    for char in cmd:
        if char == "F":
            forward()
        elif char == "B":
            backward()
        elif char == "L":
            turn_left()
        elif char == "R":
            turn_right()
        elif char == "S":
            stop_car()
        elif char in "0123456789":
            # Map '0'-'9' to 0% - 90% (or '9' -> 90%)
            speed_val = int(char) * 10
            set_speed(speed_val)
        elif char == "q":
            set_speed(100)  # Maximum 100% speed


# ── Self-Test Diagnostic Routine ──────────────────────────────
def run_self_test():
    """Runs a sequenced motor test to verify wiring direction and PWM."""
    print("=" * 60)
    print("  Raspberry Pi Bluetooth Car — Automated Motor Self-Test")
    print("=" * 60)
    setup_gpio()

    try:
        set_speed(70)
        print("\n[TEST 1/5] Testing FORWARD (2 seconds)...")
        forward()
        time.sleep(2)

        print("\n[TEST 2/5] Testing BACKWARD (2 seconds)...")
        backward()
        time.sleep(2)

        print("\n[TEST 3/5] Testing PIVOT LEFT (1.5 seconds)...")
        turn_left()
        time.sleep(1.5)

        print("\n[TEST 4/5] Testing PIVOT RIGHT (1.5 seconds)...")
        turn_right()
        time.sleep(1.5)

        print("\n[TEST 5/5] Testing SPEED PWM RAMP (50% -> 80% -> 100%)...")
        forward()
        for spd in (50, 80, 100):
            set_speed(spd)
            time.sleep(1)

        print("\n[TEST DONE] Stopping vehicle.")
        stop_car()
        print("Self-test completed successfully!")

    except KeyboardInterrupt:
        print("\nSelf-test interrupted by user.")
    finally:
        cleanup()


# ── Interactive Keyboard CLI Mode ─────────────────────────────
def run_cli_mode():
    """Allows manual control from keyboard for testing without Bluetooth."""
    import termios
    import tty

    print("=" * 60)
    print("  Raspberry Pi Bluetooth Car — Interactive Keyboard CLI")
    print("=" * 60)
    print("  Controls:")
    print("    W : Forward        S : Backward")
    print("    A : Turn Left      D : Turn Right")
    print("    Space / X : Stop")
    print("    1-9 / Q   : Set Speed (10% - 100%)")
    print("    Ctrl + C  : Exit")
    print("=" * 60)
    setup_gpio()

    def get_char():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    try:
        while True:
            char = get_char().upper()
            if char in ("\x03", "\x1a"):  # Ctrl+C or Ctrl+Z
                break
            if char == "W":
                forward()
            elif char == "S":
                backward()
            elif char == "A":
                turn_left()
            elif char == "D":
                turn_right()
            elif char in (" ", "X"):
                stop_car()
            elif char in "0123456789Q":
                process_command(char)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


# ── Bluetooth RFCOMM Server ────────────────────────────────────
def run_bluetooth_server(port: int = 1):
    """Listens for incoming Bluetooth RFCOMM serial connections from mobile."""
    import socket

    setup_gpio()

    try:
        server_sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        server_sock.bind(("", port))
        server_sock.listen(1)
    except Exception as exc:
        print(f"[ERROR] Could not start Bluetooth RFCOMM server: {exc}")
        print("Ensure Bluetooth is enabled and BlueZ is active:")
        print("  sudo systemctl start bluetooth")
        print("  sudo sdptool add SP")
        cleanup()
        sys.exit(1)

    print("=" * 65)
    print("  🚗 Raspberry Pi Bluetooth Car Server Active")
    print(f"  Listening on RFCOMM Channel {port}...")
    print("=" * 65)
    print("  Mobile Setup Instructions:")
    print("  1. Pair your phone with Raspberry Pi via Bluetooth settings.")
    print("  2. Open 'Arduino Bluetooth RC Car' or 'Serial Bluetooth Terminal'.")
    print("  3. Connect to Raspberry Pi.")
    print("  4. Send commands: F (Forward), B (Back), L (Left), R (Right), S (Stop).")
    print("=" * 65)

    try:
        while True:
            print("\n[BT] Waiting for mobile device connection...")
            client_sock, client_info = server_sock.accept()
            print(f"[BT] Connection established with: {client_info}")

            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    decoded = data.decode("utf-8", errors="ignore")
                    process_command(decoded)
            except (ConnectionResetError, BrokenPipeError):
                print("[BT] Mobile client disconnected.")
            except Exception as e:
                print(f"[BT] Client error: {e}")
            finally:
                stop_car()
                client_sock.close()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Terminating Bluetooth car server...")
    finally:
        server_sock.close()
        cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Raspberry Pi Bluetooth RC Car Controller")
    parser.add_argument("--test", action="store_true", help="Run automated motor self-test routine")
    parser.add_argument("--cli", action="store_true", help="Control motors interactively via keyboard")
    parser.add_argument("--port", type=int, default=1, help="Bluetooth RFCOMM channel port (default: 1)")
    args = parser.parse_args()

    if args.test:
        run_self_test()
    elif args.cli:
        run_cli_mode()
    else:
        run_bluetooth_server(args.port)
