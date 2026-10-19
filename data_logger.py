"""
data_logger.py
Persists crash dumps and event logs to the filesystem as JSON files.
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(os.path.dirname(__file__), "crash_logs")
os.makedirs(LOG_DIR, exist_ok=True)


def save_crash_dump(buffer_snapshot: list, trigger: str = "crash") -> str:
    """
    Write the circular-buffer snapshot to a timestamped JSON file.
    Returns the file path of the saved dump.
    """
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{trigger}_{ts}.json"
    filepath = os.path.join(LOG_DIR, filename)

    payload = {
        "event"     : trigger,
        "timestamp" : datetime.now().isoformat(),
        "entries"   : buffer_snapshot,
    }

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)

    logger.info("Crash dump saved → %s", filepath)
    return filepath


def list_crash_logs() -> list[dict]:
    """
    Return a list of all saved crash log files with metadata.
    Sorted newest-first.
    """
    logs = []
    for fname in sorted(os.listdir(LOG_DIR), reverse=True):
        if fname.endswith(".json"):
            fpath = os.path.join(LOG_DIR, fname)
            stat  = os.stat(fpath)
            logs.append({
                "filename"    : fname,
                "size_bytes"  : stat.st_size,
                "modified_at" : datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    return logs


def load_crash_log(filename: str) -> dict | None:
    """Load a specific crash log JSON by filename."""
    fpath = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(fpath):
        return None
    with open(fpath) as f:
        return json.load(f)
