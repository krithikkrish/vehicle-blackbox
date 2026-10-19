"""
crash_detection.py
Crash / event detection engine.
Combines SW-420 vibration flag + sudden speed drop to confirm a crash.
Also handles alcohol alert threshold logic.
"""

# ── Tunable thresholds ──────────────────────────────────────────────────────
SPEED_DROP_THRESHOLD_KMPH = 20      # Speed must drop ≥ this in one tick
ALCOHOL_VOLTAGE_THRESHOLD = 0.40    # ADS1115 voltage (V) above which alert triggers
ALCOHOL_WARMUP_READINGS = 60        # Ignore first N readings while MQ-3 warms up
# ────────────────────────────────────────────────────────────────────────────

_alcohol_reading_count = 0


def detect_crash(prev_speed: float, curr_speed: float,
                 vibration_triggered: bool) -> bool:
    """
    Return True if a crash is detected.
    Conditions: vibration flag set AND sudden speed drop.
    """
    speed_drop = prev_speed - curr_speed
    return vibration_triggered and speed_drop >= SPEED_DROP_THRESHOLD_KMPH


def detect_alcohol(voltage: float) -> bool:
    """
    Return True if alcohol concentration exceeds safe threshold.
    Skips the first ALCOHOL_WARMUP_READINGS readings while MQ-3 heats up.
    """
    global _alcohol_reading_count
    _alcohol_reading_count += 1
    if _alcohol_reading_count < ALCOHOL_WARMUP_READINGS:
        return False
    return voltage >= ALCOHOL_VOLTAGE_THRESHOLD
