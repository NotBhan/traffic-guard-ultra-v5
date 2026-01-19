# utils/helpers.py

import time


def current_timestamp():
    """
    Returns current timestamp string
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")


def safe_int(value, default=0):
    """
    Safely convert value to int
    """
    try:
        return int(value)
    except:
        return default
