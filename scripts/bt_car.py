#!/usr/bin/env python3
"""
bt_car.py — Raspberry Pi Bluetooth Controlled Car
Receives commands ('F', 'B', 'L', 'R', 'S', 0-9) from mobile via Bluetooth RFCOMM.
Compatible with standard apps:
  - "Arduino Bluetooth RC Car"
  - "Bluetooth RC Controller"
  - "Serial Bluetooth Terminal"
"""

import socket
import sys
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("[WARN] RPi.GPIO not found. Running in simulation mode.")
    GPIO = None

# ── Pin Configuration (BCM numbering) ──────────────────────────
# Safe pins that don't conflict with I2C (2,3) or UART (14,15)
ENA = 12  # Left motor PWM speed
IN1 = 23  # Left motor Forward
IN2 = 24  # Left motor Reverse
IN3 = 22  # Right motor Forward
IN4 = 25  # Right motor Reverse
ENB = 13  # Right motor PWM speed

pwm_a = None
pwm_b = None
current_speed = 80  # Default speed percentage (0-100)


def setup_gpio():
    global pwm_a, pwm_b
    if not GPIO:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for pin in (ENA, IN1, IN2, IN3, IN4, ENB):
        GPIO.setup(pin, GPIO.OUT)

    # 100 Hz PWM frequency for smooth motor control
    pwm_a = GPIO.PWM(ENA, 100)
    pwm_b = GPIO.PWM(ENB, 100)
    pwm_a.start(current_speed)
    pwm_b.start(current_speed)
    stop_car()
    print("[INFO] GPIO and PWM initialized.")


# ── Motor Driving Functions ────────────────────────────────────
def set_speed(speed_percent: int):
    global current_speed
    current_speed = max(0, min(100, speed_percent))
    if GPIO and pwm_a and pwm_b:
        pwm_a.ChangeDutyCycle(current_speed)
        pwm_b.ChangeDutyCycle(current_speed)
    print(f"[MOTOR] Speed set to {current_speed}%")


def forward():
    print("[MOTOR] FORWARD")
    if GPIO:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)


def backward():
    print("[MOTOR] BACKWARD")
    if GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)


def turn_left():
    print("[MOTOR] TURN LEFT")
    if GPIO:
        # Spin turn: Left wheels reverse, Right wheels forward
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)


def turn_right():
    print("[MOTOR] TURN RIGHT")
    if GPIO:
        # Spin turn: Left wheels forward, Right wheels reverse
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)


def stop_car():
    print("[MOTOR] STOP")
    if GPIO:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)


def cleanup():
    stop_car()
    if GPIO and pwm_a and pwm_b:
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()
    print("[INFO] GPIO cleaned up.")


# ── Command Processing ─────────────────────────────────────────
def process_command(cmd: str):
    if not cmd:
        return

    cmd = cmd.strip()
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
            # Map '0'-'9' to 0% - 100% speed
            speed_val = int(char) * 10
            set_speed(speed_val if speed_val > 0 else 0)
        elif char == "q":
            set_speed(100)


# ── Bluetooth RFCOMM Server ────────────────────────────────────
def run_bluetooth_server(port: int = 1):
    setup_gpio()

    server_sock = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    server_sock.bind(("", port))
    server_sock.listen(1)

    print("==================================================")
    print("  Raspberry Pi Bluetooth Car Server Started")
    print(f"  Listening on RFCOMM Channel {port}...")
    print("  Pair phone via bluetoothctl & connect from app.")
    print("==================================================")

    try:
        while True:
            print("\n[BT] Waiting for phone connection...")
            client_sock, client_info = server_sock.accept()
            print(f"[BT] Connected to mobile client: {client_info}")

            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    decoded = data.decode("utf-8", errors="ignore")
                    process_command(decoded)
            except (ConnectionResetError, BrokenPipeError):
                print("[BT] Mobile disconnected.")
            finally:
                stop_car()
                client_sock.close()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Exiting...")
    finally:
        server_sock.close()
        cleanup()


if __name__ == "__main__":
    port_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_bluetooth_server(port_num)
