#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import serial
import time

# Primary UART for Pi 4 GPIO 14/15 is /dev/ttyAMA0 (with fallback to /dev/serial0)
SERIAL_PORTS = ['/dev/ttyAMA0', '/dev/serial0', '/dev/ttyS0']
BAUD_RATE = 9600

def read_gps():
    ser = None
    for port in SERIAL_PORTS:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            print(f"Connected to GPS on {port}. Waiting for NMEA data...")
            break
        except Exception:
            continue

    if ser is None:
        print("Hardware connect failed. Using MOCK mode.")
        class MockSerial:
            def readline(self):
                time.sleep(1)
                return b'$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A\n'
            def close(self): pass
            @property
            def is_open(self): return True
        ser = MockSerial()
        
    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
                # In a real app, parse $GPRMC or $GPGGA using a library like pynmea2
    except KeyboardInterrupt:
        print("\nExiting GPS test.")
    except Exception as e:
        print("Error communicating with GPS module:", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    read_gps()
