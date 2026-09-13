#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import time
from buffer import CircularBuffer
from sensors import SensorInterface
from alerts import AlertSystem
from crash_logic import CrashDetector

# Configurations
EMERGENCY_PHONE = "+1234567890" # Replace with real number
LOOP_DELAY_SEC = 0.1 # 10Hz sampling

def main():
    print("Starting Smart Vehicle Black Box...")
    
    # Initialize modules
    buffer = CircularBuffer(max_seconds=15, sample_rate_hz=10)
    sensors = SensorInterface()
    alerts = AlertSystem(phone_number=EMERGENCY_PHONE)
    crash_detector = CrashDetector()
    
    crash_handled = False
    
    try:
        while True:
            # 1. Read all sensors
            reading = sensors.read_all()
            
            # 2. Store in circular buffer
            buffer.add_reading(reading)
            
            # 3. Check for routine safety violations (Temperature, Alcohol, etc.)
            if reading["temperature_c"] and reading["temperature_c"] > 45.0:
                alerts.trigger_local_alarm("High Temperature!")
                
            # 4. Check for Crash Event
            if not crash_handled and crash_detector.evaluate(reading):
                print("\n!!! EXECUTING EMERGENCY PROTOCOL !!!")
                
                # Dump the last 15 seconds of data
                dump_file = buffer.dump_to_file("crash_log.json")
                
                # Send SOS SMS with latest GPS
                alerts.send_emergency_sms(location_data=reading.get("gps"))
                
                crash_handled = True # Prevent sending 1000 SMS messages
                print("Emergency protocols completed. Continuing to log...\n")
                
            # Sleep to maintain 10Hz loop
            time.sleep(LOOP_DELAY_SEC)
            
    except KeyboardInterrupt:
        print("\nShutting down Black Box...")
    finally:
        sensors.cleanup()

if __name__ == "__main__":
    main()
