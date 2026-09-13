import time
import random
import glob

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
            self.VIBRATION_PIN = 17
            GPIO.setup(self.VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Setup GPS Serial
            try:
                self.gps_serial = serial.Serial('/dev/serial0', 9600, timeout=1)
            except:
                self.gps_serial = None
            
            # (ADS1115 and MPU6050 setup would go here using smbus2 or adafruit libraries)
            
    def read_temperature(self):
        """Read DS18B20 1-Wire temperature."""
        if self.mock:
            return random.uniform(25.0, 30.0)
            
        try:
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28*')[0]
            device_file = device_folder + '/w1_slave'
            
            with open(device_file, 'r') as f:
                lines = f.readlines()
                
            if lines[0].strip()[-3:] == 'YES':
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos+2:]
                    return float(temp_string) / 1000.0
            return None
        except:
            return None # Sensor not wired

    def read_vibration(self):
        """Read SW-420 digital vibration sensor."""
        if self.mock:
            # 5% chance of mock vibration
            return random.random() < 0.05
            
        return bool(GPIO.input(self.VIBRATION_PIN))
        
    def read_gps(self):
        """Read latest GPS coordinates."""
        if self.mock:
            return {"lat": 48.1173, "lon": 11.5167} # Mock Munich coordinates
            
        if self.gps_serial and self.gps_serial.in_waiting:
            line = self.gps_serial.readline().decode('utf-8', errors='ignore').strip()
            # Basic mock parse, a real implementation uses pynmea2
            if "$GPRMC" in line:
                return {"raw_nmea": line}
        return None
        
    def read_all(self):
        """Return a dictionary of all current sensor readings."""
        return {
            "timestamp": time.time(),
            "temperature_c": self.read_temperature(),
            "vibration_detected": self.read_vibration(),
            "gps": self.read_gps(),
            # Placeholders for ADC and MPU6050 which need the hardware libraries
            "alcohol_level": random.uniform(0, 100) if self.mock else 0,
            "smoke_level": random.uniform(0, 100) if self.mock else 0,
            "acceleration_g": random.uniform(0.9, 1.1) if self.mock else 1.0 
        }

    def cleanup(self):
        if not self.mock:
            GPIO.cleanup()
