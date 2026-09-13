#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import time

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print(f"Hardware import failed: {e}. Using MOCK mode.")
    import random
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_DOWN = "PUD_DOWN"
        def setmode(self, mode): pass
        def setup(self, pin, mode, pull_up_down=None): pass
        def input(self, pin): return random.choice([0, 0, 0, 0, 1])
        def cleanup(self): pass
    GPIO = MockGPIO()

# Replace with the actual GPIO BCM pin number you connect the SW-420 to
VIBRATION_PIN = 17

def setup():
    GPIO.setmode(GPIO.BCM)
    # The SW-420 usually acts as a simple switch
    GPIO.setup(VIBRATION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print(f"Monitoring vibration on GPIO {VIBRATION_PIN}...")

def loop():
    try:
        while True:
            if GPIO.input(VIBRATION_PIN):
                print(f"[{time.strftime('%H:%M:%S')}] Vibration Detected!")
                time.sleep(0.5) # simple debounce
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting vibration test.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    setup()
    loop()
