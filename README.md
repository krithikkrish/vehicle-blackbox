# 🚗 Smart Vehicle Black Box

> ⚠️ **Teammates:** If you are looking for instructions on how to wire the hardware and run the code, **[CLICK HERE TO READ THE SETUP GUIDE](SETUP_GUIDE.md)**!

---

## What is this project?

The **Smart Vehicle Black Box** is an embedded system that sits inside a vehicle and continuously records sensor data — just like a flight recorder (black box) in an airplane. It is built on a **Raspberry Pi 4B** running standard **Raspberry Pi OS (64-bit)**.

The system does three things:

1. **Records everything.** Every sensor reading (vibration, alcohol, GPS location, etc.) is logged to a CSV file on the SD card, 10 times per second. This creates a complete history of the trip.

2. **Detects crashes automatically.** If the vibration sensor picks up a sustained impact (not just a pothole), the system saves the last 15 seconds of data to a `crash_log.json` file and sends an **SOS SMS** with the vehicle's GPS coordinates to an emergency contact.

3. **Warns the driver.** If alcohol is detected in the cabin air, the system turns on a dashboard LED as a warning.

---

## Hardware Used

| Component | What it does |
|-----------|-------------|
| **Raspberry Pi 4B** | The brain of the system. Runs all the code. |
| **SW-420 Vibration Sensor** | Detects physical impact — used to identify crashes. Connected to GPIO 18 (Pin 12). |
| **MQ-3 Alcohol Sensor** | Detects alcohol in the cabin air — used for DUI prevention. Connected to GPIO 23 (Pin 16). |
| **Hall-Effect Module** | Detects magnets — can be used for door/tamper detection. Connected to GPIO 22 (Pin 15). |
| **NEO-6M GPS Module** | Tracks the vehicle's real-time location via satellite. Connected to UART (Pin 8 & 10). |
| **SIM800L GSM Module** | Sends emergency SMS messages. Requires a SIM card with SMS credit. Connected via USB. |
| **LED + 220Ω Resistor** | Dashboard warning light. Turns on when alcohol is detected or a crash happens. Connected to GPIO 17 (Pin 11). |

---

## How the Software Works

The main program (`main.py`) runs a loop that executes **10 times per second**. On each cycle:

1. **Read** — Polls all sensors (vibration, alcohol, hall-effect, GPS).
2. **Log** — Writes the reading to `continuous_log.csv` on the SD card.
3. **Buffer** — Stores the reading in a 15-second rolling memory buffer.
4. **Check** — Looks for crash conditions (sustained vibration for 3+ consecutive readings) and alcohol detection.
5. **Act** — If a crash is confirmed:
   - Dumps the 15-second buffer to `crash_log.json`
   - Turns on the LED
   - Sends an SOS SMS with GPS coordinates

### Why 3 consecutive readings?
A single vibration spike could be a speedbump or pothole. Requiring 3 consecutive vibration detections (0.3 seconds) filters out false alarms while still reacting fast enough for real crashes.

---

## Files in this Project

| File | What it does |
|------|-------------|
| `main.py` | **Start here.** The main program that runs the entire system. |
| `sensors.py` | Reads data from all the physical sensors. |
| `buffer.py` | Manages the 15-second memory buffer and the continuous CSV logger. |
| `crash_logic.py` | The crash detection algorithm (sustained vibration check). |
| `alerts.py` | Controls the LED and sends the SOS SMS via the GSM module. |
| `requirements.txt` | Python libraries needed to run the project. |
| `SETUP_GUIDE.md` | Step-by-step wiring and installation guide for the Raspberry Pi. |
| `tests/` | Individual test scripts to verify each sensor works on its own. |

---

## Data Files (auto-generated)

| File | When it's created | What's inside |
|------|-------------------|---------------|
| `continuous_log.csv` | As soon as `main.py` starts | Every single sensor reading, logged continuously. |
| `crash_log.json` | Only when a crash is detected | The last 15 seconds of sensor data before the crash. |

---

## Quick Start

```bash
git clone https://github.com/krithikkrish/vehicle-blackbox.git
cd vehicle-blackbox
pip3 install -r requirements.txt
python3 main.py
```

For full wiring instructions and detailed setup, see the **[Setup Guide](SETUP_GUIDE.md)**.

---

## What's Coming Next

- [ ] Flask Web Dashboard for remote live monitoring
- [ ] Speed calculation from GPS data
- [ ] Trip summary reports
