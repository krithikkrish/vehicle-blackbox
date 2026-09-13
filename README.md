# Smart Vehicle Black Box and Driver Safety Monitoring System

> ⚠️ **Teammates:** If you are looking for instructions on how to wire the hardware and run the code, **[CLICK HERE TO READ THE SETUP GUIDE](SETUP_GUIDE.md)**!

An embedded system designed to improve road safety by continuously monitoring critical vehicle and driver parameters: vibration, alcohol, and GPS location. 

During normal operation, the system alerts the driver on abnormal conditions (alcohol detection). On accident detection (via sustained vibration), it immediately records the latest sensor readings and GPS location, and transmits a crash report via SMS to assist emergency responders.

## Architecture

This project is built around a **Raspberry Pi 4B** running **Raspberry Pi OS (64-bit)**. 

### Key Features
- **Dual Logging System:** Continuously saves all sensor data to a CSV file (`continuous_log.csv`), while keeping a 15-second rolling buffer in memory.
- **Hardware Alerts:** On-device physical alerts (LEDs) for driver warnings.
- **Web Dashboard:** (Coming Soon) A Flask-based web UI hosted on the Pi for remote monitoring via a browser.
- **Crash Detection:** Triggered by sustained vibration (SW-420), filtered by duration to avoid false positives from potholes.
- **Emergency SMS:** Transmits crash location and data via a SIM800L GSM module.

## Hardware Components

### Core & Interfaces
- **Raspberry Pi 4B** (2GB/4GB)
- **USB-to-Serial Adapter** (Resolves UART conflict: GSM on USB, GPS on hardware UART)

### Sensors
- **SW-420** (Vibration sensor, digital GPIO 18)
- **MQ-3** (Alcohol sensor, digital GPIO 23)
- **Hall-Effect** (Magnet sensor, digital GPIO 22)
- **NEO-6M GPS** (Hardware UART TX/RX)

### Communication & Output
- **SIM800L** GSM/GPRS Module (via USB-to-Serial)
- LED (GPIO 17) for driver feedback.

## Setup Instructions

Please see **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for a comprehensive guide on wiring and running the code on the Raspberry Pi.
