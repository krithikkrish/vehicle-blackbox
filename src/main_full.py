#!/usr/bin/env python3
"""
src/main_full.py — Vehicle Black Box CLI (Version 3: BOTH GPS & GSM ACTIVE)
--------------------------------------------------------------------------
Convenience entrypoint for launching the Headless CLI with both GPS & GSM.
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : ENABLED (SIM800L SMS on crash with live coordinates)

Run on Pi:
    python3 src/main_full.py
"""

from main import run_cli

if __name__ == "__main__":
    run_cli(mode="FULL")
