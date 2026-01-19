# hardware/arduino_serial.py

import time
import serial
from threading import Lock

from hardware.signal_commands import build_command

# -------------------------------
# SERIAL CONFIG
# -------------------------------
SERIAL_PORT = "COM3"      # ⚠️ CHANGE if needed
BAUD_RATE = 9600
WRITE_DELAY = 0.1         # seconds

_ser = None
_lock = Lock()


# -------------------------------
# GET SERIAL CONNECTION
# -------------------------------
def _get_serial():
    global _ser

    with _lock:
        if _ser is None or not _ser.is_open:
            try:
                _ser = serial.Serial(
                    port=SERIAL_PORT,
                    baudrate=BAUD_RATE,
                    timeout=1
                )
                time.sleep(2)  # Arduino reset delay
                print("[ARDUINO] Connected")
            except Exception as e:
                print("[ARDUINO] Connection failed:", e)
                _ser = None

        return _ser


# -------------------------------
# SEND SIGNAL
# -------------------------------
def send_signal_to_arduino(direction, color):
    """
    Send signal command to Arduino safely
    """
    ser = _get_serial()
    if ser is None:
        print("[ARDUINO] Not connected")
        return False

    try:
        cmd = build_command(direction, color)
        ser.write((cmd + "\n").encode())
        ser.flush()
        time.sleep(WRITE_DELAY)
        print("[ARDUINO] Sent:", cmd)
        return True
    except Exception as e:
        print("[ARDUINO] Write failed:", e)
        return False
