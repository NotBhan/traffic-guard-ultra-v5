# force_red.py
import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

print("Forcing RED ON...")
# <1100> = North(1) Red(1) Yellow(0) Green(0)
ser.write(b"<1100>\n") 

ser.close()