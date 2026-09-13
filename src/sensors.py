import time
import random

# Try to import hardware libraries, fallback to mock mode
try:
    import RPi.GPIO as GPIO
    import serial
    MOCK_MODE = False
except Exception as e:
    print(f"Hardware not fully available: {e}. Using MOCK mode for sensors.")
    MOCK_MODE = True

class SensorInterface:
    def __init__(self):
        self.mock = MOCK_MODE
        
        if not self.mock:
            # Set up real GPIO pins
            GPIO.setmode(GPIO.BCM)
            
            # SW-420 Vibration (Pin 12 -> GPIO18)
            self.VIBRATION_PIN = 18
            GPIO.setup(self.VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # MQ-3 Alcohol (Pin 16 -> GPIO23)
            self.ALCOHOL_PIN = 23
            GPIO.setup(self.ALCOHOL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Hall-effect module (Pin 15 -> GPIO22)
            self.HALL_PIN = 22
            GPIO.setup(self.HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Setup GPS Serial (NEO-6M on GPIO14/15)
            try:
                self.gps_serial = serial.Serial('/dev/serial0', 9600, timeout=1)
            except:
                self.gps_serial = None
                
    def read_vibration(self):
        """Read SW-420 digital vibration sensor."""
        if self.mock:
            # 5% chance of mock vibration
            return random.random() < 0.05
        return bool(GPIO.input(self.VIBRATION_PIN))
        
    def read_alcohol(self):
        """Read MQ-3 digital alcohol sensor."""
        if self.mock:
            return random.random() < 0.01
        return bool(GPIO.input(self.ALCOHOL_PIN))
        
    def read_hall(self):
        """Read Hall-effect digital sensor."""
        if self.mock:
            return random.choice([True, False])
        return bool(GPIO.input(self.HALL_PIN))

    def read_gps(self):
        """Read latest GPS coordinates."""
        if self.mock:
            return {"lat": 48.1173, "lon": 11.5167} # Mock Munich coordinates
            
        if self.gps_serial and self.gps_serial.in_waiting:
            line = self.gps_serial.readline().decode('utf-8', errors='ignore').strip()
            # Basic mock parse
            if "$GPRMC" in line:
                return {"raw_nmea": line}
        return None
        
    def read_all(self):
        """Return a dictionary of all current sensor readings."""
        return {
            "timestamp": time.time(),
            "vibration_detected": self.read_vibration(),
            "alcohol_detected": self.read_alcohol(),
            "hall_sensor_active": self.read_hall(),
            "gps": self.read_gps()
        }

    def cleanup(self):
        if not self.mock:
            GPIO.cleanup()
