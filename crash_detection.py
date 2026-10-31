"""
crash_detection.py
Crash / event detection engine.
Detects collisions via SW-420 vibration impact and/or sudden speed drops.
Also handles alcohol alert threshold logic.
"""

# ── Tunable thresholds ──────────────────────────────────────────────────────
SPEED_DROP_THRESHOLD_KMPH = 20      # Deceleration threshold (km/h drop)
ALCOHOL_VOLTAGE_THRESHOLD = 0.40    # ADS1115 voltage (V) above which alert triggers
ALCOHOL_WARMUP_READINGS   = 30      # Ignore first N readings while MQ-3 warms up
VIBRATION_SUSTAINED_TICKS = 2       # Consecutive 100ms logging ticks required for vibration crash
# ────────────────────────────────────────────────────────────────────────────

_alcohol_reading_count = 0
_vibration_consecutive_ticks = 0


def detect_crash(prev_speed: float, curr_speed: float,
                 vibration_triggered: bool) -> bool:
    """
    Return True if a crash is detected.
    Conditions:
      - Primary: SW-420 sustained vibration/impact detected across consecutive cycles.
      - Secondary: Sudden severe deceleration (speed drop >= 20 km/h).
    """
    global _vibration_consecutive_ticks

    if vibration_triggered:
        _vibration_consecutive_ticks += 1
    else:
        _vibration_consecutive_ticks = 0

    # Require sustained vibration across consecutive cycles (or severe deceleration)
    # to reject transient bumps, desk vibrations, and engine idle tremors
    if _vibration_consecutive_ticks >= VIBRATION_SUSTAINED_TICKS:
        return True

    speed_drop = prev_speed - curr_speed
    if speed_drop >= SPEED_DROP_THRESHOLD_KMPH and prev_speed > 10.0:
        return True

    return False


def detect_alcohol(voltage: float) -> bool:
    """
    Return True if alcohol concentration exceeds safe threshold.
    Skips initial warmup cycles while MQ-3 heats up.
    """
    global _alcohol_reading_count
    _alcohol_reading_count += 1
    if _alcohol_reading_count < ALCOHOL_WARMUP_READINGS:
        return False
    return voltage >= ALCOHOL_VOLTAGE_THRESHOLD
