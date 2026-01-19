# core/fail_safe.py

import time

# -------------------------------
# FAIL-SAFE CONFIG
# -------------------------------
FAIL_SAFE_GREEN_TIME = 20
FAIL_SAFE_DIRECTION = "north"

_last_failure_time = 0


def handle_camera_failure():
    """
    Called when camera feed fails.
    Returns safe signal state.
    """
    global _last_failure_time

    _last_failure_time = time.time()

    return {
        "current_direction": FAIL_SAFE_DIRECTION,
        "signal": "GREEN",
        "remaining_time": FAIL_SAFE_GREEN_TIME,
        "fail_safe": True
    }


def is_fail_safe_active(timeout=5):
    """
    Returns True if fail-safe was triggered recently
    """
    return (time.time() - _last_failure_time) <= timeout
