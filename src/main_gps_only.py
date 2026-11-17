#!/usr/bin/env python3
"""
src/main_gps_only.py — Vehicle Black Box CLI (Version 2: GPS ONLY, No GSM)
-------------------------------------------------------------------------
Convenience entrypoint for launching the Headless CLI in GPS-only mode.
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : DISABLED (No SMS attempts)

Run on Pi:
    python3 src/main_gps_only.py
"""

from main import run_cli

if __name__ == "__main__":
    run_cli(mode="GPS_ONLY")
