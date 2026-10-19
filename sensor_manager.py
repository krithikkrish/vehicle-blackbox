"""
sensor_manager.py
One thread per sensor. Each thread reads its sensor, updates the
shared circular buffer, and sets the shared state dict.

Sensors:
  - NEO-6M GPS      → UART /dev/ttyAMA0
  - Hall Effect     → GPIO 17 (pulse counter)
  - MQ-3 Alcohol    → ADS1115 channel A0 (I2C)
  - SW-420 Vibration→ GPIO 27 (interrupt)
"""

import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Shared live state ────────────────────────────────────────────────────────
state = {
    "timestamp"      : None,
    "gps_lat"        : 0.0,
    "gps_lon"        : 0.0,
    "gps_speed_kmh"  : 0.0,
    "gps_fix"        : False,
    "hall_speed_kmh" : 0.0,
    "alcohol_voltage": 0.0,
    "alcohol_alert"  : False,
    "vibration"      : False,
    "crash_detected" : False,
    "system_status"  : "STARTING",
}
state_lock = threading.Lock()

def update_state(**kwargs):
    with state_lock:
        state.update(kwargs)
        state["timestamp"] = datetime.now().isoformat()

def get_state() -> dict:
    with state_lock:
        return dict(state)

# ── GPS Thread ───────────────────────────────────────────────────────────────
def gps_thread():
    """Parse NMEA sentences from NEO-6M over /dev/ttyAMA0."""
    try:
        import serial
        import pynmea2
        GPS_PORT = "/dev/ttyAMA0"
        with serial.Serial(GPS_PORT, 9600, timeout=1) as gps:
            logger.info("GPS thread started on %s", GPS_PORT)
            while True:
                try:
                    line = gps.readline().decode("ascii", errors="ignore").strip()
                    if line.startswith("$GPRMC") or line.startswith("$GNRMC"):
                        msg = pynmea2.parse(line)
                        if msg.status == "A":  # Active fix
                            update_state(
                                gps_lat       = float(msg.latitude),
                                gps_lon       = float(msg.longitude),
                                gps_speed_kmh = float(msg.spd_over_grnd or 0) * 1.852,
                                gps_fix       = True,
                            )
                        else:
                            update_state(gps_fix=False)
                except pynmea2.ParseError:
                    pass
    except Exception as exc:
        logger.error("GPS thread error: %s", exc)
        update_state(gps_fix=False, system_status="GPS_ERROR")


# ── Hall Effect Speed Thread ─────────────────────────────────────────────────
def hall_thread():
    """Count pulses from Hall Effect sensor on GPIO 17 → km/h."""
    try:
        import RPi.GPIO as GPIO
        HALL_PIN               = 17
        PULSES_PER_REV         = 1
        WHEEL_CIRCUMFERENCE_M  = 1.85      # ~59cm diameter tyre
        SAMPLE_INTERVAL_SEC    = 1.0

        pulse_count = {"n": 0}

        def _callback(channel):
            pulse_count["n"] += 1

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=_callback)

        logger.info("Hall Effect thread started on GPIO %d", HALL_PIN)
        while True:
            pulse_count["n"] = 0
            time.sleep(SAMPLE_INTERVAL_SEC)
            revs      = pulse_count["n"] / PULSES_PER_REV
            speed_ms  = (revs * WHEEL_CIRCUMFERENCE_M) / SAMPLE_INTERVAL_SEC
            speed_kmh = speed_ms * 3.6
            update_state(hall_speed_kmh=round(speed_kmh, 1))

    except Exception as exc:
        logger.error("Hall thread error: %s", exc)


# ── MQ-3 Alcohol Thread (via ADS1115) ───────────────────────────────────────
def alcohol_thread():
    """Read MQ-3 analog output via ADS1115 channel A0."""
    try:
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ch  = AnalogIn(ads, ADS.P0)

        from crash_detection import detect_alcohol
        logger.info("MQ-3/ADS1115 thread started")

        while True:
            voltage = round(ch.voltage, 4)
            alert   = detect_alcohol(voltage)
            update_state(alcohol_voltage=voltage, alcohol_alert=alert)
            time.sleep(0.1)  # 10 Hz

    except Exception as exc:
        logger.error("Alcohol/ADS1115 thread error: %s", exc)


# ── SW-420 Vibration Thread ──────────────────────────────────────────────────
def vibration_thread():
    """Monitor SW-420 vibration sensor on GPIO 27."""
    try:
        import RPi.GPIO as GPIO
        VIB_PIN = 27

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(VIB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        logger.info("Vibration thread started on GPIO %d", VIB_PIN)
        while True:
            triggered = GPIO.input(VIB_PIN) == GPIO.LOW
            update_state(vibration=triggered)
            time.sleep(0.05)  # 20 Hz for fast response

    except Exception as exc:
        logger.error("Vibration thread error: %s", exc)


# ── Main logging loop (combines state → circular buffer) ─────────────────────
def logging_loop():
    """
    Central tick: every 100 ms, snapshot current state into circular buffer
    and run crash detection.
    """
    import circular_buffer
    import crash_detection
    import alert_dispatcher
    import data_logger

    prev_speed = 0.0
    logger.info("Logging loop started")

    while True:
        s = get_state()
        circular_buffer.log_reading(s)

        # Crash detection
        curr_speed = max(s["gps_speed_kmh"], s["hall_speed_kmh"])
        if crash_detection.detect_crash(prev_speed, curr_speed, s["vibration"]):
            logger.warning("CRASH DETECTED!")
            update_state(crash_detected=True, system_status="CRASH")
            snapshot = circular_buffer.dump_buffer()
            data_logger.save_crash_dump(snapshot, trigger="crash")
            alert_dispatcher.send_crash_sms(
                lat=s["gps_lat"], lon=s["gps_lon"], speed_kmh=prev_speed
            )
        elif s["alcohol_alert"]:
            update_state(system_status="ALCOHOL_ALERT")
            alert_dispatcher.send_alcohol_sms(
                lat=s["gps_lat"], lon=s["gps_lon"], voltage=s["alcohol_voltage"]
            )
        else:
            update_state(crash_detected=False, system_status="NORMAL")

        prev_speed = curr_speed
        time.sleep(0.1)   # 10 Hz main tick


# ── Start all threads ─────────────────────────────────────────────────────────
def start_all():
    threads = [
        threading.Thread(target=gps_thread,       daemon=True, name="GPS"),
        threading.Thread(target=hall_thread,       daemon=True, name="Hall"),
        threading.Thread(target=alcohol_thread,    daemon=True, name="MQ3"),
        threading.Thread(target=vibration_thread,  daemon=True, name="SW420"),
        threading.Thread(target=logging_loop,      daemon=True, name="Logger"),
    ]
    for t in threads:
        t.start()
        logger.info("Started thread: %s", t.name)
    return threads
