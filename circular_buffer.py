"""
circular_buffer.py
Thread-safe rolling circular buffer for sensor readings.
Fixed depth: retains rolling window of sensor readings.
"""

from collections import deque
import threading

BUFFER_DEPTH = 300  # 30 seconds at 10 Hz

_buffer: deque = deque(maxlen=BUFFER_DEPTH)
_lock = threading.Lock()


def log_reading(reading: dict) -> None:
    """Append a sensor reading dict to the circular buffer."""
    with _lock:
        _buffer.append(dict(reading))


def get_latest() -> dict | None:
    """Return the most recent reading, or None if buffer is empty."""
    with _lock:
        return _buffer[-1] if _buffer else None


def dump_buffer() -> list:
    """Return a snapshot copy of the entire buffer."""
    with _lock:
        return list(_buffer)


def dump_last_seconds(seconds: int = 10) -> list:
    """Return readings from the last N seconds (at 10 Hz)."""
    with _lock:
        count = seconds * 10
        return list(_buffer)[-count:]


def get_all() -> list:
    """Return all entries (alias for dump_buffer, used by dashboard API)."""
    return dump_buffer()


def size() -> int:
    with _lock:
        return len(_buffer)
