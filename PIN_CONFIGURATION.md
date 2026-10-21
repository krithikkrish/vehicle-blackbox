# 📌 Car Blackbox Data Logger — Pin Configuration & Wiring Guide

> **Project:** Vehicle Blackbox Data Logger (Raspberry Pi 4)  
> **Status:** Verified & Code-Aligned  
> **ADC Converter:** ADS1115 (16-bit I2C, Address `0x48`)  

---

## 1. 📋 Master Raspberry Pi 4 Pin-by-Pin Table

| Pi Pin # | Pin Function | Connected Device & Wire | Signal / Voltage | Purpose |
|:---:|:---:|---|:---:|---|
| **Pin 1** | **3.3V Power** | **SW-420 VCC** (Red) | 3.3V DC | Low-power digital sensor power rail |
| **Pin 2** | **5V Power** | **MQ-3 VCC**, **SIM VCC**, **ADS1115 VDD** | 5V DC | High-power analog & sensor power rail |
| **Pin 3** | **GPIO 2 (SDA)** | **ADS1115 SDA** | 3.3V I2C Data | ADC I2C communication (Address `0x48`) |
| **Pin 4** | **5V Power** | **GPS VCC**, **Temperature Sensor VCC** | 5V DC | Sensor power rail |
| **Pin 5** | **GPIO 3 (SCL)** | **ADS1115 SCL** | 3.3V I2C Clock | ADC I2C clock line |
| **Pin 6** | **GND** | **MQ-3 GND**, **Temp GND**, **SW-420 GND** | 0V | Common Ground return |
| **Pin 8** | **GPIO 14 (UART TX)** | **GPS RX** (Green) / **SIM RX** | 3.3V Serial TX | Serial transmit command/data |
| **Pin 9** | **GND** | **GPS GND**, **SIM GND** | 0V | Common Ground return |
| **Pin 10** | **GPIO 15 (UART RX)** | **GPS TX** (Yellow) / **SIM TX** | 3.3V Serial RX | Serial receive NMEA / AT data |
| **Pin 11** | **GPIO 17** | **LED Anode (+)** *(via 220Ω resistor)* | 3.3V Output | Crash & Alcohol Alert Indicator |
| **Pin 12** | **GPIO 18** | **SW-420 DO** (Yellow) | 3.3V Input | Digital Vibration detection (`HIGH` = Impact) |
| **Pin 14** | **GND** | **ADS1115 GND** | 0V | ADC Ground return |
| **Pin 15** | **GPIO 22** | **Hall-Effect Sensor DO** | 3.3V Input | Wheel rotation counter for speed (km/h) |
| **Pin 25** | **GND** | **LED Cathode (-)** | 0V | LED Ground return |

---

## 2. 🎛️ ADS1115 ADC Channel Mapping (I2C Address `0x48`)

The ADS1115 converts all analog signals to 16-bit digital values over the Pi's I2C bus (GPIO 2 & 3).

| Channel Pin | Connected Sensor | Sensor Pin | Signal Range | Conversion Formula in Code |
|:---:|---|---|:---:|---|
| **A0** | **MQ-3 Gas / Alcohol** | AOUT | 0.0V – 5.0V | `ppm = (voltage / 5.0) * 100`<br>*(Alert if voltage ≥ 0.40V)* |
| **A1** | *Reserved* | AOUT | 0.0V – 5.0V | Analog vibration sensor (if used) |
| **A2** | **Temperature Sensor (LM35)** | AOUT | 0.0V – 5.0V | `celsius = voltage * 100.0`<br>*(LM35: 10mV per °C)* |
| **A3** | *Unused* | — | — | Available for future sensor expansion |

---

## 3. 🔌 Module-by-Module Connection Details

### 3.1 ADS1115 ADC Module (16-bit I2C)
```
ADS1115 Module:
├── VDD (Power) → Raspberry Pi Pin 2 or 4 (5V)  [CRITICAL: 5V to read 0-5V signals!]
├── GND (Ground)→ Raspberry Pi Pin 14 (GND)
├── SDA (Data)  → Raspberry Pi Pin 3 (GPIO 2)
└── SCL (Clock) → Raspberry Pi Pin 5 (GPIO 3)
```

### 3.2 MQ-3 Alcohol / Gas Sensor (Analog via ADS1115)
```
MQ-3 Sensor:
├── VCC (Red)   → Raspberry Pi Pin 2 (5V)
├── GND (Black) → Raspberry Pi Pin 6 (GND)
└── AOUT(Yellow)→ ADS1115 Channel A0
```
- **Signal Type:** 0–5V Analog Voltage
- **Conversion:** 16-bit digital via ADS1115 Channel A0
- **Formula:** `ppm = (voltage / 5.0) * 100`

### 3.3 Temperature Sensor (LM35 Analog via ADS1115)
```
LM35 Sensor:
├── VCC (Red)   → Raspberry Pi Pin 4 (5V)
├── GND (Black) → Raspberry Pi Pin 6 (GND)
└── AOUT(Yellow)→ ADS1115 Channel A2
```
- **Signal Type:** 0–5V Analog Voltage
- **Conversion:** 16-bit digital via ADS1115 Channel A2
- **Formula:** `celsius = voltage * 100.0` (10mV per °C)

### 3.4 SW-420 Vibration Sensor (Digital Direct)
```
SW-420 Sensor:
├── VCC (Red)   → Raspberry Pi Pin 1 (3.3V)
├── GND (Black) → Raspberry Pi Pin 6 (GND)
└── DO  (Yellow)→ Raspberry Pi Pin 12 (GPIO 18)
```
- **Signal Type:** 3.3V Digital Input
- **Output:** `LOW` (0V) = Stable, `HIGH` (3.3V) = Vibration / Impact detected
- **No ADC Needed:** Direct GPIO reading

### 3.5 Status / Alert LED
```
LED Circuit:
├── Anode   (+ / Long leg)  → 220Ω Resistor → Raspberry Pi Pin 11 (GPIO 17)
└── Cathode (- / Short leg) → Raspberry Pi Pin 25 (GND)
```
- **Signal Type:** 3.3V Digital Output
- **Operation:** Turned ON (`HIGH`) during crashes or alcohol detection

### 3.6 NEO-6M GPS Module (UART Serial)
```
NEO-6M GPS:
├── VCC (Red)   → Raspberry Pi Pin 4 (5V)
├── GND (Black) → Raspberry Pi Pin 9 (GND)
├── TX  (Yellow)→ Raspberry Pi Pin 10 (GPIO 15 / UART RX)  [CROSSED]
└── RX  (Green) → Raspberry Pi Pin 8  (GPIO 14 / UART TX)  [CROSSED]
```
- **Protocol:** UART Serial (9600 baud)
- **Port:** `/dev/ttyAMA0` (fallback `/dev/serial0`)
- **Format:** NMEA sentences (`$GPRMC`, `$GPGGA`)

### 3.7 SIM800L / 4G GSM Module
```
SIM Module:
├── USB-to-Serial Adapter → Any USB port on the Pi (/dev/ttyUSB0)
└── OR via UART           → TX to GPIO 14, RX to GPIO 15
```
- **Protocol:** Serial AT Commands (9600 baud)

### 3.8 Hall-Effect Wheel Speed Sensor
```
Hall-Effect Sensor:
├── VCC (Red)   → Raspberry Pi Pin 4 (5V)
├── GND (Black) → Raspberry Pi Pin 14 (GND)
└── DO  (Yellow)→ Raspberry Pi Pin 15 (GPIO 22)
```
- **Signal Type:** Pulse counter input on GPIO 22
- **Speed Calculation:** Count pulses per second converted to km/h based on wheel circumference

---

## 4. ⚡ Critical Electrical Safety Rules

> [!CAUTION]
> **1. ADS1115 VDD must be connected to 5V (NOT 3.3V):**  
> If powered by 3.3V, any analog voltage from the MQ-3 or LM35 exceeding 3.3V will be clipped, resulting in corrupted sensor readings and loss of data.
>
> **2. SW-420 VCC must be connected to 3.3V (NOT 5V):**  
> The Raspberry Pi GPIO pins are **NOT 5V tolerant**. Powering the digital SW-420 module from 3.3V guarantees its digital output never exceeds 3.3V.
>
> **3. LED must have the 220Ω resistor:**  
> Connecting an LED directly between GPIO 17 and GND without a resistor will draw excessive current and burn out the GPIO pin.
>
> **4. GPS Serial lines must be crossed:**  
> GPS **TX** connects to Pi **RX** (Pin 10), and GPS **RX** connects to Pi **TX** (Pin 8).

---

## 5. 🧪 Sensor Diagnostic & Verification Commands

All test scripts are located in the `tests/` directory:

| Test Script | Command | What It Verifies |
|---|---|---|
| **ADS1115 Diagnostic** | `python3 tests/test_ads1115.py` | Scans channels A0, A1, A2, A3 on I2C `0x48` |
| **MQ-3 Gas Sensor** | `python3 tests/test_mq3.py` | Monitors voltage (V) and PPM via ADS1115 Channel A0 |
| **Temperature Sensor** | `python3 tests/test_temperature.py` | Displays real-time temperature in °C via ADS1115 Channel A2 |
| **Vibration Sensor** | `python3 tests/test_vibration.py` | Verifies SW-420 impact detection on GPIO 18 |
| **GPS Module** | `python3 tests/test_gps.py` | Verifies UART NMEA sentences on `/dev/ttyAMA0` |
| **GSM Module** | `python3 tests/test_gsm_sms.py` | Sends a test emergency SMS via AT commands |

---

## 6. 🚀 Running the System

- **Core Blackbox Logger:**
  ```bash
  python3 src/main.py
  ```
- **Full Live Web Dashboard:**
  ```bash
  python3 main.py
  ```
  *Dashboard access:* `http://<pi-ip-address>:5000` or `http://raspberrypi.local:5000`
