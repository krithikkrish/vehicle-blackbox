"""
main_gps_only.py — Vehicle Black Box (Version 2: GPS ONLY, No GSM)
-----------------------------------------------------------------
Convenience entrypoint for launching the Web Dashboard in GPS-only mode.
- GPS Module  : ENABLED (NEO-6M NMEA parser on /dev/ttyAMA0 @ 9600 baud)
- GSM Alerts  : DISABLED (No SMS transmission attempts, avoiding port conflicts)

Run on Pi:
    python3 main_gps_only.py

Dashboard:  http://blackbox.local:5000
"""

from main import run

if __name__ == "__main__":
    run(mode="GPS_ONLY")
