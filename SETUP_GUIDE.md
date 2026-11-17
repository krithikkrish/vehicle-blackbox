# 🚗 Vehicle Black Box — How to Wire & Run

> **Read this fully before touching any wires.**

---

## 🔌 STEP 1: Wire Everything Up

> **⚠️ UNPLUG the Pi's power cable before connecting any wires. Wiring while powered on can fry the Pi or the sensor.**

### How to Find the Pin Numbers

The Pi has 40 metal pins in 2 rows. Hold it with the USB ports facing you:
- **Pin 1** = top-left corner
- Left column = odd (1, 3, 5, 7…)
- Right column = even (2, 4, 6, 8…)

Google **"Raspberry Pi 4 GPIO pinout"** and keep that image open while wiring.

---

### SW-420 Vibration Sensor

| Sensor Wire | Goes To | Pi Pin # |
|-------------|---------|----------|
| VCC | 3.3V | **Pin 1** |
| GND | Ground | **Pin 6** |
| DO | GPIO18 | **Pin 12** |

---

### ADS1115 ADC Converter (I2C Interface)

| Module Pin | Goes To | Pi Pin # |
|------------|---------|----------|
| **VDD** | 5V Power (CRITICAL: 5V not 3.3V) | **Pin 2 or Pin 4** |
| **GND** | Ground | **Pin 14** |
| **SDA** | GPIO 2 (I2C Data) | **Pin 3** |
| **SCL** | GPIO 3 (I2C Clock) | **Pin 5** |

---

### MQ-3 Alcohol / Gas Sensor (Analog via ADS1115)

| Sensor Wire | Goes To | Connection |
|-------------|---------|------------|
| VCC | 5V | **Pi Pin 2** |
| GND | Ground | **Pi Pin 6** |
| **AOUT** | Analog Input | **ADS1115 Channel A0** |

---

### Temperature Sensor (LM35 / Analog via ADS1115)

| Sensor Wire | Goes To | Connection |
|-------------|---------|------------|
| VCC | 5V | **Pi Pin 4** |
| GND | Ground | **Pi Pin 6** |
| **AOUT** | Analog Input | **ADS1115 Channel A2** |

---


### Hall-effect Module

| Sensor Wire | Goes To | Pi Pin # |
|-------------|---------|----------|
| VCC | Power | **Pin 4** |
| GND | Ground | **Pin 14** |
| DO | GPIO22 | **Pin 15** |

---

### NEO-6M GPS Module

| Sensor Wire | Goes To | Pi Pin # |
|-------------|---------|----------|
| VCC | Power | **Pin 2 or Pin 4** |
| GND | Ground | **Pin 20** |
| **TX** | GPIO15 (RXD) | **Pin 10** |
| **RX** | GPIO14 (TXD) | **Pin 8** |

> **⚠️ GPS TX goes to Pi RX, and GPS RX goes to Pi TX. They are crossed on purpose. This is NOT a mistake.**

---

### LED (Alert Light)

| LED Wire | Goes To | Pi Pin # |
|----------|---------|----------|
| Long leg (+) | GPIO17 **through the 220Ω resistor** | **Pin 11** |
| Short leg (-) | Ground | **Pin 25** |

> Connect the resistor between Pin 11 and the long leg of the LED. Without the resistor, the LED will burn out.

---

### SIM800L GSM Module

| Module | Goes To |
|--------|---------|
| Connect via **USB-to-Serial adapter** | Any USB port on the Pi |

> Insert a working SIM card (with SMS balance) into the SIM800L **before** powering on.

---

### L298N Motor Driver (Bluetooth RC Car Chassis — Optional)

If you are building the motorized RC vehicle chassis alongside the blackbox:

| L298N Pin | Goes To | Pi Pin # / Power |
|---|---|---|
| **ENA** (Left PWM) | GPIO 12 (PWM0) | **Pin 32** *(Remove black jumper)* |
| **IN1** (Left Forward) | GPIO 23 | **Pin 16** |
| **IN2** (Left Reverse) | GPIO 24 | **Pin 18** |
| **IN3** (Right Forward) | GPIO 27 | **Pin 13** *(Conflict-free with Hall Effect!)* |
| **IN4** (Right Reverse) | GPIO 25 | **Pin 22** |
| **ENB** (Right PWM) | GPIO 13 (PWM1) | **Pin 33** *(Remove black jumper)* |
| **GND** | Ground & Battery (-) | **Pin 30** *(Common Ground is mandatory!)* |
| **12V / VMS** | Battery Pack (+) | 7.4V – 12V Li-ion battery pack |

> **⚠️ CRITICAL:** Always power the DC motors from an external battery pack (e.g. 2x 18650 Li-ion batteries). Never power the motors directly from the Raspberry Pi 5V header pin. Always tie the Battery (-) terminal and Raspberry Pi GND together.

---

### ✅ Wiring Checklist (Go Through This Before Powering On)

- [ ] No loose or dangling wires
- [ ] VCC wires go to power pins (1, 2, or 4) — **NOT** to any GPIO pin
- [ ] GND wires go to ground pins (6, 9, 14, 20, 25, or 30)
- [ ] Data wires go to correct GPIO pins
- [ ] LED has the 220Ω resistor (not connected directly)
- [ ] GPS: TX → Pin 10, RX → Pin 8 (crossed)
- [ ] SIM card is inside the SIM800L
- [ ] If using L298N motors: Battery (-) is connected to Raspberry Pi GND (Common Ground)

---

## 🛜 STEP 2: Enable Serial Port for GPS (One-Time Only)

You need to do this **once** so the GPS can talk to the Pi.

1. Open Terminal on the Pi
2. Run:
   ```bash
   sudo raspi-config
   ```
3. Go to **3 Interface Options** → **I6 Serial Port**
4. *"Login shell over serial?"* → **No**
5. *"Enable serial port hardware?"* → **Yes**
6. Press Finish → **Reboot** when asked

---

## 💻 STEP 3: Download the Code

Open Terminal and run these commands **one by one**:

```bash
cd ~
```

```bash
git clone https://github.com/krithikkrish/vehicle-blackbox.git
```

```bash
cd vehicle-blackbox
```

---

## 📦 STEP 4: Install the Required Libraries

```bash
pip3 install -r requirements.txt
```

> If you get an error saying "externally managed environment", run this instead:
> ```bash
> pip3 install --break-system-packages -r requirements.txt
> ```

---

## 📱 STEP 5: Set Your Emergency Phone Number

Configure your emergency contact via `.env`:

```bash
cp .env.example .env
nano .env
```

Set `EMERGENCY_PHONE` to the **real phone number** you want the SOS SMS to go to (with country code, e.g., `+919876543210`):
```bash
EMERGENCY_PHONE=+919876543210
```

Alternatively, you can export it as an environment variable before running:
```bash
export EMERGENCY_PHONE="+919876543210"
```

---

## 🧪 STEP 6: Test Each Sensor One by One

Before running the full system, test each sensor individually to make sure wiring is correct.

### Test Vibration (SW-420)
```bash
cd ~/vehicle-blackbox/tests
python3 test_vibration.py
```
Tap the sensor. You should see the readings change. Press `Ctrl + C` to stop.

### Test GPS (NEO-6M)
```bash
python3 test_gps.py
```
> **GPS needs clear sky!** Take the Pi near a window or outside. First fix takes 1–5 minutes. Be patient. Press `Ctrl + C` to stop.

### Test ADS1115 ADC (I2C 0x48)
```bash
python3 test_ads1115.py
```
Scans all 4 channels on the ADS1115. Press `Ctrl + C` to stop.

### Test MQ-3 Gas Sensor (Analog via ADS1115 A0)
```bash
python3 test_mq3.py
```
Monitors voltage and PPM. Blow some alcohol vapor or lighter gas near the sensor to see the value increase. Press `Ctrl + C` to stop.

### Test Temperature Sensor (LM35 via ADS1115 A2)
```bash
python3 test_temperature.py
```
Displays current ambient temperature in °C. Press `Ctrl + C` to stop.

### Test SMS (SIM800L)
```bash
python3 test_gsm_sms.py
```
This will try to send a test SMS. Make sure the SIM has credit. Press `Ctrl + C` to stop.

### Test Motors & Chassis (L298N)
```bash
python3 tests/test_motors.py
```
Performs a 7-step sequenced motor check (forward, reverse, turn left, turn right, and speed ramp). Elevate your car wheels before running this test.

---

## 🚀 STEP 7: Run the Full Black Box System

### Option A: Full Live Web Dashboard (Recommended)
```bash
cd ~/vehicle-blackbox
python3 main.py
```
Open your browser on phone or laptop:
`http://<pi-ip-address>:5000` or `http://raspberrypi.local:5000`

### Option B: Headless Black Box Logger
```bash
cd ~/vehicle-blackbox
python3 src/main.py
```

You should see:
```
Starting Smart Vehicle Black Box...
```

**What it's doing right now:**
- Reading all sensors 10 times per second
- Saving every reading to `continuous_log.csv` (on the SD card)
- Keeping the last 15 seconds of data in memory
- If vibration stays for more than 0.3 seconds → **CRASH detected** → LED turns on → SMS sent → Last 15 seconds saved to `crash_log.json`
- If alcohol is detected → LED turns on

**To stop it:** Press `Ctrl + C`

---

## 🏎️ STEP 8: Drive the Vehicle via Mobile Bluetooth (RC Car Mode)

You can drive the car using your smartphone over Bluetooth while the Black Box logs telemetry.

### 1. Enable Bluetooth Serial (One-Time Setup on Pi)
Open a terminal on your Pi:
```bash
sudo bluetoothctl
```
Inside the `[bluetooth]#` console, enter:
```text
power on
discoverable on
pairable on
agent on
default-agent
```
On your mobile phone:
- Open **Bluetooth Settings** $\to$ Scan for devices $\to$ Select your Raspberry Pi (`raspberrypi` or `blackbox`).
- Confirm the numeric pairing passkey on both phone and Pi (`yes`).
- Type `exit` in `bluetoothctl`.

Next, enable the Serial Port Profile (SPP):
```bash
sudo sdptool add SP
```

### 2. Start the Bluetooth Car Controller
```bash
cd ~/vehicle-blackbox
python3 scripts/bt_car.py
```

### 3. Connect via Smartphone App
1. Install **"Arduino Bluetooth RC Car"** (by Andi.Co) or **"Serial Bluetooth Terminal"** from Google Play Store / App Store.
2. Open the app $\to$ Settings/Connect icon $\to$ Select your paired **Raspberry Pi**.
3. Use the directional buttons / steering wheel to drive:

| Mobile Command | Function |
|:---:|---|
| **F** | Drive Forward |
| **B** | Drive Backward |
| **L** | Pivot Turn Left |
| **R** | Pivot Turn Right |
| **S** | Neutral / Stop |
| **0 – 9** | Variable Speed Regulation (0% to 90%) |
| **q** | Maximum Speed (100% duty cycle) |

> **Pro Tip:** To test without a mobile phone, run `python3 scripts/bt_car.py --cli` for keyboard control (`W`, `A`, `S`, `D`, `Space`) or `python3 scripts/bt_car.py --test` for automated self-test!

---

## 🔄 STEP 9: Getting Future Code Updates

When I push updates to GitHub, pull them like this:

```bash
cd ~/vehicle-blackbox
git pull origin main
```

Then run again:
```bash
python3 src/main.py
```

---

## 📁 What Each File Does

| File | Purpose |
|------|---------|
| `src/main.py` | **Run this.** The main program that starts everything. |
| `sensors.py` | Talks to the physical sensors. |
| `buffer.py` | Stores last 15 seconds + saves CSV to SD card. |
| `crash_logic.py` | Decides if a crash happened. |
| `alerts.py` | Turns on LED + sends SOS SMS. |
| `tests/` | Individual sensor test scripts. |

| Auto-generated File | When it appears |
|---------------------|----------------|
| `continuous_log.csv` | Created the moment you run `src/main.py`. Every sensor reading goes here. |
| `crash_log.json` | Created only if a crash is detected. Contains the last 15 seconds of data. |

---

## 🔴 Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'RPi'` | Run `pip3 install RPi.GPIO` (add `--break-system-packages` if needed) |
| `Permission denied` | Run with `sudo python3 src/main.py` |
| GPS shows no data | Enable serial port (Step 2), take GPS outside, wait 5 mins, reboot Pi |
| SMS not sending | Check SIM card is inserted, has credit, and run `ls /dev/ttyUSB*` — tell me the output |
| LED not turning on | Check LED direction (long leg = +), check resistor is connected |
| Vibration always triggering | Check wiring (VCC to Pin 1 at 3.3V, NOT 5V) |
| Program crashes immediately | Run the individual test scripts (Step 6) first to find which sensor has a problem |

---

## 📞 Stuck?

Take a photo of:
1. Your wiring
2. The error on screen

Send both to the group chat 🙌
