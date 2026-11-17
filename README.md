# 🚗 Autonomous IoT Vehicle Black Box & Event Data Recorder (EDR)

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%204B-C51A4A?style=flat-square&logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.com/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0-000000?style=flat-square&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![Architecture](https://img.shields.io/badge/Interface-I%C2%B2C%20%7C%20UART%20%7C%20GPIO-00599C?style=flat-square)](https://www.raspberrypi.com/documentation/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete%20%2F%20Production%20Ready-brightgreen?style=flat-square)]()

> A robust, fault-tolerant embedded Event Data Recorder (EDR) and telematics telemetry hub engineered for the **Raspberry Pi 4B**. Provides continuous 10Hz sensor data acquisition, dual-tier fail-safe storage, false-positive resilient impact detection, preventive cabin air monitoring, automated satellite-coordinated SMS emergency dispatch, and a live web telemetry dashboard.

---

## 📑 Table of Contents

- [Executive Summary](#-executive-summary)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Hardware & Pinout Specifications](#-hardware--pinout-specifications)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Execution & Operating Modes](#-execution--operating-modes)
  - [1. Web Dashboard Mode](#1-web-dashboard-mode-default)
  - [2. Headless CLI Mode](#2-headless-cli-mode)
  - [Operational Modes Matrix](#operational-modes-matrix)
- [REST API Reference](#-rest-api-reference)
- [Sensor Calibration & Diagnostics Suite](#-sensor-calibration--diagnostics-suite)
- [Production Deployment (systemd)](#-production-deployment-systemd)
- [Supplementary Documentation](#-supplementary-documentation)

---

## 🌟 Executive Summary

Post-accident forensic investigation and emergency dispatch often suffer from critical informational blind spots:
1. **Critical Pre-Crash Data Gap:** Without objective telemetry, it is nearly impossible to verify speed, driver intoxication, cabin conditions, or trajectory leading up to an impact for insurance audits.
2. **Emergency Response Latency:** Unconscious occupants or accidents on remote roadways cause delayed rescue operations, drastically increasing mortality rates.
3. **Commercial Barrier:** Proprietary fleet black boxes are costly, closed-source, and difficult to customize for modular lab testing and fleet integration.

This project delivers an open, production-ready IoT Black Box that records sensor state continuously at 10Hz, freezes the critical pre-crash window into an immutable snapshot upon impact, dispatches emergency SMS alerts containing real-time GPS coordinates via cellular GSM, and exposes an interactive web dashboard for real-time monitoring and crash analysis.

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │                    RASPBERRY PI 4B                     │
                                  │                                                        │
┌─────────────────────────┐  I²C  │  ┌──────────────────────┐    ┌──────────────────────┐  │
│  ADS1115 (16-bit ADC)   ├───────┼─▶│ Analog Sampling      ├───▶│ Hot Circular Buffer  │  │
│  • Ch0: MQ-3 Alcohol    │       │  │ Thread (10Hz)        │    │ (Rolling 15s Window) │  │
│  • Ch2: LM35 Temp       │       │  └──────────────────────┘    └──────────┬───────────┘  │
└─────────────────────────┘       │                                         │              │
                                  │  ┌──────────────────────┐               │ On Impact    │
┌─────────────────────────┐  UART │  │ NMEA GPS Thread      │               ▼              │
│  NEO-6M GPS Module      ├───────┼─▶│ (pynmea2 @ 9600baud) │    ┌──────────────────────┐  │
└─────────────────────────┘       │  └──────────────────────┘    │ Crash Dump Engine    │  │
                                  │                              │ (crash_<time>.json)  │  │
┌─────────────────────────┐  GPIO │  ┌──────────────────────┐    └──────────┬───────────┘  │
│  SW-420 Impact Sensor   ├───────┼─▶│ Vibration Window     │               │              │
└─────────────────────────┘       │  │ Accumulator (100Hz)  │──┐            │              │
                                  │  └──────────────────────┘  │            │              │
┌─────────────────────────┐  GPIO │  ┌──────────────────────┐  ▼            ▼              │
│  Hall Effect Speed      ├───────┼─▶│ RPM & Edge Counter   ├─▶┌──────────────────────┐    │
└─────────────────────────┘       │  └──────────────────────┘  │ Crash Detection      │    │
                                  │                            │ Engine               │    │
                                  │                            └────────────┬─────────┘    │
                                  │                                         │              │
┌─────────────────────────┐  GPIO │  ┌──────────────────────┐               ▼              │
│  Alarm Indicator LED    │◀──────┼──┤ Visual Alert Output  │    ┌──────────────────────┐  │
└─────────────────────────┘       │  └──────────────────────┘    │ Emergency Dispatcher │  │
                                  │                              │ • SMS with Maps Link │  │
┌─────────────────────────┐  UART │  ┌──────────────────────┐    │ • Local LED Warning  │  │
│  SIM800L GSM Module     │◀──────┼──┤ AT Command Driver    │◀───┴──────────────────────┘  │
└─────────────────────────┘       │  │ (/dev/ttyUSB0)       │                              │
                                  │  └──────────────────────┘                              │
                                  │                                                        │
                                  │  ┌──────────────────────────────────────────────────┐  │
                                  │  │   Flask Telemetry Server (http://0.0.0.0:5000)   │  │
                                  │  │   • Live Gauges & Sensors  • Crash Log Inspector │  │
                                  │  │   • OpenStreetMap Tracking • REST Data Endpoints │  │
                                  │  └──────────────────────────────────────────────────┘  │
                                  └────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Features

- **Multi-Sensor 10Hz Telemetry:** Concurrent threaded acquisition polls speed, impact, cabin temperature, alcohol vapor concentration, and satellite positioning.
- **Fail-Safe Dual-Storage Engine:**
  - **Cold Continuous Storage:** Appends every reading to `continuous_log.csv` for post-trip forensic review and regulatory auditing.
  - **Hot Circular Memory Buffer:** Maintains a rolling 15-second in-memory `deque` (150 frames) that instantly freezes and dumps to `crash_logs/crash_<timestamp>.json` upon crash detection.
- **Resilient Crash Detection Algorithm:**
  - Eliminates false positives from potholes and desk vibrations using a **200ms windowed hit accumulator** (threshold-calibrated) paired with sudden deceleration cross-checking ($>20\text{ km/h}$ drop).
- **Cabin Safety & Intoxication Guard:**
  - Continuous MQ-3 monitoring with programmable 30-sample warm-up filter and ADS1115 analog voltage evaluation to trigger real-time intoxication alerts.
- **Autonomous Emergency Response:**
  - Automatically dispatches SOS SMS messages over SIM800L containing coordinates, timestamp, and a direct Google Maps pinpoint URL (`https://maps.google.com/?q=LAT,LON`).
- **Interactive Web Dashboard:**
  - Built with Flask, vanilla CSS, and JavaScript. Delivers real-time tachometer/speed meters, live Leaflet / OpenStreetMap GPS tracking, live alert badges, and a full historical crash log inspector.
- **Hardware-Agnostic Mock & Simulation Support:**
  - Built-in simulation fallback allows full development, testing, and UI demonstration on any computer without requiring physical Raspberry Pi hardware.

---

## 🔌 Hardware & Pinout Specifications

| Component | Function | Interface / Protocol | Pi Pin # | GPIO (BCM) | Operating Voltage |
|:---|:---|:---|:---:|:---:|:---:|
| **ADS1115 ADC** | 16-Bit I²C Analog-to-Digital Converter | I²C (SDA / SCL @ `0x48`) | Pin 3, 5 | GPIO 2, GPIO 3 | 5.0V |
| **MQ-3 Gas Sensor** | Cabin Alcohol Vapor Detection | Analog $\to$ ADS1115 Ch0 (`A0`) | Pin 2, 6 | — | 5.0V (Heater) |
| **LM35 Sensor** | Cabin Temperature Sensor | Analog $\to$ ADS1115 Ch2 (`A2`) | Pin 4, 6 | — | 5.0V |
| **SW-420 Sensor** | Physical Shock & Vibration Impact | Digital GPIO (Pull-Down) | Pin 12 | GPIO 18 | 3.3V |
| **Hall Effect Sensor** | Wheel Rotation / Speed Calculation | Digital GPIO (Pull-Up) | Pin 15 | GPIO 22 | 5.0V / 3.3V |
| **Status Alarm LED** | Visual Alert / Fault Indicator | Digital Output (220Ω series) | Pin 11 | GPIO 17 | 3.3V |
| **NEO-6M GPS** | Satellite Positioning & Telematics | UART (`/dev/ttyAMA0`, 9600 baud) | Pin 8, 10 | GPIO 14, GPIO 15 | 5.0V (VCC) / 3.3V (Logic) |
| **SIM800L GSM** | Emergency Cellular SMS Alerts | UART via USB-TTL (`/dev/ttyUSB0`)| USB Port | — | External 4.0V–4.2V (2A burst) |

> 📖 *For complete schematics, breadboard diagrams, and common grounding rules, refer to [**PIN_CONFIGURATION.md**](PIN_CONFIGURATION.md).*

---

## 📁 Repository Structure

```
vehicle-blackbox/
├── .env.example             # Configuration template (phone number, port, modes)
├── .gitignore               # Clean ignore rules (caches, local logs, OS artifacts)
├── PIN_CONFIGURATION.md     # Comprehensive hardware wiring & pinout diagrams
├── README.md                # System documentation & technical overview
├── SETUP_GUIDE.md           # Step-by-step assembly and hardware setup walkthrough
├── Vehicle_Black_Box_Report.md # Formal technical research report and documentation
├── alert_dispatcher.py      # SIM800L GSM serial driver and emergency SMS composer
├── app.py                   # Flask server, HTML routes, and telemetry JSON REST API
├── blackbox.service         # Systemd service unit for automated background boot
├── calibration.json         # Persisted sensor calibration parameters & offsets
├── circular_buffer.py       # Thread-safe fixed-depth rolling memory buffer
├── crash_detection.py       # Multi-condition crash and alcohol threshold engine
├── data_logger.py           # Persistent filesystem JSON/CSV serialization
├── main.py                  # Primary entrypoint for Web Dashboard (CLI args & env support)
├── main_full.py             # Convenience launcher: Full deployment (GPS + GSM)
├── main_gps_only.py         # Convenience launcher: GPS-only deployment
├── requirements.txt         # Production Python dependencies
├── sensor_manager.py        # Central multi-threaded sensor polling and state manager
├── scripts/
│   └── bt_car.py            # Optional Bluetooth RC vehicle chassis motor controller
├── src/                     # Standalone Headless CLI Subsystem
│   ├── alerts.py            # Headless alert dispatch module
│   ├── buffer.py            # Headless circular buffer & CSV logger
│   ├── crash_logic.py       # Headless impact detection logic
│   ├── main.py              # Unified Headless CLI entrypoint
│   ├── main_full.py         # Headless CLI: Full mode wrapper
│   ├── main_gps_only.py     # Headless CLI: GPS-only wrapper
│   └── sensors.py           # Standalone sensor abstraction with mock fallbacks
├── static/
│   ├── css/style.css        # Responsive dashboard design system
│   └── js/dashboard.js      # Real-time dashboard telemetry updater & charts
├── templates/
│   ├── dashboard.html       # Primary telemetry interface
│   ├── log_detail.html      # Forensic crash log frame-by-frame inspector
│   └── logs.html            # Persisted incident log catalogue
└── tests/                   # Hardware diagnostics & interactive calibration suite
    ├── calibrate_temp.py    # Interactive terminal wizard for temperature calibration
    ├── test_ads1115.py      # I²C ADC multi-channel voltage verification
    ├── test_gps.py          # NEO-6M satellite fix & NMEA sentence stream test
    ├── test_gsm_sms.py      # SIM800L AT communication & SMS dispatch test
    ├── test_hall.py         # Hall effect pulse counting & RPM diagnostic
    ├── test_mq3.py          # MQ-3 analog voltage & alcohol threshold validation
    ├── test_temperature.py  # Temperature sensor reading & calibration test
    └── test_vibration.py    # SW-420 hit accumulator & vibration window tester
```

---

## 🚀 Getting Started

### Prerequisites

- **Hardware:** Raspberry Pi 4B (Raspberry Pi OS Lite or Desktop, 32-bit or 64-bit)
- **Software:** Python 3.9+ with `pip` and `python3-venv`
- **Interfaces:** I²C and Serial enabled via `raspi-config`:
  ```bash
  sudo raspi-config
  # Interface Options -> I2C -> Enable
  # Interface Options -> Serial Port -> Shell: NO, Hardware: YES
  ```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/krithikkrish/vehicle-blackbox.git
   cd vehicle-blackbox
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > *Note: On standard Raspberry Pi OS environments using system-managed Python packages, install using `--break-system-packages` if preferred:*
   > ```bash
   > pip3 install --break-system-packages -r requirements.txt
   > ```

### Environment Configuration

Copy the sample environment file to initialize local configuration:
```bash
cp .env.example .env
```

Edit `.env` to match your deployment parameters:
```ini
# Emergency recipient phone number with country code (e.g. India: +91)
EMERGENCY_PHONE=+919876543210

# Operating mode: FULL, GPS_ONLY, or GSM_ONLY
BLACKBOX_MODE=GPS_ONLY

# Web Dashboard HTTP port
PORT=5000
```

---

## 💻 Execution & Operating Modes

The system can run either as an **Interactive Web Dashboard** or as a **Lightweight Headless CLI**, supporting three tailored hardware profiles to accommodate available sensors and avoid UART serial contention.

### 1. Web Dashboard Mode (Default)

Launches background acquisition threads and serves the interactive Flask telemetry UI.

```bash
# 1. Run with default settings (reads BLACKBOX_MODE from .env, default: GPS_ONLY)
python3 main.py

# 2. Run specifically with GPS active (No GSM needed)
python3 main.py --mode gps
# Or via shortcut:
python3 main_gps_only.py

# 3. Run full production deployment (Both GPS & GSM active)
python3 main.py --mode full
# Or via shortcut:
python3 main_full.py

# 4. Run in GSM-only mode (No GPS attached, UART pins 14/15 free)
python3 main.py --mode gsm
```

Access the dashboard in your web browser at:
`http://localhost:5000` or `http://blackbox.local:5000`

---

### 2. Headless CLI Mode

Ideal for minimal installations, low memory overhead, or terminal-only debugging without running a web server.

```bash
# Run headless CLI with GPS tracking
python3 src/main.py --mode gps
# Or:
python3 src/main_gps_only.py

# Run headless CLI with full GPS + GSM SMS capabilities
python3 src/main.py --mode full
# Or:
python3 src/main_full.py
```

---

### Operational Modes Matrix

| Mode Flag | GPS Tracking (NEO-6M) | GSM Alerts (SIM800L) | UART Requirements | Primary Use Case |
|:---:|:---:|:---:|:---|:---|
| `--mode gps` / `GPS_ONLY` | **ACTIVE** (`/dev/ttyAMA0`) | **DISABLED** | Pins 14 & 15 | Lab testing with GPS satellite map & speed telemetry |
| `--mode gsm` / `GSM_ONLY` | **DISABLED** | **ACTIVE** (`/dev/ttyUSB0`) | USB-TTL Adapter | Cellular SMS dispatch testing without satellite lock |
| `--mode full` / `FULL` | **ACTIVE** (`/dev/ttyAMA0`) | **ACTIVE** (`/dev/ttyUSB0`) | Dedicated UART + USB | Full vehicle deployment with live map & SOS SMS dispatch |

---

## 📡 REST API Reference

The web dashboard polls these internal endpoints, which can also be utilized for external fleet management integration:

| Method | Endpoint | Description | Response Format |
|:---|:---|:---|:---|
| `GET` | `/` | Web Telemetry Dashboard Interface | HTML |
| `GET` | `/logs` | Historical Incident & Crash Log Explorer | HTML |
| `GET` | `/logs/<filename>` | Frame-by-Frame Forensic Analysis of an Incident | HTML |
| `GET` | `/api/live` | Current 10Hz telemetry snapshot across all sensors | JSON |
| `GET` | `/api/history` | Last 60 readings from in-memory circular buffer | JSON Array |
| `GET` | `/api/logs` | Metadata list of all persisted crash JSON files | JSON Array |
| `GET` | `/api/logs/<filename>` | Complete dump payload for a specific crash file | JSON Object |
| `POST` | `/api/reset_crash` | Reset latched crash alarm state and restore normal logging | JSON Object |

### Sample `/api/live` Response

```json
{
  "timestamp": "2026-11-17T10:14:00.123456",
  "mode": "FULL",
  "gps_lat": 12.840642,
  "gps_lon": 80.153418,
  "gps_speed_kmh": 42.5,
  "gps_fix": true,
  "hall_rpm": 480,
  "hall_speed_kmh": 41.8,
  "alcohol_voltage": 0.28,
  "alcohol_ppm": 4.5,
  "alcohol_alert": false,
  "temperature_c": 28.3,
  "vibration": false,
  "crash_detected": false,
  "system_status": "MONITORING"
}
```

---

## 🧪 Sensor Calibration & Diagnostics Suite

The `tests/` directory provides standalone diagnostic scripts to independently verify hardware wiring and calibrate thresholds before full deployment:

```bash
# 1. Calibrate vibration sensor & verify hit accumulator against desk knocks
python3 tests/test_vibration.py

# 2. Run the interactive Temperature Calibration Wizard
python3 tests/calibrate_temp.py

# 3. Verify ADS1115 16-bit ADC multi-channel voltage readings
python3 tests/test_ads1115.py

# 4. Check NEO-6M satellite lock and print live NMEA strings
python3 tests/test_gps.py

# 5. Test SIM800L AT commands and send a test SMS to emergency contact
python3 tests/test_gsm_sms.py

# 6. Verify Hall Effect pulse counting & non-contact magnetic RPM
python3 tests/test_hall.py

# 7. Test MQ-3 alcohol sensor analog sensitivity
python3 tests/test_mq3.py
```

---

## ⚙️ Production Deployment (systemd)

To ensure the black box runs reliably on system boot and auto-restarts upon failure, a systemd service unit [`blackbox.service`](blackbox.service) is included.

1. **Copy the service file to the systemd directory:**
   ```bash
   sudo cp blackbox.service /etc/systemd/system/
   ```

2. **Reload the systemd daemon:**
   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl enable blackbox.service
   sudo systemctl start blackbox.service
   ```

4. **Inspect live service logs:**
   ```bash
   journalctl -u blackbox.service -f
   ```

---

## 📚 Supplementary Documentation

- [**SETUP_GUIDE.md**](SETUP_GUIDE.md) — Step-by-step physical assembly, breadboard wiring, and sensor verification guide.
- [**PIN_CONFIGURATION.md**](PIN_CONFIGURATION.md) — Pinout tables, GPIO channel assignments, and hardware diagrams.
- [**Vehicle_Black_Box_Report.md**](Vehicle_Black_Box_Report.md) — Comprehensive technical report covering system requirements, literature review, and experimental evaluation.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
