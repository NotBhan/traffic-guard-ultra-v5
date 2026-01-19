# core/timing_logic.py

from core.traffic_state import get_all_counts

CYCLE_ORDER = ["north", "south", "east", "west"]
MIN_GREEN = 5
MAX_GREEN = 60
TIME_PER_VEHICLE = 2  # Seconds per car

def calculate_dynamic_duration(direction):
    """
    Calculates Green Time based on vehicle count.
    """
    counts = get_all_counts()
    count = counts.get(direction, 0)
    
    if count <= 0:
        return MIN_GREEN

    duration = MIN_GREEN + (count * TIME_PER_VEHICLE)
    return max(MIN_GREEN, min(duration, MAX_GREEN))

def get_next_valid_direction(current_direction):
    """
    Finds next lane, SKIPPING lanes with 0 cars.
    """
    counts = get_all_counts()
    try:
        current_idx = CYCLE_ORDER.index(current_direction)
    except:
        current_idx = -1

    for i in range(1, 5):
        next_idx = (current_idx + i) % 4
        next_dir = CYCLE_ORDER[next_idx]
        
        # If lane has cars, pick it
        if counts.get(next_dir, 0) > 0:
            return next_dir
    
    # Fallback
    return CYCLE_ORDER[(current_idx + 1) % 4]