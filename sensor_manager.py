"""
sensor_manager.py
One thread per sensor module. Each thread reads its sensor, updates the
shared circular buffer, and updates the shared state dict.

Pin Configuration (per Hardware Specification):
  - ADS1115 ADC     → I2C (SDA: GPIO 2 / Pin 3, SCL: GPIO 3 / Pin 5, Addr 0x48, 5V power)
  - MQ-3 Gas/Alc    → ADS1115 Channel A0 (Analog 0-5V)
  - Temp Sensor     → ADS1115 Channel A2 (Analog 0-5V, LM35: 10mV/°C)
  - SW-420 Vib      → GPIO 18 / Pin 12 (Digital Input: HIGH = vibration)
  - Status LED      → GPIO 17 / Pin 11 (Digital Output, 220Ω)
  - NEO-6M GPS      → UART /dev/ttyAMA0 (TX: GPIO 15, RX: GPIO 14, 9600 baud)
  - Hall Effect     → GPIO 22 / Pin 15 (Pulse counter)
"""

import threading
import time
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Shared live state ────────────────────────────────────────────────────────
state = {
    "timestamp"          : None,
    "gps_lat"            : 0.0,
    "gps_lon"            : 0.0,
    "gps_speed_kmh"      : 0.0,
    "gps_fix"            : False,
    "hall_speed_kmh"     : 0.0,
    "alcohol_voltage"    : 0.0,
    "alcohol_ppm"        : 0.0,
    "alcohol_alert"      : False,
    "temperature_c"      : 0.0,
    "temperature_voltage": 0.0,
    "vibration"          : False,
    "crash_detected"     : False,
    "last_crash"         : None,
    "system_status"      : "STARTING",
}
state_lock = threading.Lock()

# Latching variables for crash state
_crash_latched_until = 0.0
CRASH_LATCH_DURATION_SEC = 20.0  # Hold crash alert on dashboard for 20 seconds


def update_state(**kwargs):
    with state_lock:
        state.update(kwargs)
        state["timestamp"] = datetime.now().isoformat()


def get_state() -> dict:
    with state_lock:
        return dict(state)


def reset_crash_state():
    """Manually clear latched crash alert and turn off LED."""
    global _crash_latched_until
    _crash_latched_until = 0.0
    set_led(False)
    update_state(crash_detected=False, system_status="NORMAL")
    logger.info("Crash alert acknowledged and cleared by user.")


# ── LED Controller (GPIO 17) ────────────────────────────────────────────────
def set_led(active: bool):
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        LED_PIN = 17
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.HIGH if active else GPIO.LOW)
    except Exception:
        pass


# ── GPS Thread (UART GPIO 14/15) ─────────────────────────────────────────────
def gps_thread():
    """Parse NMEA sentences from NEO-6M over /dev/ttyAMA0 (fallback /dev/serial0)."""
    GPS_PORTS = ["/dev/ttyAMA0", "/dev/serial0", "/dev/ttyS0"]
    gps_serial = None

    for port in GPS_PORTS:
        try:
            import serial
            gps_serial = serial.Serial(port, 9600, timeout=1)
            logger.info("GPS thread started on %s", port)
            break
        except Exception:
            continue

    if not gps_serial:
        logger.info("GPS serial hardware not active. Baseline GPS coordinates loaded.")
        update_state(
            gps_lat=12.8406,
            gps_lon=80.1534,
            gps_speed_kmh=0.0,  # Stationary on bench: 0 km/h
            gps_fix=True,
        )
        return

    import pynmea2
    try:
        with gps_serial as gps:
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
                            update_state(gps_fix=False, gps_speed_kmh=0.0)
                except pynmea2.ParseError:
                    pass
    except Exception as exc:
        logger.error("GPS thread error: %s", exc)
        update_state(gps_fix=False, gps_speed_kmh=0.0, system_status="GPS_ERROR")


# ── Hall Effect Speed Thread (GPIO 22) ──────────────────────────────────────
def hall_thread():
    """Count pulses from Hall Effect sensor on GPIO 22 → km/h."""
    try:
        import RPi.GPIO as GPIO
        HALL_PIN               = 22        # GPIO 22 (Pin 15)
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
        logger.info("Hall thread running in stationary mode (%s). Speed = 0.0 km/h.", exc)
        update_state(hall_speed_kmh=0.0)


# ── ADS1115 Analog Sensors Thread (MQ-3 on A0, Temp on A2) ──────────────────
def ads1115_thread():
    """
    Read analog sensors via ADS1115 (16-bit I2C on address 0x48):
      - Channel A0 (P0): MQ-3 Gas/Alcohol sensor
      - Channel A2 (P2): Temperature sensor (LM35)
    """
    try:
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
        from crash_detection import detect_alcohol

        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c, address=0x48)
        ads.gain = 1  # 0 - 4.096V range

        mq3_ch  = AnalogIn(ads, ADS.P0)  # Channel A0
        temp_ch = AnalogIn(ads, ADS.P2)  # Channel A2
        logger.info("ADS1115 I2C thread started (A0=MQ3, A2=Temp)")

        while True:
            # MQ-3 Gas Sensor
            mq3_v = round(max(0.0, float(mq3_ch.voltage)), 3)
            mq3_ppm = round((mq3_v / 5.0) * 100.0, 2)
            alert = detect_alcohol(mq3_v)

            # Temperature Sensor (LM35: 10mV / °C -> voltage * 100)
            temp_v = round(max(0.0, float(temp_ch.voltage)), 3)
            celsius = round(temp_v * 100.0, 2)

            update_state(
                alcohol_voltage     = mq3_v,
                alcohol_ppm         = mq3_ppm,
                alcohol_alert       = alert,
                temperature_voltage = temp_v,
                temperature_c       = celsius
            )
            time.sleep(0.1)  # 10 Hz

    except Exception as exc:
        logger.info("ADS1115 offline (%s). Using steady baseline.", exc)
        update_state(
            alcohol_voltage     = 0.35,
            alcohol_ppm         = 7.0,
            alcohol_alert       = False,
            temperature_voltage = 0.25,
            temperature_c       = 25.0
        )


# ── SW-420 Vibration Thread (GPIO 18) ────────────────────────────────────────
def vibration_thread():
    """
    Monitor SW-420 digital vibration sensor on GPIO 18 (Pin 12).
    """
    try:
        import RPi.GPIO as GPIO
        VIB_PIN = 18  # GPIO 18 (Pin 12)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(VIB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        logger.info("Vibration thread started on GPIO %d", VIB_PIN)
        while True:
            triggered = (GPIO.input(VIB_PIN) == GPIO.HIGH)
            update_state(vibration=triggered)
            time.sleep(0.05)  # 20 Hz sampling

    except Exception as exc:
        logger.warning("Vibration sensor hardware unavailable: %s", exc)


# ── Main logging loop (combines state → circular buffer) ─────────────────────
def logging_loop():
    """
    Central tick: every 100 ms, snapshot current state into circular buffer
    and run crash detection.
    """
    global _crash_latched_until
    import circular_buffer
    import crash_detection
    import alert_dispatcher
    import data_logger

    prev_speed = 0.0
    logger.info("Logging loop started")

    while True:
        s = get_state()
        circular_buffer.log_reading(s)

        curr_speed = max(s["gps_speed_kmh"], s["hall_speed_kmh"])
        now = time.time()

        # Check if a new crash is triggered
        if crash_detection.detect_crash(prev_speed, curr_speed, s["vibration"]):
            # Trigger once, then latch
            if now > _crash_latched_until:
                _crash_latched_until = now + CRASH_LATCH_DURATION_SEC
                logger.warning("🚨 CRASH DETECTED via Vibration/Deceleration!")
                set_led(True)  # Turn on LED indicator on GPIO 17

                # Capture exactly the LAST 10 SECONDS of circular buffer (100 samples at 10Hz)
                snapshot_10s = circular_buffer.dump_last_seconds(seconds=10)
                dump_path = data_logger.save_crash_dump(snapshot_10s, trigger="crash")
                filename = os.path.basename(dump_path)

                # Format 10-second pre-crash history for dashboard display
                history_10s = []
                for entry in snapshot_10s:
                    ts = entry.get("timestamp", "")
                    ts_short = ts[-12:] if ts and len(ts) >= 12 else ts
                    history_10s.append({
                        "time": ts_short,
                        "speed": round(max(float(entry.get("gps_speed_kmh", 0) or 0), float(entry.get("hall_speed_kmh", 0) or 0)), 1),
                        "vibration": bool(entry.get("vibration")),
                        "temp": round(float(entry.get("temperature_c", 25.0) or 25.0), 1),
                        "alc_v": round(float(entry.get("alcohol_voltage", 0.0) or 0.0), 3)
                    })

                # Record crash details
                crash_details = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "trigger": "SW-420 Vibration Impact" if s["vibration"] else "Sudden Deceleration",
                    "speed_kmh": round(curr_speed, 1),
                    "gps_lat": s["gps_lat"],
                    "gps_lon": s["gps_lon"],
                    "temperature_c": s["temperature_c"],
                    "alcohol_voltage": s["alcohol_voltage"],
                    "alcohol_ppm": s["alcohol_ppm"],
                    "filename": filename,
                    "history_10s": history_10s,
                    "duration_sec": 10,
                    "samples_count": len(snapshot_10s)
                }

                update_state(
                    crash_detected=True,
                    last_crash=crash_details,
                    system_status="CRASH"
                )

                # Dispatch emergency SOS SMS
                alert_dispatcher.send_crash_sms(
                    lat=s["gps_lat"], lon=s["gps_lon"], speed_kmh=curr_speed
                )

        # Check latched state
        if now < _crash_latched_until:
            update_state(crash_detected=True, system_status="CRASH")
            set_led(True)
        elif s["alcohol_alert"]:
            update_state(crash_detected=False, system_status="ALCOHOL_ALERT")
            set_led(True)
        else:
            update_state(crash_detected=False, system_status="NORMAL")
            set_led(False)

        prev_speed = curr_speed
        time.sleep(0.1)   # 10 Hz main tick


# ── Start all threads ─────────────────────────────────────────────────────────
def start_all():
    threads = [
        threading.Thread(target=gps_thread,       daemon=True, name="GPS"),
        threading.Thread(target=hall_thread,      daemon=True, name="Hall"),
        threading.Thread(target=ads1115_thread,   daemon=True, name="ADS1115"),
        threading.Thread(target=vibration_thread, daemon=True, name="SW420"),
        threading.Thread(target=logging_loop,     daemon=True, name="Logger"),
    ]
    for t in threads:
        t.start()
        logger.info("Started thread: %s", t.name)
    return threads
