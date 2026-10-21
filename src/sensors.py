import time
import random

# Hardware library imports with graceful fallback to MOCK mode
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except Exception as e:
    print(f"RPi.GPIO not available ({e}). Using mock GPIO.")
    GPIO_AVAILABLE = False

try:
    import serial
    SERIAL_AVAILABLE = True
except Exception as e:
    print(f"pyserial not available ({e}). Using mock serial.")
    SERIAL_AVAILABLE = False

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    ADS_AVAILABLE = True
except Exception as e:
    print(f"ADS1115 libraries not available ({e}). Using mock ADC.")
    ADS_AVAILABLE = False


class SensorInterface:
    def __init__(self):
        # 1. GPIO Setup
        # SW-420 DO -> GPIO 18 (Pin 12)
        self.VIBRATION_PIN = 18
        # Hall-effect module DO -> GPIO 22 (Pin 15)
        self.HALL_PIN = 22

        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.setup(self.HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                self.gpio_ready = True
            except Exception as e:
                print(f"GPIO setup error: {e}")
                self.gpio_ready = False
        else:
            self.gpio_ready = False

        # 2. ADS1115 I2C ADC Setup (SDA=GPIO2, SCL=GPIO3, Address=0x48)
        # Channel A0: MQ-3 Gas/Alcohol sensor
        # Channel A2: Temperature sensor (LM35)
        self.mq3_channel = None
        self.temperature_channel = None
        if ADS_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.ads = ADS.ADS1115(i2c, address=0x48)
                # Gain of 1 gives range up to 4.096V (ADS1115 internal reference)
                self.ads.gain = 1
                self.mq3_channel = AnalogIn(self.ads, ADS.P0)          # Channel A0
                self.temperature_channel = AnalogIn(self.ads, ADS.P2)  # Channel A2
                print("ADS1115 ADC initialized on I2C 0x48 (A0=MQ3, A2=Temp)")
            except Exception as e:
                print(f"ADS1115 setup error: {e}. Fallback to mock analog.")
                self.mq3_channel = None
                self.temperature_channel = None

        # 3. GPS UART Setup (NEO-6M on GPIO 14/15)
        self.gps_serial = None
        if SERIAL_AVAILABLE:
            for port in ['/dev/ttyAMA0', '/dev/serial0', '/dev/ttyS0']:
                try:
                    self.gps_serial = serial.Serial(port, 9600, timeout=1)
                    print(f"GPS connected on {port}")
                    break
                except Exception:
                    continue

    def read_vibration(self):
        """
        Read SW-420 digital vibration sensor on GPIO 18.
        Specification: HIGH when vibration detected, LOW = no vibration.
        """
        if self.gpio_ready:
            try:
                return GPIO.input(self.VIBRATION_PIN) == GPIO.HIGH
            except Exception:
                pass
        # Mock mode fallback (5% chance of mock vibration)
        return random.random() < 0.05

    def read_mq3(self):
        """
        Read MQ-3 gas sensor (Analog via ADS1115 Channel A0).
        Formula: ppm = (voltage / 5.0) * 100
        """
        if self.mq3_channel is not None:
            try:
                voltage = max(0.0, float(self.mq3_channel.voltage))
                raw_val = int(self.mq3_channel.value)
                ppm = (voltage / 5.0) * 100.0
                return {
                    'voltage': round(voltage, 3),
                    'raw': raw_val,
                    'ppm': round(ppm, 2)
                }
            except Exception as e:
                print(f"Error reading MQ3 from ADS1115: {e}")

        # Mock fallback
        v = round(random.uniform(0.3, 0.6), 3)
        return {
            'voltage': v,
            'raw': int((v / 4.096) * 32767),
            'ppm': round((v / 5.0) * 100.0, 2)
        }

    def read_temperature(self):
        """
        Read Temperature sensor (Analog via ADS1115 Channel A2).
        Formula: LM35 gives 10mV per °C -> celsius = voltage * 100.0
        """
        if self.temperature_channel is not None:
            try:
                voltage = max(0.0, float(self.temperature_channel.voltage))
                raw_val = int(self.temperature_channel.value)
                celsius = voltage * 100.0
                return {
                    'voltage': round(voltage, 3),
                    'raw': raw_val,
                    'celsius': round(celsius, 2)
                }
            except Exception as e:
                print(f"Error reading Temp from ADS1115: {e}")

        # Mock fallback
        v = round(random.uniform(0.24, 0.28), 3)
        return {
            'voltage': v,
            'raw': int((v / 4.096) * 32767),
            'celsius': round(v * 100.0, 2)
        }

    def read_alcohol(self):
        """
        Returns True if alcohol concentration exceeds threshold.
        Threshold: MQ3 voltage >= 0.40V (or > ~40 PPM).
        """
        mq3 = self.read_mq3()
        return mq3['voltage'] >= 0.40

    def read_hall(self):
        """Read Hall-effect digital sensor on GPIO 22."""
        if self.gpio_ready:
            try:
                return bool(GPIO.input(self.HALL_PIN))
            except Exception:
                pass
        return random.choice([True, False])

    def read_gps(self):
        """Read latest GPS coordinates via UART."""
        if self.gps_serial and self.gps_serial.in_waiting:
            try:
                line = self.gps_serial.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('$'):
                    return {"nmea": line}
            except Exception:
                pass
        return {"nmea": "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"}

    def read_all(self):
        """Return a structured dictionary of all current sensor readings."""
        mq3_data = self.read_mq3()
        temp_data = self.read_temperature()
        vib_detected = self.read_vibration()
        alcohol_detected = mq3_data['voltage'] >= 0.40
        hall_active = self.read_hall()
        gps_data = self.read_gps()

        return {
            "timestamp": time.time(),
            "vibration_detected": vib_detected,
            "alcohol_detected": alcohol_detected,
            "mq3_voltage": mq3_data['voltage'],
            "mq3_ppm": mq3_data['ppm'],
            "temperature_celsius": temp_data['celsius'],
            "temperature_voltage": temp_data['voltage'],
            "mq3": mq3_data,
            "temperature": temp_data,
            "hall_sensor_active": hall_active,
            "gps": gps_data
        }

    def cleanup(self):
        if self.gpio_ready:
            try:
                GPIO.cleanup()
            except Exception:
                pass
        if self.gps_serial and self.gps_serial.is_open:
            try:
                self.gps_serial.close()
            except Exception:
                pass
