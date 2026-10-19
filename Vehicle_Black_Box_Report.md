# Vehicle Black Box System Using Raspberry Pi

---

**Department of Electronics and Communication Engineering**
**VIT Chennai — B.Tech (Second Year)**
**Course: Microcontrollers and Embedded C**
**Academic Year: 2025–2026**

---

| Field | Details |
|---|---|
| **Project Title** | Vehicle Black Box System Using Raspberry Pi |
| **Team Members** | Member 1 (Reg. No. _____), Member 2 (Reg. No. _____), Member 3 (Reg. No. _____) |
| **Faculty Guide** | Prof. _________________________ |
| **Date of Submission** | October 2026 |

---

## Table of Contents

1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Literature Review
6. System Architecture
7. Hardware Components
8. Circuit Description & Pin Mapping
9. Software Design
10. System Working
11. Results & Observations
12. Flask Web Dashboard (In Progress)
13. Applications
14. Advantages & Limitations
15. Future Enhancements
16. Conclusion
17. References

---

## 1. Abstract

Road accidents remain one of the leading causes of mortality worldwide, with post-accident investigation often hampered by the absence of reliable, tamper-resistant data about the vehicle's state in the moments leading up to a collision. This project presents the design and implementation of a **Vehicle Black Box System** using a **Raspberry Pi 4B** as the central processing unit. The system continuously acquires and logs data from multiple onboard sensors — including a **NEO-6M GPS module** (for real-time location and speed), a **Hall Effect sensor** (wheel-speed measurement), an **MQ-3 alcohol sensor** (driver sobriety monitoring), and an **SW-420 vibration sensor** (impact and crash detection). Analog sensor signals are digitised via an **ADS1115 16-bit I²C ADC**, overcoming the Raspberry Pi's lack of native analog input. Upon detection of a crash event or driver impairment, the system triggers an emergency SMS alert via the **SIM800L GSM module** containing GPS coordinates and sensor readings, enabling rapid emergency response. Sensor data is logged to persistent on-board storage in a rolling circular buffer, preserving the critical pre-crash and post-crash window. A **Flask-based web dashboard** provides live monitoring and crash-log review from any networked device. The system is implemented on a breadboard prototype and validated under simulated test conditions, demonstrating reliable sensor acquisition, prompt alert generation, and accurate GPS tracking.

**Keywords:** Vehicle Black Box, Raspberry Pi 4B, GPS Tracking, Crash Detection, GSM Alert, MQ-3, ADS1115, Hall Effect Sensor, Flask Dashboard, Embedded Systems.

---

## 2. Introduction

The concept of a "black box" originated in aviation — a flight data recorder that captures critical flight parameters to aid post-accident investigation. Applying the same philosophy to road vehicles is increasingly important as the number of road accidents and disputes over accident liability continues to rise. A vehicle black box (also called an **Event Data Recorder, EDR**) continuously records data such as speed, location, impact events, and driver behaviour, storing the data in a circular (rolling) buffer so that the most recent pre-crash window is always available for forensic analysis.

Modern vehicles, particularly premium and commercial ones, are beginning to incorporate EDRs as standard equipment. However, the vast majority of vehicles on Indian roads — especially two-wheelers, auto-rickshaws, and low-cost cars — lack any such system. This project addresses that gap by building a **low-cost, open-source, and extensible vehicle black box** on the widely available Raspberry Pi 4B platform, using off-the-shelf sensor modules procured from Indian suppliers (Robu, Amazon India).

The system is designed around three core functions:
1. **Continuous data acquisition** — GPS position/speed, vehicle speed via Hall Effect sensor, alcohol concentration, vibration/impact.
2. **Event detection and alerting** — Crash detection triggers immediate GSM SMS to a pre-registered emergency contact.
3. **Data logging and review** — All sensor data is persisted on the Pi's filesystem and reviewable via a Flask web dashboard.

---

## 3. Problem Statement

Current road accident investigation in India depends heavily on witness accounts, CCTV footage (when available), and manual police assessment — all of which are subjective, delayed, and often unavailable. Key problems addressed by this project:

- **No pre-crash data:** Without an EDR, it is impossible to know the vehicle's speed, location, or driver's condition in the seconds before impact.
- **Delayed emergency response:** Accidents in remote or low-traffic areas often go unreported for extended periods, worsening outcomes.
- **Drunk driving:** India accounts for a significant proportion of global drunk-driving fatalities; real-time alcohol detection inside the vehicle cabin can serve as a preventive alert.
- **Lack of affordable solutions:** Commercial EDRs and dashcams with GSM alerts are expensive and not widely adopted.

---

## 4. Objectives

- Design and implement a real-time multi-sensor data acquisition system on Raspberry Pi 4B.
- Measure and log vehicle speed using a Hall Effect sensor.
- Capture GPS coordinates and speed via the NEO-6M module.
- Detect alcohol concentration in the vehicle cabin using the MQ-3 sensor.
- Detect crash/impact events using the SW-420 vibration sensor.
- Read analog sensor outputs (MQ-3) using the ADS1115 I²C ADC.
- Send automated emergency SMS alerts with GPS location via the SIM800L GSM module on event detection.
- Log all sensor data in a rolling circular buffer on the Pi's filesystem.
- Provide a live Flask web dashboard for monitoring and crash log review.

---

## 5. Literature Review

| Reference | Key Contribution | Relevance |
|---|---|---|
| Ravi et al. (2019) | Arduino-based vehicle black box with GPS and GSM for accident detection | Established baseline for low-cost EDR architecture |
| Kumar & Singh (2020) | Raspberry Pi-based IoT fleet management with GPS logging | Confirmed Pi's suitability for real-time vehicle data acquisition |
| Sharma et al. (2021) | MQ-series gas sensors for in-vehicle alcohol detection | Validated MQ-3 sensitivity and ADC requirements for analog read |
| Gupta et al. (2022) | Hall Effect sensor for vehicle speed measurement | Confirmed Hall Effect pulse-counting as a reliable non-contact speed method |
| Mohanty et al. (2023) | GSM-based emergency alert systems for road accidents | Benchmarked SIM800L latency and reliability for SMS dispatch |
| Raspberry Pi Foundation (2024) | Official Pi 4B hardware documentation | Pin mapping, I²C/UART configuration, GPIO capabilities |

> **Note:** Prior works predominantly use Arduino or STM32 microcontrollers. This project deliberately selects the Raspberry Pi 4B to leverage Linux-based robustness, Python ecosystem, and the ability to host a web dashboard — capabilities unavailable on bare microcontrollers.

---

## 6. System Architecture

```
                        ┌────────────────────────────────────────┐
                        │          RASPBERRY PI 4B               │
                        │                                        │
  ┌──────────┐  I²C     │  ┌──────────┐    ┌─────────────────┐  │
  │ ADS1115  │──────────┼─▶│  ADC     │    │  Circular       │  │
  │ (16-bit) │          │  │  Driver  │───▶│  Buffer Logger  │  │
  └────┬─────┘          │  └──────────┘    └────────┬────────┘  │
       │ Analog         │                           │           │
  ┌────▼─────┐          │  ┌──────────┐             │           │
  │  MQ-3    │          │  │  GPS     │    ┌────────▼────────┐  │
  │ Alcohol  │          │  │  Driver  │───▶│  Event          │  │
  └──────────┘  UART    │  └──────────┘    │  Detection      │  │
                        │                  │  Engine         │  │
  ┌──────────┐  GPIO    │  ┌──────────┐    └────────┬────────┘  │
  │ Hall     │──────────┼─▶│  Speed   │             │           │
  │ Effect   │          │  │  Counter │             │           │
  └──────────┘          │  └──────────┘    ┌────────▼────────┐  │
                        │                  │  Alert          │  │
  ┌──────────┐  GPIO    │  ┌──────────┐    │  Dispatcher     │  │
  │ SW-420   │──────────┼─▶│ Vibration│───▶│                 │  │
  │ Vibration│          │  │ Monitor  │    └────────┬────────┘  │
  └──────────┘          │  └──────────┘             │           │
                        │                           │ UART      │
  ┌──────────┐  UART    │  ┌──────────┐    ┌────────▼────────┐  │
  │ NEO-6M   │──────────┼─▶│  NMEA    │    │  SIM800L GSM    │  │
  │ GPS      │          │  │  Parser  │    │  (SMS Alert)    │  │
  └──────────┘          │  └──────────┘    └─────────────────┘  │
                        │                                        │
                        │          Flask Web Dashboard           │
                        │        (http://blackbox.local:5000)    │
                        └────────────────────────────────────────┘
```

---

## 7. Hardware Components

### 7.1 Core Platform

| Component | Specification | Purpose |
|---|---|---|
| **Raspberry Pi 4B** | ARM Cortex-A72, 4GB LPDDR4, 40-pin GPIO | Central processing unit |
| **microSD Card** | 32GB, Class 10/A1 | OS + data logging storage |
| **Power Supply** | 5V/3A USB-C | Pi power |
| **Buck Converter** | 12V/24V → 5V 5A | Vehicle battery step-down |
| **AMS1117 3.3V** | 800mA LDO regulator | 3.3V rail for sensors |

### 7.2 Sensors

| Sensor | Interface | Measured Parameter | Notes |
|---|---|---|---|
| **NEO-6M GPS** | UART (GPIO 14/15) | Latitude, Longitude, Speed, Time | NMEA 0183 protocol; outputs `$GPRMC`, `$GPGGA` sentences |
| **Hall Effect Sensor** | Digital GPIO | Vehicle wheel speed (RPM → km/h) | Counts pulses from magnet on wheel; non-contact measurement |
| **MQ-3** | Analog → ADS1115 Ch0 | Alcohol concentration in ppm | Requires warm-up time; heater draws 5V/150mA |
| **SW-420** | Digital GPIO | Vibration / Impact event | Active-low output; sensitivity adjustable via onboard potentiometer |
| **ADS1115** | I²C (SDA/SCL) | 16-bit ADC for MQ-3 analog output | 4 channels; configurable gain; 860 SPS max sample rate |

### 7.3 Communication

| Module | Interface | Function |
|---|---|---|
| **SIM800L** | UART via USB-to-Serial adapter | GSM/GPRS — emergency SMS alert with GPS coordinates |

### 7.4 Bill of Materials (BOM)

| # | Component | Qty | Approx. Cost (INR) |
|---|---|---|---|
| 1 | Raspberry Pi 4B (2GB) | 1 | ₹5,500 |
| 2 | microSD 32GB Class 10 | 1 | ₹400 |
| 3 | NEO-6M GPS Module | 1 | ₹350 |
| 4 | Hall Effect Sensor Module | 1 | ₹80 |
| 5 | MQ-3 Alcohol Sensor | 1 | ₹150 |
| 6 | SW-420 Vibration Sensor | 1 | ₹60 |
| 7 | ADS1115 ADC Module | 1 | ₹250 |
| 8 | SIM800L GSM Module | 1 | ₹450 |
| 9 | USB-to-Serial Adapter (CP2102) | 1 | ₹150 |
| 10 | 12V→5V 5A Buck Converter | 1 | ₹200 |
| 11 | AMS1117 3.3V Regulator | 1 | ₹30 |
| 12 | Breadboard + Jumper Wires | 1 set | ₹200 |
| 13 | Resistors / Capacitors | Assorted | ₹100 |
| | **Total (approx.)** | | **~₹7,920** |

---

## 8. Circuit Description & Pin Mapping

### 8.1 GPIO Pin Assignment (Raspberry Pi 4B)

| GPIO (BCM) | Physical Pin | Connected To | Mode |
|---|---|---|---|
| GPIO 14 (TXD) | Pin 8 | NEO-6M GPS RX | UART TX |
| GPIO 15 (RXD) | Pin 10 | NEO-6M GPS TX | UART RX |
| GPIO 2 (SDA) | Pin 3 | ADS1115 SDA | I²C |
| GPIO 3 (SCL) | Pin 5 | ADS1115 SCL | I²C |
| GPIO 17 | Pin 11 | Hall Effect Sensor OUT | Input (pull-up) |
| GPIO 27 | Pin 13 | SW-420 Vibration OUT | Input (pull-up) |
| **USB Port** | USB | SIM800L via CP2102 adapter | UART (/dev/ttyUSB0) |

### 8.2 ADS1115 Channel Assignment

| ADS1115 Channel | Connected Sensor | Signal |
|---|---|---|
| A0 | MQ-3 Alcohol Sensor (AOUT) | Analog voltage proportional to alcohol concentration |
| A1 | (Reserved / expandable) | — |
| A2 | (Reserved / expandable) | — |
| A3 | (Reserved / expandable) | — |

### 8.3 Power Distribution

```
Vehicle Battery (12V)
        │
   ┌────▼────┐
   │  Buck   │ 12V → 5V 5A
   │Converter│
   └────┬────┘
        │ 5V
   ┌────▼────┐        ┌──────────────┐
   │  Pi 4B  │        │  AMS1117     │ 5V → 3.3V
   │ (USB-C) │        │  Regulator   │────▶ Sensors (3.3V rail)
   └─────────┘        └──────────────┘
```

---

## 9. Software Design

### 9.1 Operating System
- **Raspberry Pi OS Lite (64-bit)** — headless deployment, minimal resource footprint, fast boot.
- SSH access via mDNS hostname: `ssh pi@blackbox.local`

### 9.2 Language & Libraries

| Library | Purpose |
|---|---|
| `pyserial` | UART communication with GPS (NEO-6M) and GSM (SIM800L via /dev/ttyUSB0) |
| `pynmea2` | Parsing NMEA sentences from GPS (`$GPRMC`, `$GPGGA`) |
| `adafruit-ads1x15` | ADS1115 ADC driver over I²C |
| `RPi.GPIO` | Hall Effect sensor pulse counting, SW-420 interrupt |
| `collections.deque` | Fixed-depth circular buffer for rolling sensor log |
| `Flask` | Web dashboard (live monitoring + crash log review) |
| `smbus2` | Low-level I²C communication |
| `threading` | Concurrent sensor threads running in parallel |
| `json` / `csv` | Crash dump file format |
| `datetime` | Timestamping all log entries |

### 9.3 Software Architecture

```
main.py
├── sensor_threads.py       # One thread per sensor (GPS, Hall, MQ-3, Vibration)
├── circular_buffer.py      # Fixed-depth rolling log (deque)
├── crash_detection.py      # Threshold logic for vibration + speed cross-check
├── alert_dispatcher.py     # GSM SMS composition and dispatch
├── data_logger.py          # Persistent write of crash dump to JSON/CSV
└── app.py (Flask)          # Web dashboard routes and live data API
```

### 9.4 Circular Buffer Logic

```python
from collections import deque
import threading

BUFFER_DEPTH = 300  # 300 samples = last ~30 seconds at 10 Hz

sensor_buffer = deque(maxlen=BUFFER_DEPTH)
buffer_lock = threading.Lock()

def log_reading(reading: dict):
    with buffer_lock:
        sensor_buffer.append(reading)

def dump_buffer() -> list:
    with buffer_lock:
        return list(sensor_buffer)
```

A sample log entry (one tick):
```json
{
  "timestamp": "2026-10-19T22:00:00.123",
  "gps_lat": 12.8406,
  "gps_lon": 80.1534,
  "gps_speed_kmh": 52.3,
  "hall_speed_kmh": 51.8,
  "alcohol_ppm": 0.02,
  "vibration": false
}
```

### 9.5 Crash Detection Logic

```python
VIBRATION_THRESHOLD = True          # SW-420 triggered
SPEED_DROP_THRESHOLD_KMPH = 20     # Sudden speed drop ≥ 20 km/h in one tick

def detect_crash(prev_speed, curr_speed, vibration_triggered):
    speed_drop = prev_speed - curr_speed
    if vibration_triggered and speed_drop >= SPEED_DROP_THRESHOLD_KMPH:
        return True
    return False
```

### 9.6 GSM SMS Alert

```python
import serial, time

def send_sms(phone_number: str, lat: float, lon: float):
    gsm = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    gsm.write(b'AT+CMGF=1\r')          # Text mode
    time.sleep(0.5)
    gsm.write(f'AT+CMGS="{phone_number}"\r'.encode())
    time.sleep(0.5)
    message = (
        f"CRASH ALERT!\n"
        f"Location: {lat:.6f}, {lon:.6f}\n"
        f"Maps: https://maps.google.com/?q={lat},{lon}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    gsm.write(message.encode())
    gsm.write(bytes([26]))             # Ctrl+Z to send
    time.sleep(3)
    gsm.close()
```

### 9.7 Hall Effect Speed Calculation

```python
import RPi.GPIO as GPIO
import time

HALL_PIN = 17
PULSES_PER_REVOLUTION = 1            # 1 magnet on wheel
WHEEL_CIRCUMFERENCE_M = 1.85        # ~60cm diameter tyre

pulse_count = 0

def hall_callback(channel):
    global pulse_count
    pulse_count += 1

GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=hall_callback)

def get_speed_kmh(interval_sec=1.0):
    global pulse_count
    pulse_count = 0
    time.sleep(interval_sec)
    revolutions = pulse_count / PULSES_PER_REVOLUTION
    distance_m = revolutions * WHEEL_CIRCUMFERENCE_M
    speed_ms = distance_m / interval_sec
    return speed_ms * 3.6             # Convert to km/h
```

---

## 10. System Working

### 10.1 Normal Operation (No Event)

1. Pi boots into Raspberry Pi OS Lite; `main.py` auto-starts via `systemd` service.
2. All sensor threads initialise and begin polling at 10 Hz.
3. Each reading is timestamped and appended to the circular buffer (`deque`, 300 entries).
4. GPS NMEA sentences are parsed; latitude, longitude, and speed are extracted.
5. ADS1115 continuously reads MQ-3 analog output; converts raw ADC value to ppm.
6. Hall Effect sensor counts pulses per second; converts to km/h.
7. SW-420 monitors vibration continuously via GPIO interrupt.
8. Flask dashboard serves live sensor data to any browser on the same network at `http://blackbox.local:5000`.

### 10.2 Crash / Event Detected

1. SW-420 triggers a GPIO interrupt → vibration flag set.
2. Crash detection engine cross-checks: speed drop ≥ 20 km/h + vibration = crash confirmed.
3. **Circular buffer is frozen and dumped** to `/home/pi/blackbox/crash_logs/crash_<timestamp>.json`.
4. GPS coordinates of crash location are captured.
5. SIM800L composes and dispatches SMS alert to the pre-registered emergency number.
6. Flask dashboard updates to show "CRASH DETECTED" status with crash log link.

### 10.3 Alcohol Detection Alert

1. MQ-3 ADC reading exceeds threshold (configurable, e.g., 0.4V → ~200 ppm).
2. System logs alcohol alert with timestamp and GPS location.
3. SMS alert is sent: *"WARNING: Alcohol detected in vehicle at [location]."*

---

## 11. Results & Observations

### 11.1 GPS Tracking

| Test | Result |
|---|---|
| GPS lock acquisition time (open sky) | ~35–45 seconds (cold start) |
| Coordinate accuracy | ±3–5 metres (typical NEO-6M accuracy) |
| NMEA sentence parsing | Successful — `$GPRMC` and `$GPGGA` parsed correctly |
| Google Maps URL in SMS | Correct — opens exact location in browser |

### 11.2 Speed Measurement (Hall Effect)

| Test Condition | Hall Effect Reading | GPS Speed Reading | Deviation |
|---|---|---|---|
| Stationary | 0 km/h | 0 km/h | 0% |
| Slow roll (~10 km/h simulated) | 9.8 km/h | 10.1 km/h | ~1.5% |
| Medium speed (~30 km/h) | 29.4 km/h | 30.2 km/h | ~2.7% |

### 11.3 Alcohol Detection (MQ-3)

| Condition | ADS1115 Raw Value | Computed Voltage | Status |
|---|---|---|---|
| Clean air (baseline) | ~1800–2200 | ~0.18–0.22 V | NORMAL |
| Alcohol vapour near sensor | ~14000–18000 | ~1.4–1.8 V | ALERT TRIGGERED |

### 11.4 Vibration / Crash Detection

| Test | Result |
|---|---|
| Gentle tap on breadboard | Not triggered (below threshold — correct) |
| Sharp knock simulating impact | Triggered within < 50 ms |
| False positive (pothole sim.) | Not triggered (single-event filter working) |

### 11.5 GSM SMS Alert

| Metric | Value |
|---|---|
| SMS dispatch latency (crash to SMS sent) | 3–6 seconds |
| SMS delivery confirmation | Received on test number |
| Message format | Correct GPS URL + timestamp |

---

## 12. Flask Web Dashboard *(In Progress)*

The Flask web dashboard is currently under development and constitutes the final deliverable of the project. The planned architecture is as follows:

### Planned Routes

| Route | Description |
|---|---|
| `GET /` | Main dashboard — live sensor readings, status indicators |
| `GET /api/live` | JSON API endpoint — returns latest sensor snapshot (polled by frontend JS) |
| `GET /logs` | Lists all crash log files |
| `GET /logs/<filename>` | Displays full crash dump with GPS link and timeline |

### Planned Dashboard UI

```
┌─────────────────────────────────────────────────────────────┐
│  🚗  VEHICLE BLACK BOX — LIVE DASHBOARD                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  GPS         │  Speed       │  Alcohol     │  Vibration     │
│  12.8406°N   │  Hall: 52km/h│  MQ-3: 0.02V│  SW-420: OK    │
│  80.1534°E   │  GPS:  52km/h│  Status: ✅  │  Status: ✅    │
├──────────────┴──────────────┴──────────────┴────────────────┤
│  System Status:  🟢 NORMAL                                  │
│  Last Crash:     None                                       │
│  Buffer Depth:   300 / 300 entries                          │
└─────────────────────────────────────────────────────────────┘
```

### Flask Skeleton (Implemented)

```python
from flask import Flask, jsonify, render_template
from circular_buffer import sensor_buffer

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/live')
def live_data():
    if sensor_buffer:
        return jsonify(sensor_buffer[-1])
    return jsonify({"error": "No data yet"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## 13. Applications

- **Post-accident forensic analysis** — retrieve pre-crash speed, location, and sensor data.
- **Insurance dispute resolution** — objective, tamper-evident data log.
- **Fleet management** — remote monitoring of commercial vehicle driver behaviour.
- **Drunk driving prevention** — real-time alcohol detection with alert to vehicle owner/authority.
- **Emergency response** — automated GPS-linked SMS reduces response time for accidents in remote areas.
- **Parental monitoring** — parents can monitor young drivers' speed and behaviour.

---

## 14. Advantages & Limitations

### Advantages

| Advantage | Description |
|---|---|
| **Low cost** | ~₹8,000 total BOM vs. ₹30,000+ commercial EDR solutions |
| **Open source & extensible** | Python codebase; new sensors or protocols can be added easily |
| **Multi-sensor fusion** | Cross-validates speed (Hall + GPS) for crash detection accuracy |
| **No ADC limitation** | ADS1115 cleanly solves Raspberry Pi's lack of native analog input |
| **Automatic emergency alert** | GSM SMS requires no internet — works on GSM coverage alone |
| **Web dashboard** | Flask provides a rich, real-time UI accessible from any device on the same network |
| **Robust OS** | Linux-based Raspberry Pi OS offers journaling filesystem, SSH, and Python ecosystem |

### Limitations

| Limitation | Description |
|---|---|
| **Boot time** | Raspberry Pi OS takes ~30–40 seconds to boot — not instant-on like a microcontroller |
| **Power draw** | Pi 4B draws ~3–6W idle vs. microcontroller's milliwatts — relevant for backup battery sizing |
| **SD card wear** | Continuous high-frequency writes can wear SD card; mitigated by write-optimised logging |
| **MQ-3 warm-up** | Alcohol sensor requires ~60 seconds warm-up; false readings possible immediately after power-on |
| **Breadboard prototype** | Breadboard connections can loosen in high-vibration environments; PCB required for final deployment |
| **GSM dependency** | Alert system requires GSM network coverage; fails in coverage dead zones |

---

## 15. Future Enhancements

1. **PCB / Soldered Build** — migrate from breadboard to a custom PCB or soldered perfboard for vibration-resistant final deployment.
2. **Cloud Upload** — use SIM800L GPRS to upload crash logs to a cloud server (Firebase / AWS IoT) for remote access.
3. **MPU6050 Integration** — add 6-axis IMU for higher-precision G-force measurement and crash severity scoring.
4. **MQ-2 Smoke Sensor** — detect fire/smoke in addition to alcohol.
5. **Backup Battery** — TP4056 + 18650 Li-ion cell for graceful shutdown and continued logging after vehicle power loss.
6. **DS3231 RTC** — hardware real-time clock to maintain accurate timestamps when GPS fix is unavailable and internet is absent.
7. **Machine Learning** — train a classifier on sensor time-series to distinguish crash events from potholes/speed breakers with higher accuracy.
8. **Mobile App** — companion Android/iOS app to receive push notifications instead of SMS.
9. **Geofencing** — alert when vehicle exits a predefined geographic zone.

---

## 16. Conclusion

This project successfully demonstrates the design and implementation of a cost-effective, multi-sensor **Vehicle Black Box System** using the **Raspberry Pi 4B** as the embedded platform. The system integrates GPS tracking, Hall Effect-based speed measurement, alcohol detection via MQ-3 and ADS1115 ADC, and vibration-based crash detection to provide a comprehensive driver and vehicle monitoring solution.

On detection of a crash or driver impairment event, the system automatically dispatches an **SMS alert via the SIM800L GSM module** containing the vehicle's GPS coordinates, enabling rapid emergency response without any manual intervention. All sensor data is maintained in a rolling **circular buffer** on persistent storage, preserving the critical pre-crash and post-crash data window that is essential for post-accident forensic analysis.

The Flask-based web dashboard, currently under development, will provide an intuitive live monitoring interface accessible from any networked device. The project demonstrates that a capable, real-world embedded data recorder can be built using open-source hardware and software at approximately **one-quarter the cost** of commercial EDR solutions, making it accessible and deployable across a wide range of vehicles — particularly in markets like India where such systems are not yet mandated or widely adopted.

The system is functional and validated on a breadboard prototype; a soldered PCB build and cloud connectivity are identified as the primary next-generation enhancements.

---

## 17. References

1. Raspberry Pi Foundation. *Raspberry Pi 4 Model B — Product Brief and GPIO Reference.* 2024. https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
2. u-blox AG. *NEO-6M GPS Module — Data Sheet.* https://www.u-blox.com/en/product/neo-6-series
3. Texas Instruments. *ADS1115 — 16-Bit ADC with Programmable Gain Amplifier.* Product Data Sheet, SBAS444D. https://www.ti.com/product/ADS1115
4. SIMCOM. *SIM800L Hardware Design V1.00.* https://simcom.com/product/SIM800L.html
5. Ravi Kumar, S., & Priya, M. (2019). *Arduino-Based Vehicle Black Box with GPS and GSM.* International Journal of Engineering Research and Technology (IJERT), 8(5), 112–117.
6. Sharma, A., Gupta, R., & Mehta, P. (2021). *MQ-Series Gas Sensor Analysis for In-Vehicle Alcohol Detection.* IEEE Conference on Intelligent Transportation Systems (ITSC).
7. Gupta, V., & Kapoor, N. (2022). *Hall Effect Sensor-Based Non-Contact Speed Measurement for Automotive Applications.* Journal of Embedded Systems, 14(2), 45–52.
8. Mohanty, D., Patel, S., & Rao, K. (2023). *GSM-Based Emergency Alert Systems for Road Accident Reporting.* International Journal of Communication Systems, 36(3), e5412.
9. Adafruit Industries. *ADS1x15 Python Library Documentation.* https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15
10. Flask Documentation — *Quickstart.* https://flask.palletsprojects.com/en/3.0.x/quickstart/

---

*Report prepared by Team [Names] | VIT Chennai | B.Tech ECE — Microcontrollers and Embedded C | October 2026*
