# 🚗 Vehicle Black Box Prototype

> ⚠️ **Teammates:** Check out the **[SETUP GUIDE](SETUP_GUIDE.md)** and the **[PIN CONFIGURATION GUIDE](PIN_CONFIGURATION.md)** for wiring and pinouts!

---

## 🌟 Overview & The Problem

Every year, thousands of accident victims die because help didn't arrive fast enough. Furthermore, **insurance companies** struggle with fraudulent claims and lack objective data to verify the exact circumstances of a crash. In many cases:

- The driver is unconscious and can't call for help.
- Bystanders don't know the exact location to report.
- There's no hard data to reconstruct what happened before the crash for insurance verification.

The **Smart Vehicle Black Box** is an embedded IoT prototype built on a **Raspberry Pi 4B** that solves these problems automatically by providing instant emergency alerts and immutable data logs.

---

## 🔬 Prototype Implementation Note

**Please note:** This project is currently a **hardware prototype** and is not deployed inside a real vehicle. To demonstrate functionality in a lab environment:
- We use **potentiometers** to simulate changes in vehicle speed.
- We use a **trigger button** and the SW-420 vibration sensor to simulate crash impacts.

Despite being a prototype, the core logic is production-ready. For example, our crash detection algorithm actively **filters out false positives** (like speedbumps or potholes) by requiring a sustained crash signal before triggering the emergency protocol.

---

## ⚙️ How It Works

The system runs a **10Hz sensor loop** (10 readings per second) that does four things on every tick:

```
┌─────────────┐
│  READ       │  ← Poll all sensors (vibration, alcohol, hall, GPS, speed simulation)
├─────────────┤
│  LOG        │  ← Write the reading to continuous_log.csv on the SD card
├─────────────┤
│  BUFFER     │  ← Push the reading into a 15-second circular memory buffer
├─────────────┤
│  EVALUATE   │  ← Check for crash conditions or alcohol detection
└──────┬──────┘
       │
       ▼  (If crash detected)
┌─────────────────────────────────────────────┐
│  1. Dump last 15 seconds → crash_log.json   │
│  2. Turn on LED alarm                       │
│  3. Send SOS SMS with GPS coordinates       │
└─────────────────────────────────────────────┘
```

### Crash Detection Logic (Eliminating False Positives)
A single vibration spike or button press is **not** treated as a crash. Instead, the system uses a **streak counter**: the crash signal must be sustained for **3 consecutive readings** (0.3 seconds) before the emergency protocol is triggered. This filters out false alarms while reacting within a fraction of a second to a real collision.

### Alcohol Detection
The MQ-3 gas sensor continuously samples the air. When the digital output goes HIGH (alcohol concentration above threshold), the system immediately lights up the dashboard LED as a warning.

---

## 🧩 Hardware Components

| Component | Purpose in Prototype |
|-----------|---------|
| **Raspberry Pi 4B** | Central processing unit. Runs the Python telemetry loop. |
| **SW-420 / Button** | Detects physical impacts and sustained vibration during simulated crashes. |
| **Potentiometer** | Simulates vehicle speed data for telemetry logging. |
| **MQ-3** | Monitors cabin air for alcohol. Has an adjustable sensitivity knob. |
| **NEO-6M** | Provides real-time latitude/longitude coordinates via satellite. |
| **SIM800L** | Sends emergency SMS messages over the cellular network. |
| **LED + 220Ω Resistor** | Dashboard warning light — turns on for alcohol alerts and crash events. |

---

## 💾 Data Storage for Insurance Verification

The system uses a **dual-storage strategy** to ensure data is never lost:

| Storage | File | Format | When | Purpose |
|---------|------|--------|------|---------|
| **Cold Storage** | `continuous_log.csv` | CSV | Every tick (10/sec) | Full trip log. Every sensor reading ever recorded. Crucial for insurance audits. |
| **Hot Buffer** | In-memory (`deque`) | Python objects | Every tick (10/sec) | Rolling 15-second window. Automatically discards older readings. |
| **Crash Dump** | `crash_log.json` | JSON | On crash event only | Snapshot of the hot buffer at the moment of crash. Contains the critical 15 seconds before impact. |

---

## 🚀 Ready-to-Run Code Versions

The repository provides **3 distinct, fully ready-to-run versions** tailored for modular lab testing and avoiding hardware UART serial contention:

### 1️⃣ Version 1: GSM Only (No GPS) — Default `main.py`
Ideal when you do not have the GPS module connected or want UART pins 14/15 completely free.
- **GSM Alerts**: **ACTIVE** (Dispatches emergency SOS SMS on crash/impact via SIM800L or simulation).
- **GPS Receiver**: **DISABLED** (Serial thread omitted, no UART port lock).
- **Run Web Dashboard**:
  ```bash
  python3 main.py
  ```
- **Run CLI**:
  ```bash
  python3 src/main.py
  ```
- **Web Dashboard**: `http://blackbox.local:5000`

---

### 2️⃣ Version 2: GPS Only (No GSM) — `main_gps_only.py`
Ideal when you want satellite tracking, live OpenStreetMap visualization, and speed calculation without a SIM module.
- **GPS Receiver**: **ACTIVE** (NEO-6M NMEA parser on `/dev/ttyAMA0` @ 9600 baud).
- **GSM Alerts**: **DISABLED** (No SMS attempts, bypassing port conflicts).
- **Run Web Dashboard**:
  ```bash
  python3 main_gps_only.py
  ```
- **Run CLI**:
  ```bash
  python3 src/main_gps_only.py
  ```
- **Web Dashboard**: `http://blackbox.local:5000`

---

### 3️⃣ Version 3: Both GPS & GSM Active — `main_full.py`
Full production-ready blackbox deployment with all sensors and modules operating simultaneously.
- **GPS Receiver**: **ACTIVE** (NEO-6M on `/dev/ttyAMA0` UART).
- **GSM Alerts**: **ACTIVE** (SIM800L on `/dev/ttyUSB0` with live GPS location link in SOS SMS).
- **Run Web Dashboard**:
  ```bash
  python3 main_full.py
  ```
- **Run CLI**:
  ```bash
  python3 src/main_full.py
  ```
- **Web Dashboard**: `http://blackbox.local:5000`

---

## 🛠️ Hardware Wiring & Pin Configuration

For detailed pin connections, see **[PIN_CONFIGURATION.md](PIN_CONFIGURATION.md)**:
- **ADS1115 ADC**: I2C (SDA: GPIO 2 / Pin 3, SCL: GPIO 3 / Pin 5, Addr `0x48`, 5V)
- **MQ-3 Alcohol**: Analog into ADS1115 Channel A0 (`ADS.P0`)
- **LM35 Temperature**: Analog into ADS1115 Channel A2 (`ADS.P2`)
- **SW-420 Vibration**: Digital into GPIO 18 (Pin 12)
- **Status / Alert LED**: GPIO 17 (Pin 11) with 220Ω resistor
- **NEO-6M GPS**: UART TX/RX on GPIO 14 & 15 (`/dev/ttyAMA0`)
- **SIM800L GSM**: USB-to-TTL on `/dev/ttyUSB0` (or `/dev/ttyAMA0` in GSM-only mode)
- **Hall Effect Speed**: GPIO 22 (Pin 15)

