"""
main_full.py — Vehicle Black Box (Version 3: BOTH GPS & GSM ACTIVE)
-------------------------------------------------------------------
Convenience entrypoint for launching the full Web Dashboard deployment.
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : ENABLED (SIM800L SMS alert sender on /dev/ttyUSB0)

Run on Pi:
    python3 main_full.py

Dashboard:  http://blackbox.local:5000
"""

from main import run

if __name__ == "__main__":
    run(mode="FULL")
