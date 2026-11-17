"""
tests/test_unit.py
Automated unit test suite for the Vehicle Black Box system.
Tests circular buffer, crash detection algorithm, data logger, and Flask endpoints.
Runs without hardware dependencies (compatible with CI/CD).
"""

import json
import os
import shutil
import tempfile
import unittest

# Ensure repo root is on sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import circular_buffer
import crash_detection
import data_logger

try:
    from app import app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    app = None


class TestCircularBuffer(unittest.TestCase):
    def setUp(self):
        # Clear buffer before each test
        circular_buffer._buffer.clear()

    def test_log_reading_and_latest(self):
        reading = {"timestamp": "2026-11-17T10:00:00", "speed": 45.0}
        circular_buffer.log_reading(reading)
        self.assertEqual(circular_buffer.size(), 1)
        latest = circular_buffer.get_latest()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["speed"], 45.0)

    def test_buffer_capacity_rollover(self):
        depth = circular_buffer.BUFFER_DEPTH
        for i in range(depth + 50):
            circular_buffer.log_reading({"index": i})
        self.assertEqual(circular_buffer.size(), depth)
        all_entries = circular_buffer.get_all()
        self.assertEqual(len(all_entries), depth)
        # Oldest preserved entry should be index 50
        self.assertEqual(all_entries[0]["index"], 50)
        # Newest entry should be index depth + 49
        self.assertEqual(all_entries[-1]["index"], depth + 49)

    def test_dump_buffer_returns_copy(self):
        circular_buffer.log_reading({"val": 1})
        dump = circular_buffer.dump_buffer()
        self.assertEqual(len(dump), 1)
        dump.append({"val": 2})
        # Internal buffer should remain unchanged
        self.assertEqual(circular_buffer.size(), 1)


class TestCrashDetection(unittest.TestCase):
    def test_crash_detected_on_vibration_impact(self):
        # Physical impact detected by SW-420 triggers crash
        result = crash_detection.detect_crash(
            prev_speed=50.0, curr_speed=48.0, vibration_triggered=True
        )
        self.assertTrue(result)

    def test_crash_detected_on_severe_deceleration(self):
        # Severe deceleration (speed drop >= 20 km/h from > 10 km/h) triggers crash even without sensor trigger
        result = crash_detection.detect_crash(
            prev_speed=60.0, curr_speed=20.0, vibration_triggered=False
        )
        self.assertTrue(result)

    def test_no_crash_on_normal_braking(self):
        # Normal braking (speed drop < 20 km/h without vibration) should NOT trigger crash
        result = crash_detection.detect_crash(
            prev_speed=30.0, curr_speed=20.0, vibration_triggered=False
        )
        self.assertFalse(result)

    def test_no_crash_stationary(self):
        # Stationary vehicle with no vibration should NOT trigger crash
        result = crash_detection.detect_crash(
            prev_speed=0.0, curr_speed=0.0, vibration_triggered=False
        )
        self.assertFalse(result)

    def test_alcohol_warmup_filter(self):
        # Reset counter
        crash_detection._alcohol_reading_count = 0
        # Warmup readings should return False regardless of voltage
        for _ in range(crash_detection.ALCOHOL_WARMUP_READINGS - 1):
            self.assertFalse(crash_detection.detect_alcohol(voltage=0.85))

        # After warmup, high voltage triggers alert
        self.assertTrue(crash_detection.detect_alcohol(voltage=0.85))
        # Normal voltage does not trigger alert
        self.assertFalse(crash_detection.detect_alcohol(voltage=0.20))


class TestDataLogger(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_log_dir = data_logger.LOG_DIR
        data_logger.LOG_DIR = self.test_dir

    def tearDown(self):
        data_logger.LOG_DIR = self.orig_log_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_crash_dump(self):
        sample_entries = [
            {"timestamp": "2026-11-17T10:00:00", "hall_speed_kmh": 50.0},
            {"timestamp": "2026-11-17T10:00:01", "hall_speed_kmh": 0.0},
        ]
        saved_path = data_logger.save_crash_dump(sample_entries, trigger="test_crash")
        self.assertTrue(os.path.isfile(saved_path))

        fname = os.path.basename(saved_path)
        loaded = data_logger.load_crash_log(fname)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["event"], "test_crash")
        self.assertEqual(len(loaded["entries"]), 2)

    def test_list_crash_logs(self):
        data_logger.save_crash_dump([{"tick": 1}], trigger="event1")
        data_logger.save_crash_dump([{"tick": 2}], trigger="event2")
        logs = data_logger.list_crash_logs()
        self.assertEqual(len(logs), 2)
        self.assertIn("filename", logs[0])
        self.assertIn("size_bytes", logs[0])


@unittest.skipIf(not FLASK_AVAILABLE, "Flask not installed in test environment")
class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_dashboard_route_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"VEHICLE BLACK BOX", response.data)

    def test_api_live_endpoint(self):
        response = self.client.get("/api/live")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("system_status", data)
        self.assertIn("gps_speed_kmh", data)
        self.assertIn("hall_speed_kmh", data)

    def test_api_history_endpoint(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_logs_page_route(self):
        response = self.client.get("/logs")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Crash", response.data)


if __name__ == "__main__":
    unittest.main()
