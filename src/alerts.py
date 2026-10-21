import time
import os

try:
    import serial
    SERIAL_AVAILABLE = True
except Exception:
    SERIAL_AVAILABLE = False


class AlertSystem:
    def __init__(self, phone_number="+91XXXXXXXXXX", enable_gsm: bool = True):
        self.phone_number = phone_number
        self.enable_gsm = bool(enable_gsm)
        self.LED_PIN = 17  # GPIO 17 / Pin 11

        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.LED_PIN, GPIO.OUT)
            GPIO.output(self.LED_PIN, GPIO.LOW)
            self.gpio_ready = True
        except Exception as e:
            self.gpio_ready = False

    def trigger_local_alarm(self, reason):
        """Turn on the physical LED on GPIO 17."""
        print(f"\n🚨 [LOCAL ALARM TRIGGERED]: {reason} (LED on GPIO 17 turned ON)")
        if self.gpio_ready:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.LED_PIN, GPIO.HIGH)
            except Exception:
                pass

    def clear_alarm(self):
        """Turn off the physical LED on GPIO 17."""
        if self.gpio_ready:
            try:
                import RPi.GPIO as GPIO
                GPIO.output(self.LED_PIN, GPIO.LOW)
            except Exception:
                pass

    def send_emergency_sms(self, location_data):
        """
        Send SOS SMS via SIM800L / GSM module.
        If GSM is disabled, skips sending.
        If no physical GSM module is connected, gracefully runs in Simulation Mode.
        """
        if not self.enable_gsm:
            print("ℹ️ GSM alert skipped — GSM module is DISABLED in this configuration.")
            return False

        message = f"🚨 SOS! CRASH DETECTED. Location: {location_data}"

        # Detect if physical GSM serial port is available
        gsm_port = None
        for port in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyAMA0']:
            if os.path.exists(port):
                gsm_port = port
                break

        if not gsm_port or not SERIAL_AVAILABLE:
            print("\n" + "=" * 60)
            print("  📱 [GSM ACTIVE — SIMULATION MODE (No Hardware Module Connected)]")
            print(f"  Simulated SMS dispatched to: {self.phone_number}")
            print(f"  Message: {message}")
            print("=" * 60 + "\n")
            return True

        # If physical hardware is present, send real AT commands
        try:
            ser = serial.Serial(gsm_port, 9600, timeout=1)
            ser.write(b'AT+CMGF=1\r')
            time.sleep(0.5)
            ser.write(f'AT+CMGS="{self.phone_number}"\r'.encode())
            time.sleep(0.5)
            ser.write(message.encode())
            ser.write(bytes([26]))
            time.sleep(2)
            ser.close()
            print(f"Real SMS dispatched via {gsm_port} to {self.phone_number}")
            return True
        except Exception as e:
            print(f"Physical GSM transmission failed ({e}). Falling back to simulation.")
            print(f"  Simulated Content: {message}")
            return True
