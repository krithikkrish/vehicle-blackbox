#!/usr/bin/env python3
"""
calibrate_temp.py — Interactive Temperature Sensor Calibration Tool
-------------------------------------------------------------------
Calibrates the temperature sensor connected to ADS1115 Channel A2.
Supports LM35, TMP36, and 10K NTC Thermistors.
Saves calibrated parameters to calibration.json.
"""

import os
import sys
import time
import json
import math

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HARDWARE_AVAILABLE = True
except Exception as e:
    HARDWARE_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBRATION_FILE = os.path.join(BASE_DIR, "calibration.json")


def load_calibration():
    defaults = {
        "sensor_type": "LM35",
        "offset_c": 0.0,
        "scale": 100.0,
        "min_valid_voltage": 0.05
    }
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, "r") as f:
                defaults.update(json.load(f))
        except Exception:
            pass
    return defaults


def save_calibration(config):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n[OK] Calibration saved to {CALIBRATION_FILE}")


def compute_temp(voltage, sensor_type, scale=100.0, offset_c=0.0):
    sensor_type = sensor_type.upper()
    if sensor_type == "TMP36":
        raw = (voltage - 0.5) * 100.0
    elif sensor_type == "NTC10K":
        vcc = 5.0
        v_clamped = max(0.01, min(vcc - 0.01, voltage))
        r_ntc = 10000.0 * (v_clamped / (vcc - v_clamped))
        t_k = 1.0 / ((1.0 / 298.15) + (1.0 / 3950.0) * math.log(max(1.0, r_ntc / 10000.0)))
        raw = t_k - 273.15
    else:  # LM35 default
        raw = voltage * scale
    return raw + offset_c


def main():
    print("=" * 65)
    print(" 🌡️  TEMPERATURE SENSOR CALIBRATION WIZARD")
    print("=" * 65)

    current_config = load_calibration()
    print(f"Current Config: Type={current_config.get('sensor_type')}, "
          f"Offset={current_config.get('offset_c')}°C, "
          f"Scale={current_config.get('scale')}\n")

    temp_channel = None
    if HARDWARE_AVAILABLE:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c, address=0x48)
            ads.gain = 1  # 0 to 4.096V range
            temp_channel = AnalogIn(ads, ADS.P2)
            print("Connected to ADS1115 at 0x48 (Reading Channel A2)")
        except Exception as e:
            print(f"Warning: Hardware ADS1115 unavailable ({e}). Using mock readings.")

    # Sample voltages
    voltages = []
    print("\nSampling voltage from ADS1115 Channel A2 (2 seconds)...")
    for _ in range(20):
        if temp_channel is not None:
            v = max(0.0, float(temp_channel.voltage))
        else:
            v = 0.264
        voltages.append(v)
        time.sleep(0.1)

    avg_v = sum(voltages) / len(voltages)
    print(f"Average Measured Voltage on A2: {avg_v:.4f} V")

    print("\nEstimated temperatures based on sensor models:")
    t_lm35  = compute_temp(avg_v, "LM35")
    t_tmp36 = compute_temp(avg_v, "TMP36")
    t_ntc   = compute_temp(avg_v, "NTC10K")
    print(f"  [1] LM35 (Linear 10mV/°C)           : {t_lm35:5.1f} °C")
    print(f"  [2] TMP36 (500mV offset + 10mV/°C)  : {t_tmp36:5.1f} °C")
    print(f"  [3] NTC 10K Thermistor Module        : {t_ntc:5.1f} °C")

    # Prompt user
    print("\nCalibration Options:")
    print("  1. Select Sensor Type (LM35 / TMP36 / NTC10K)")
    print("  2. Apply Quick Calibration Offset (match your room thermometer)")
    print("  3. Custom Scale & Offset")
    print("  4. Reset to Factory Defaults (LM35, Offset 0.0)")

    choice = input("\nEnter choice [1-4] (default: 2): ").strip() or "2"

    if choice == "1":
        print("\nSelect your physical sensor type:")
        print("  1. LM35 (Standard 3-pin TO-92, 10mV/°C)")
        print("  2. TMP36 (3-pin TO-92 with 500mV offset)")
        print("  3. NTC 10K Thermistor module (4-pin PCB with AO/DO)")
        st_choice = input("Select [1-3]: ").strip()
        st_map = {"1": "LM35", "2": "TMP36", "3": "NTC10K"}
        current_config["sensor_type"] = st_map.get(st_choice, "LM35")
        current_config["offset_c"] = 0.0

    elif choice == "2":
        try:
            target_str = input("\nEnter the actual current ambient/room temperature in °C (e.g. 27.5): ").strip()
            target_c = float(target_str)
            st = current_config.get("sensor_type", "LM35")
            raw_c = compute_temp(avg_v, st, scale=current_config.get("scale", 100.0), offset_c=0.0)
            offset = round(target_c - raw_c, 1)
            current_config["offset_c"] = offset
            print(f"\nCalculated Offset: {offset:+.1f} °C (Raw {raw_c:.1f}°C -> Calibrated {target_c:.1f}°C)")
        except ValueError:
            print("Invalid temperature entered. Calibration aborted.")
            return

    elif choice == "3":
        try:
            st = input("Enter sensor type [LM35 / TMP36 / NTC10K]: ").strip().upper() or "LM35"
            scale_str = input("Enter scale factor (default 100.0): ").strip() or "100.0"
            offset_str = input("Enter offset in °C (default 0.0): ").strip() or "0.0"
            current_config["sensor_type"] = st
            current_config["scale"] = float(scale_str)
            current_config["offset_c"] = float(offset_str)
        except ValueError:
            print("Invalid input. Calibration aborted.")
            return

    elif choice == "4":
        current_config = {
            "sensor_type": "LM35",
            "offset_c": 0.0,
            "scale": 100.0,
            "min_valid_voltage": 0.05
        }

    save_calibration(current_config)

    # Show new verification reading
    final_temp = compute_temp(
        avg_v,
        current_config.get("sensor_type", "LM35"),
        scale=current_config.get("scale", 100.0),
        offset_c=current_config.get("offset_c", 0.0)
    )
    print(f"\n✅ Verification: Current voltage {avg_v:.4f}V now reads as {final_temp:.1f} °C")
    print("Restart blackbox.service or main.py to apply.")


if __name__ == "__main__":
    main()
