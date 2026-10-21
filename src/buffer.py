from collections import deque
import json
import csv
import time
import os

class CircularBuffer:
    def __init__(self, max_seconds=10, sample_rate_hz=10):
        # Calculate max items based on time and frequency (10s * 10Hz = 100 samples)
        self.max_items = max_seconds * sample_rate_hz
        self.buffer = deque(maxlen=self.max_items)
        
    def add_reading(self, reading):
        """Add a new dictionary of sensor readings to the buffer."""
        self.buffer.append(reading)
        
    def get_all(self):
        """Return a list of all current readings in chronological order."""
        return list(self.buffer)
        
    def dump_to_file(self, filename="crash_dump.json"):
        """Save the current buffer to a JSON file (e.g., during a crash)."""
        data = {
            "timestamp": time.time(),
            "event": "CRASH_DETECTED",
            "history": list(self.buffer)
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Buffer successfully dumped to {filename}")
        return filename

class CSVLogger:
    def __init__(self, filename="continuous_log.csv"):
        self.filename = filename
        self.headers_written = False
        
    def log_reading(self, reading):
        """Append a single reading to the continuous CSV log."""
        # Flatten row for clean CSV logging
        row = {}
        for k, v in reading.items():
            if isinstance(v, dict):
                # Extract simple sub-values if not already present
                for sub_k, sub_v in v.items():
                    col_name = f"{k}_{sub_k}"
                    if col_name not in reading and not isinstance(sub_v, dict):
                        row[col_name] = sub_v
            else:
                row[k] = v

        file_exists = os.path.isfile(self.filename)
        with open(self.filename, mode='a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=row.keys())
            if not file_exists or not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            writer.writerow(row)
