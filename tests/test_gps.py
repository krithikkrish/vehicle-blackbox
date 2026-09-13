#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import serial
import time

# Hardware UART for Pi 4 is typically /dev/ttyS0 or /dev/serial0
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 9600

def read_gps():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to GPS on {SERIAL_PORT}. Waiting for NMEA data...")
    except Exception as e:
        print(f"Hardware connect failed: {e}. Using MOCK mode.")
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
