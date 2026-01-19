# core/signal_controller.py

import time
import threading
from core.traffic_state import set_current_green, get_current_green, get_all_counts
from core.timing_logic import calculate_dynamic_duration, get_next_valid_direction
from core.mode_manager import get_arduino_status
from hardware.arduino_serial import send_signal_to_arduino

# GLOBAL SHARED VARIABLE FOR TIMER
# This is what the Dashboard reads.
current_remaining_time = 0

def get_remaining_time():
    """Returns the live countdown value for the API"""
    return current_remaining_time

class TrafficController(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        set_current_green("north") # Start with North

    def run(self):
        global current_remaining_time
        print("🚦 AI Traffic Controller Started")
        
        while self.running:
            # 1. GET CURRENT STATE
            current_green = get_current_green()
            
            # 2. CALCULATE DURATION
            # (e.g., 5s base + 2s per car)
            duration = calculate_dynamic_duration(current_green)
            
            # Update Hardware (Green)
            if get_arduino_status():
                send_signal_to_arduino(current_green, "green")
            
            # 3. COUNTDOWN LOOP (The Timer)
            # We decrement the global variable every second
            current_remaining_time = duration
            while current_remaining_time > 0:
                if not self.running: return
                time.sleep(1)
                current_remaining_time -= 1

            # 4. YELLOW LIGHT
            if get_arduino_status():
                send_signal_to_arduino(current_green, "yellow")
            
            # Hardcoded Yellow duration (not counted in main timer)
            time.sleep(3) 

            # 5. SWITCH SIGNAL
            next_green = get_next_valid_direction(current_green)
            set_current_green(next_green)
            
            # Safety buffer
            time.sleep(1)

    def stop(self):
        self.running = False