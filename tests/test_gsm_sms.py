#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
import serial
import time

# Update with the correct USB port, e.g., /dev/ttyUSB0
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
PHONE_NUMBER = '+1234567890' # Replace with actual number

def send_sms(phone_number, message):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to SIM800L on", SERIAL_PORT)
    except Exception as e:
        print(f"Hardware connect failed: {e}. Using MOCK mode.")
        class MockSerial:
            in_waiting = 10
            def write(self, data):
                print(f"[MOCK SERIAL TX]: {data}")
            def read(self, size):
                return b"OK\r\n"
            def close(self): pass
        ser = MockSerial()
        
    try:
        # Check AT communication
        ser.write(b'AT\r')
        time.sleep(1)
        print(ser.read(ser.in_waiting).decode('utf-8'))
        
        # Set text mode
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        print(ser.read(ser.in_waiting).decode('utf-8'))
        
        # Send SMS command
        command = f'AT+CMGS="{phone_number}"\r'
        ser.write(command.encode('utf-8'))
        time.sleep(1)
        
        # Send message content and CTRL+Z (ASCII 26)
        ser.write(message.encode('utf-8'))
        ser.write(bytes([26]))
        time.sleep(3)
        
        print("Response after sending:")
        print(ser.read(ser.in_waiting).decode('utf-8'))
        ser.close()
    except Exception as e:
        print("Error communicating with GSM module:", e)

if __name__ == "__main__":
    test_msg = "Smart Black Box Test: GSM SMS is working!"
    send_sms(PHONE_NUMBER, test_msg)
