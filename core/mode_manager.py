# core/mode_manager.py

from threading import Lock

# -------------------------------
# INTERNAL STATE
# -------------------------------
_current_mode = "simulation"
_arduino_enabled = True  # Default to ON (change to False if you want default OFF)
_lock = Lock()


# -------------------------------
# MODE HANDLERS
# -------------------------------
def get_current_mode():
    with _lock:
        return _current_mode

def set_mode(mode):
    global _current_mode
    if mode not in ["simulation", "live"]:
        return False
    with _lock:
        _current_mode = mode
    return True

def is_simulation_mode():
    return get_current_mode() == "simulation"


# -------------------------------
# ARDUINO HANDLERS (NEW)
# -------------------------------
def get_arduino_status():
    with _lock:
        return _arduino_enabled

def set_arduino_status(enabled):
    global _arduino_enabled
    with _lock:
        _arduino_enabled = bool(enabled)
        print(f"[SYSTEM] Arduino Mode set to: {_arduino_enabled}")