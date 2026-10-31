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

    # Load calibration settings
    import os, json, math
    cal_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "calibration.json")
    cal = {"sensor_type": "LM35", "offset_c": 0.0, "scale": 100.0}
    if os.path.exists(cal_file):
        try:
            with open(cal_file, "r") as f:
                cal.update(json.load(f))
        except Exception:
            pass

    st = cal.get("sensor_type", "LM35")
    offset = float(cal.get("offset_c", 0.0))
    scale = float(cal.get("scale", 100.0))
    print(f"Active Calibration: Sensor={st} | Offset={offset:+.1f}°C | Scale={scale}\n")

    try:
        while True:
            if temp_channel is not None:
                voltage = max(0.0, float(temp_channel.voltage))
                raw_val = int(temp_channel.value)
            else:
                voltage = round(random.uniform(0.24, 0.28), 3)
                raw_val = int((voltage / 4.096) * 32767)

            if st == "TMP36":
                raw_c = (voltage - 0.5) * 100.0
            elif st == "NTC10K":
                vcc = 5.0
                v_clamped = max(0.01, min(vcc - 0.01, voltage))
                r_ntc = 10000.0 * (v_clamped / (vcc - v_clamped))
                t_k = 1.0 / ((1.0 / 298.15) + (1.0 / 3950.0) * math.log(max(1.0, r_ntc / 10000.0)))
                raw_c = t_k - 273.15
            else:  # LM35
                raw_c = voltage * scale

            celsius = round(raw_c + offset, 2)

            if voltage < 0.10:
                diag = "[⚠️  LOW / FLOATING]"
            elif 0.15 <= voltage <= 0.45:
                diag = "[🟢 OK - Ambient]"
            else:
                diag = "[ℹ️  INFO]"

            print(f"[{time.strftime('%H:%M:%S')}] Temp Sensor -> Voltage: {voltage:.3f} V | Raw: {raw_val:5d} | Temp: {celsius:5.2f} °C ({st}) {diag}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting temperature test.")


if __name__ == "__main__":
    main()
