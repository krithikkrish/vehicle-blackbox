import time

try:
    import serial
    MOCK_MODE = False
except:
    MOCK_MODE = True

class AlertSystem:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.mock = MOCK_MODE
        
        if not self.mock:
            import RPi.GPIO as GPIO
            self.LED_PIN = 17
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.LED_PIN, GPIO.OUT)
            GPIO.output(self.LED_PIN, GPIO.LOW)
            
    def trigger_local_alarm(self, reason):
        """Turn on the physical LED."""
        print(f"ALARM TRIGGERED: {reason}")
        if not self.mock:
            import RPi.GPIO as GPIO
            GPIO.output(self.LED_PIN, GPIO.HIGH)

    def send_emergency_sms(self, location_data):
        """Send SOS SMS via SIM800L."""
        message = f"SOS! CRASH DETECTED. Location: {location_data}"
        print(f"Attempting to send SMS to {self.phone_number}: {message}")
        
        if self.mock:
            print("[MOCK] SMS Sent successfully.")
            return True
            
        try:
            # Same logic as your test_gsm_sms.py
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            ser.write(b'AT+CMGF=1\r')
            time.sleep(0.5)
            ser.write(f'AT+CMGS="{self.phone_number}"\r'.encode())
            time.sleep(0.5)
            ser.write(message.encode())
            ser.write(bytes([26]))
            time.sleep(2)
            ser.close()
            return True
        except Exception as e:
            print(f"Failed to send real SMS: {e}")
            return False
