# Smart Vehicle Black Box and Driver Safety Monitoring System

An embedded system designed to improve road safety by continuously monitoring critical vehicle and driver parameters: speed, vibration, temperature, alcohol, smoke, and GPS location. 

During normal operation, the system alerts the driver on abnormal conditions (overspeeding, high temperature, alcohol detection, smoke). On accident detection (via vibration/accelerometer), it immediately records the latest sensor readings and GPS location, and transmits a crash report to assist emergency responders.

## Architecture

This project is built around a **Raspberry Pi 4B** running **Raspberry Pi OS Lite (64-bit)**. 

### Key Features
- **Circular Data Buffer:** Continuously stores the last 10-15 seconds of sensor data in memory.
- **Hardware Alerts:** On-device physical alerts (buzzer and LEDs) for driver warnings.
- **Web Dashboard:** A Flask-based web UI hosted on the Pi for remote monitoring via a browser.
- **Crash Detection:** Triggered by high-G impacts (MPU6050) and vibration (SW-420), filtered by duration to avoid false positives.
- **Emergency SMS:** Transmits crash location and data via a SIM800L GSM module.

## Hardware Components

### Core & Interfaces
- **Raspberry Pi 4B** (2GB/4GB)
- **ADS1115** 16-bit I2C ADC (Required for reading analog sensors on the Pi)
- **USB-to-Serial Adapter** (Resolves UART conflict: GSM on USB, GPS on hardware UART)
- **DS3231 RTC Module** (I2C) for accurate offline timekeeping.

### Sensors
- **MPU6050** (Accelerometer + Gyroscope, I2C)
- **SW-420** (Vibration sensor, digital GPIO)
- **MQ-3** (Alcohol sensor, analog via ADC)
- **MQ-2** (Smoke/gas sensor, analog via ADC)
- **DS18B20** (Temperature sensor, 1-Wire)
- **IR Speed Sensor** (Digital pulse output)
- **NEO-6M GPS** (Hardware UART)

### Communication & Output
- **SIM800L** GSM/GPRS Module (via USB-to-Serial)
- Buzzer (Active) & LEDs for driver feedback.

## Setup Instructions

1. **OS Installation:** Flash a microSD card with Raspberry Pi OS Lite (64-bit). Enable SSH and Wi-Fi during imaging.
2. **System Config:** Boot the Pi, SSH in, and run `sudo raspi-config` to enable I2C, SPI, and Serial (disable serial console, enable serial hardware).
3. **Dependencies:** Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```
4. **Wiring:** Wire the sensors according to the GPIO mapping (documentation pending). 
5. **Testing:** Run the standalone scripts in the `tests/` directory to verify individual components before running the main loop.
