"""
alert_dispatcher.py
Sends emergency SMS via SIM800L / GSM module using AT commands.
If no physical GSM module is connected, automatically switches to
Simulation Mode so all crash and alert workflows can be tested seamlessly.
"""

import os
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


def _is_gsm_available() -> bool:
    """Check if the physical GSM serial port exists on the system."""
    return os.path.exists(GSM_PORT)


def _send_at(ser: serial.Serial, cmd: str, delay: float = 0.5) -> str:
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    return ser.read(ser.in_waiting).decode(errors="ignore")


def send_crash_sms(lat: float, lon: float, speed_kmh: float) -> bool:
    """
    Compose and send a crash-alert SMS with GPS coordinates.
    If no GSM module is connected, logs a simulated SMS transmission.
    """
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"🚨 CRASH ALERT!\n"
        f"Time   : {ts}\n"
        f"Speed  : {speed_kmh:.1f} km/h\n"
        f"Loc    : {lat:.6f}, {lon:.6f}\n"
        f"Maps   : https://maps.google.com/?q={lat},{lon}"
    )

    if not _is_gsm_available():
        logger.warning("=" * 60)
        logger.warning("  [GSM SIMULATION MODE — NO HARDWARE DETECTED]")
        logger.warning("  SMS would be sent to: %s", EMERGENCY_NUM)
        logger.warning("  Message Body:\n%s", msg)
        logger.warning("=" * 60)
        return True

    try:
        with serial.Serial(GSM_PORT, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")                         # Check module alive
            _send_at(gsm, "AT+CMGF=1")                  # Text mode
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)
            gsm.write(msg.encode())
            gsm.write(bytes([26]))                       # Ctrl+Z → send
            time.sleep(3)
            logger.info("Crash SMS sent via GSM to %s", EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error (%s). Falling back to simulated alert.", exc)
        logger.warning("Simulated Crash SMS:\n%s", msg)
        return False


def send_alcohol_sms(lat: float, lon: float, voltage: float) -> bool:
    """
    Send an alcohol-detection warning SMS.
    If no GSM module is connected, logs a simulated SMS transmission.
    """
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"⚠️  ALCOHOL DETECTED\n"
        f"Time   : {ts}\n"
        f"Sensor : {voltage:.3f} V\n"
        f"Loc    : {lat:.6f}, {lon:.6f}\n"
        f"Maps   : https://maps.google.com/?q={lat},{lon}"
    )

    if not _is_gsm_available():
        logger.warning("=" * 60)
        logger.warning("  [GSM SIMULATION MODE — NO HARDWARE DETECTED]")
        logger.warning("  SMS would be sent to: %s", EMERGENCY_NUM)
        logger.warning("  Message Body:\n%s", msg)
        logger.warning("=" * 60)
        return True

    try:
        with serial.Serial(GSM_PORT, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")
            _send_at(gsm, "AT+CMGF=1")
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)
            gsm.write(msg.encode())
            gsm.write(bytes([26]))
            time.sleep(3)
            logger.info("Alcohol SMS sent via GSM to %s", EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error (%s). Falling back to simulated alert.", exc)
        logger.warning("Simulated Alcohol SMS:\n%s", msg)
        return False
