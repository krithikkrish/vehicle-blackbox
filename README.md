# 🚗 Vehicle Black Box Prototype

> ⚠️ **Teammates:** If you are looking for instructions on how to wire the hardware and run the code, **[CLICK HERE TO READ THE SETUP GUIDE](SETUP_GUIDE.md)**!

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

## 🚀 Getting Started

For detailed wiring diagrams, pin connections, library installation, and step-by-step run instructions, see the **[Setup Guide](SETUP_GUIDE.md)**.

**Quick start** (if hardware is already wired):
```bash
git clone https://github.com/krithikkrish/vehicle-blackbox.git
cd vehicle-blackbox
pip3 install -r requirements.txt
python3 src/main.py
```

---

## 🗺️ What's Coming Next

- [ ] **Flask Web Dashboard** for remote live monitoring of the sensor data
