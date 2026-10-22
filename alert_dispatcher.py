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
GSM_PORTS      = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyAMA0"]
GSM_BAUDRATE   = 9600
EMERGENCY_NUM  = os.environ.get("EMERGENCY_PHONE", os.environ.get("EMERGENCY_NUM", "+91XXXXXXXXXX"))       # ← Replace with real number or export EMERGENCY_PHONE
GSM_ENABLED    = True
# ─────────────────────────────────────────────────────────────────────────────


def set_gsm_enabled(enabled: bool):
    """Enable or disable GSM transmission."""
    global GSM_ENABLED
    GSM_ENABLED = bool(enabled)
    logger.info("GSM alert dispatch set to: %s", "ENABLED" if GSM_ENABLED else "DISABLED")


def is_gsm_enabled() -> bool:
    """Return whether GSM transmission is currently enabled."""
    return GSM_ENABLED


def _get_active_gsm_port() -> str:
    """Return the first existing physical GSM serial port or None."""
    if not GSM_ENABLED:
        return None
    for port in GSM_PORTS:
        if os.path.exists(port):
            return port
    return None


def _is_gsm_available() -> bool:
    """Check if GSM is enabled and physical serial port is detected."""
    return _get_active_gsm_port() is not None


def _format_location(lat: float, lon: float) -> tuple:
    """Return readable coordinate string and Google Maps link."""
    if lat == 0.0 and lon == 0.0:
        return "Location Unavailable (GPS Disabled / No Fix)", "N/A"
    return f"{lat:.6f}, {lon:.6f}", f"https://maps.google.com/?q={lat},{lon}"


def _send_at(ser: serial.Serial, cmd: str, delay: float = 0.5) -> str:
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    return ser.read(ser.in_waiting).decode(errors="ignore")


def send_crash_sms(lat: float, lon: float, speed_kmh: float) -> bool:
    """
    Compose and send a crash-alert SMS with GPS coordinates.
    If GSM is disabled, returns immediately.
    If GSM is enabled but hardware is missing, logs simulated transmission.
    """
    if not GSM_ENABLED:
        logger.info("ℹ️ GSM alert skipped — GSM is DISABLED in this configuration (GPS-only mode).")
        return False

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    loc_str, maps_str = _format_location(lat, lon)
    msg = (
        f"🚨 CRASH ALERT!\n"
        f"Time   : {ts}\n"
        f"Speed  : {speed_kmh:.1f} km/h\n"
        f"Loc    : {loc_str}\n"
        f"Maps   : {maps_str}"
    )

    port = _get_active_gsm_port()
    if not port:
        logger.warning("=" * 60)
        logger.warning("  [GSM ACTIVE — SIMULATION MODE (No Hardware Connected)]")
        logger.warning("  SMS Destination: %s", EMERGENCY_NUM)
        logger.warning("  Message Body:\n%s", msg)
        logger.warning("=" * 60)
        return True

    try:
        with serial.Serial(port, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")                         # Check module alive
            _send_at(gsm, "AT+CMGF=1")                  # Text mode
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)
            gsm.write(msg.encode())
            gsm.write(bytes([26]))                       # Ctrl+Z → send
            time.sleep(3)
            logger.info("Crash SMS sent via GSM (%s) to %s", port, EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error on %s (%s). Falling back to simulated alert.", port, exc)
        logger.warning("Simulated Crash SMS:\n%s", msg)
        return False


def send_alcohol_sms(lat: float, lon: float, voltage: float) -> bool:
    """
    Send an alcohol-detection warning SMS.
    If GSM is disabled, returns immediately.
    If GSM is enabled but hardware is missing, logs simulated transmission.
    """
    if not GSM_ENABLED:
        logger.info("ℹ️ GSM alert skipped — GSM is DISABLED in this configuration (GPS-only mode).")
        return False

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    loc_str, maps_str = _format_location(lat, lon)
    msg = (
        f"⚠️  ALCOHOL DETECTED\n"
        f"Time   : {ts}\n"
        f"Sensor : {voltage:.3f} V\n"
        f"Loc    : {loc_str}\n"
        f"Maps   : {maps_str}"
    )

    port = _get_active_gsm_port()
    if not port:
        logger.warning("=" * 60)
        logger.warning("  [GSM ACTIVE — SIMULATION MODE (No Hardware Connected)]")
        logger.warning("  SMS Destination: %s", EMERGENCY_NUM)
        logger.warning("  Message Body:\n%s", msg)
        logger.warning("=" * 60)
        return True

    try:
        with serial.Serial(port, GSM_BAUDRATE, timeout=2) as gsm:
            _send_at(gsm, "AT")
            _send_at(gsm, "AT+CMGF=1")
            _send_at(gsm, f'AT+CMGS="{EMERGENCY_NUM}"', delay=1)
            gsm.write(msg.encode())
            gsm.write(bytes([26]))
            time.sleep(3)
            logger.info("Alcohol SMS sent via GSM (%s) to %s", port, EMERGENCY_NUM)
            return True

    except serial.SerialException as exc:
        logger.error("GSM serial error on %s (%s). Falling back to simulated alert.", port, exc)
        logger.warning("Simulated Alcohol SMS:\n%s", msg)
        return False
