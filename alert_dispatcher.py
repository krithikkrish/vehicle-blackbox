"""
alert_dispatcher.py
Sends emergency SMS via SIM800L (on /dev/ttyUSB0) using AT commands.
"""

import serial
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
GSM_PORT       = "/dev/ttyUSB0"
GSM_BAUDRATE   = 9600
EMERGENCY_NUM  = "+91XXXXXXXXXX"       # ← Replace with real number
# ─────────────────────────────────────────────────────────────────────────────


def _send_at(ser: serial.Serial, cmd: str, delay: float = 0.5) -> str:
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    return ser.read(ser.in_waiting).decode(errors="ignore")


def send_crash_sms(lat: float, lon: float, speed_kmh: float) -> bool:
    """
    Compose and send a crash-alert SMS with GPS coordinates.
    Returns True on success, False on failure.
    """
    try:
        with serial.Serial(GSM_PORT, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")                         # Check module alive
            _send_at(gsm, "AT+CMGF=1")                  # Text mode
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)

            ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = (
                f"🚨 CRASH ALERT!\n"
                f"Time   : {ts}\n"
                f"Speed  : {speed_kmh:.1f} km/h\n"
                f"Loc    : {lat:.6f}, {lon:.6f}\n"
                f"Maps   : https://maps.google.com/?q={lat},{lon}"
            )
            gsm.write(msg.encode())
            gsm.write(bytes([26]))                       # Ctrl+Z  → send
            time.sleep(3)
            logger.info("Crash SMS sent to %s", EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error: %s", exc)
        return False


def send_alcohol_sms(lat: float, lon: float, voltage: float) -> bool:
    """Send an alcohol-detection warning SMS."""
    try:
        with serial.Serial(GSM_PORT, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")
            _send_at(gsm, "AT+CMGF=1")
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)

            ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = (
                f"⚠️  ALCOHOL DETECTED\n"
                f"Time   : {ts}\n"
                f"Sensor : {voltage:.3f} V\n"
                f"Loc    : {lat:.6f}, {lon:.6f}\n"
                f"Maps   : https://maps.google.com/?q={lat},{lon}"
            )
            gsm.write(msg.encode())
            gsm.write(bytes([26]))
            time.sleep(3)
            logger.info("Alcohol SMS sent to %s", EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error: %s", exc)
        return False
