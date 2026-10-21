#!/usr/bin/env python3
"""
test_temperature.py
Tests the analog temperature sensor (e.g. LM35) connected via ADS1115 Channel A2.
Specification:
  - VCC  → 5V (Pin 4)
  - GND  → Ground (Pin 6)
  - AOUT → ADS1115 Channel A2 (I2C 0x48)
  - Output: 10mV/°C -> Celsius = Voltage * 100.0
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
    print(" Testing Temperature Sensor (LM35 via ADS1115 A2)")
    print("=" * 55)

    temp_channel = None
    if HARDWARE_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c, address=0x48)
            ads.gain = 1  # 0 to 4.096V range
            temp_channel = AnalogIn(ads, ADS.P2)  # Channel A2
            print("Connected to ADS1115 at 0x48. Reading Channel A2...")
        except Exception as e:
            print(f"ADS1115 connection failed: {e}. Falling back to MOCK mode.")
            temp_channel = None

    try:
        while True:
            if temp_channel is not None:
                voltage = max(0.0, float(temp_channel.voltage))
                raw_val = int(temp_channel.value)
                celsius = voltage * 100.0  # LM35 conversion (10mV per deg C)
            else:
                voltage = round(random.uniform(0.24, 0.28), 3)
                raw_val = int((voltage / 4.096) * 32767)
                celsius = round(voltage * 100.0, 2)

            print(f"[{time.strftime('%H:%M:%S')}] Temp Sensor -> Voltage: {voltage:.3f} V | Raw: {raw_val:5d} | Temp: {celsius:.2f} °C")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting temperature test.")


if __name__ == "__main__":
    main()
