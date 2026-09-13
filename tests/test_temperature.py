#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import os
import glob
import time
import random

# Base directory for 1-Wire devices on Raspberry Pi
BASE_DIR = '/sys/bus/w1/devices/'

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def get_temperature():
    try:
        # Find the DS18B20 folder (starts with 28-)
        device_folder = glob.glob(BASE_DIR + '28*')[0]
        device_file = device_folder + '/w1_slave'
        
        lines = read_temp_raw(device_file)
        # Wait until the sensor returns YES
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
            
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
            
    except (IndexError, FileNotFoundError):
        # We are on a Mac or the sensor is not wired correctly!
        # Return a mock value instead of crashing.
        return random.uniform(25.0, 30.0)

def main():
    print("Starting Temperature Test...")
    if not os.path.exists(BASE_DIR):
        print("Warning: /sys/bus/w1/devices not found. Using MOCK mode (Mac).")
        
    try:
        while True:
            temp_c = get_temperature()
            print(f"Temperature: {temp_c:.2f} °C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting temperature test.")

if __name__ == "__main__":
    main()
