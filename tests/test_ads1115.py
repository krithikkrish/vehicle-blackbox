#!/usr/bin/env python3
"""
test_ads1115.py
Tests the ADS1115 16-bit ADC connected over I2C.
Specification:
  - VDD → 5V (Pin 2 or 4) - CRITICAL: 5V power to read full 0-5V analog range
  - GND → Ground (Pin 14)
  - SDA → GPIO 2 / Pin 3
  - SCL → GPIO 3 / Pin 5
  - Address: 0x48 (default)
  - Channels:
      A0: MQ-3 Gas Sensor
      A1: Vibration Sensor (if analog) / Reserved
      A2: Temperature Sensor (LM35)
      A3: Unused
"""

import time
import random

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HARDWARE_AVAILABLE = True
except Exception as e:
    print(f"Hardware/library import failed ({e}). Running in MOCK mode.")
    HARDWARE_AVAILABLE = False


def main():
    print("=" * 60)
    print(" ADS1115 16-Bit I2C ADC Diagnostic & Channel Scanner")
    print(" Address: 0x48 | SDA: GPIO 2 (Pin 3) | SCL: GPIO 3 (Pin 5)")
    print("=" * 60)

    channels = {}
    if HARDWARE_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c, address=0x48)
            ads.gain = 1  # 0 to 4.096V range
            channels = {
                "A0 (MQ-3 Gas)"     : AnalogIn(ads, ADS.P0),
                "A1 (Reserved)"     : AnalogIn(ads, ADS.P1),
                "A2 (Temperature)"  : AnalogIn(ads, ADS.P2),
                "A3 (Unused)"       : AnalogIn(ads, ADS.P3),
            }
            print("Successfully initialized ADS1115 at 0x48!\n")
        except Exception as e:
            print(f"ADS1115 hardware error: {e}. Falling back to MOCK mode.\n")
            channels = {}

    try:
        while True:
            print(f"--- Snapshot at {time.strftime('%H:%M:%S')} ---")
            if channels:
                for name, ch in channels.items():
                    v = max(0.0, float(ch.voltage))
                    raw = int(ch.value)
                    print(f"  {name:18s} -> Voltage: {v:.4f} V | Raw Value: {raw:5d}")
            else:
                # Mock display
                print(f"  {'A0 (MQ-3 Gas)':18s} -> Voltage: {random.uniform(0.3, 0.5):.4f} V | Raw Value: {random.randint(2400, 4000):5d}")
                print(f"  {'A1 (Reserved)':18s} -> Voltage: {random.uniform(0.0, 0.1):.4f} V | Raw Value: {random.randint(0, 800):5d}")
                print(f"  {'A2 (Temperature)':18s} -> Voltage: {random.uniform(0.24, 0.28):.4f} V | Raw Value: {random.randint(1900, 2200):5d}")
                print(f"  {'A3 (Unused)':18s} -> Voltage: {0.0:.4f} V | Raw Value: {0:5d}")

            print()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting ADS1115 diagnostic test.")


if __name__ == "__main__":
    main()
