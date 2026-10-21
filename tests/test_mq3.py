#!/usr/bin/env python3
"""
test_mq3.py
Tests the MQ-3 Gas/Alcohol Sensor connected via ADS1115 Channel A0.
Specification:
  - VCC  → 5V (Pin 2)
  - GND  → Ground (Pin 6)
  - AOUT → ADS1115 Channel A0 (I2C 0x48)
  - Formula: PPM = (Voltage / 5.0) * 100
  - Threshold: Voltage >= 0.40V triggers Alcohol Alert
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
    print("=" * 55)
    print(" Testing MQ-3 Gas/Alcohol Sensor (via ADS1115 A0)")
    print("=" * 55)

    mq3_channel = None
    if HARDWARE_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c, address=0x48)
            ads.gain = 1  # 0 to 4.096V range
            mq3_channel = AnalogIn(ads, ADS.P0)  # Channel A0
            print("Connected to ADS1115 at 0x48. Reading Channel A0...")
        except Exception as e:
            print(f"ADS1115 connection failed: {e}. Falling back to MOCK mode.")
            mq3_channel = None

    try:
        while True:
            if mq3_channel is not None:
                voltage = max(0.0, float(mq3_channel.voltage))
                raw_val = int(mq3_channel.value)
                ppm = (voltage / 5.0) * 100.0
            else:
                voltage = round(random.uniform(0.30, 0.45), 3)
                raw_val = int((voltage / 4.096) * 32767)
                ppm = round((voltage / 5.0) * 100.0, 2)

            status = "🚨 ALERT (ALCOHOL DETECTED)" if voltage >= 0.40 else "NORMAL"
            print(f"[{time.strftime('%H:%M:%S')}] MQ-3 -> Voltage: {voltage:.3f} V | Raw: {raw_val:5d} | PPM: {ppm:.1f} | Status: {status}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting MQ-3 test.")


if __name__ == "__main__":
    main()
