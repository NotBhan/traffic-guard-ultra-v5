# core/emergency_handler.py

"""
Handles emergency vehicle priority logic.
This module can be triggered manually or via detection logic.
"""

import time

# Emergency state
_emergency_active = False
_emergency_direction = None
_emergency_start_time = None

# Max emergency green time (safety)
MAX_EMERGENCY_GREEN = 40


def activate_emergency(direction):
    """
    Activate emergency mode for given direction
    """
    global _emergency_active, _emergency_direction, _emergency_start_time

    _emergency_active = True
    _emergency_direction = direction
    _emergency_start_time = time.time()

    print(f"[EMERGENCY] Activated for direction: {direction}")


def deactivate_emergency():
    """
    Deactivate emergency mode
    """
    global _emergency_active, _emergency_direction, _emergency_start_time

    _emergency_active = False
    _emergency_direction = None
    _emergency_start_time = None

    print("[EMERGENCY] Deactivated")


def is_emergency_active():
    """
    Check if emergency mode is active
    """
    return _emergency_active


def get_emergency_status():
    """
    Returns emergency status for dashboard
    """
    if not _emergency_active:
        return {"active": False}

    elapsed = time.time() - _emergency_start_time

    # Auto-disable safety
    if elapsed >= MAX_EMERGENCY_GREEN:
        deactivate_emergency()
        return {"active": False}

    return {
        "active": True,
        "direction": _emergency_direction,
        "elapsed_time": int(elapsed)
    }
