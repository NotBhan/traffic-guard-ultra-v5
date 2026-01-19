# core/traffic_state.py

from threading import Lock

# -------------------------------
# SHARED STATE
# -------------------------------
_counts = {
    "north": 0,
    "south": 0,
    "east": 0,
    "west": 0
}

# The missing piece causing your Signal/Timer crash
_current_green = "north" 

_lock = Lock()


# -------------------------------
# VEHICLE COUNTS
# -------------------------------
def update_count(direction, count):
    if direction not in _counts: return
    with _lock:
        _counts[direction] = int(count) if count >= 0 else 0

def get_all_counts():
    with _lock:
        return dict(_counts)


# -------------------------------
# SIGNAL STATE (Fixes Timers)
# -------------------------------
def set_current_green(direction):
    global _current_green
    with _lock:
        _current_green = direction

def get_current_green():
    with _lock:
        return _current_green