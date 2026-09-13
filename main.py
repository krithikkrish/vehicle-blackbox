#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import time
from buffer import CircularBuffer, CSVLogger
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
    csv_logger = CSVLogger("continuous_log.csv")
    sensors = SensorInterface()
    alerts = AlertSystem(phone_number=EMERGENCY_PHONE)
    crash_detector = CrashDetector()
    
    crash_handled = False
    
    try:
        while True:
            # 1. Read all sensors
            reading = sensors.read_all()
            
            # 2. Log to continuous CSV and store in circular buffer
            csv_logger.log_reading(reading)
            buffer.add_reading(reading)
            
            # 3. Check for routine safety violations (Alcohol)
            if reading.get("alcohol_detected"):
                alerts.trigger_local_alarm("Driver Alcohol Detected!")
                
            # 4. Check for Crash Event
            if not crash_handled and crash_detector.evaluate(reading):
                print("\n!!! EXECUTING EMERGENCY PROTOCOL !!!")
                
                # Dump the last 15 seconds of data (JSON format)
                dump_file = buffer.dump_to_file("crash_log.json")
                
                # Trigger local LED alarm and Send SOS SMS with latest GPS
                alerts.trigger_local_alarm("CRASH!")
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
