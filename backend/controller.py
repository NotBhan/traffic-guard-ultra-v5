# ============================================================
# controller.py - 4-WAY LOGIC (Compatible with New Frontend)
# ============================================================
import time
from config import TIME_SLOTS, YELLOW_TIME, DIRECTIONS, RED_HOLD_TIME

class TrafficController:
    def __init__(self):
        self.state = "GREEN_PHASE"
        self.current_green = "north"
        self.next_green = "east"
        self.last_switch_time = time.time()
        
        self.green_duration = TIME_SLOTS["medium"]
        self.current_yellow_duration = YELLOW_TIME
        
        # Default all to Red
        self.signal_map = {d: "RED" for d in DIRECTIONS}
        self.signal_map["north"] = "GREEN"
        self.mode = "AUTO"
        
        # Cycle Order
        self.cycle_order = ["north", "east", "south", "west"]

    def update(self, counts, is_emergency, manual_command):
        now = time.time()
        elapsed = now - self.last_switch_time

        # 1. EMERGENCY OVERRIDE
        if is_emergency and self.mode != "EMERGENCY":
            self.mode = "EMERGENCY"
            self.last_switch_time = 0 
        elif not is_emergency and self.mode == "EMERGENCY":
            self.mode = "AUTO"

        # 2. STATE MACHINE
        if self.state == "GREEN_PHASE":
            if elapsed >= self.green_duration:
                self.state = "YELLOW_PHASE"
                self.last_switch_time = now
                self._update_next_green(counts)

        elif self.state == "YELLOW_PHASE":
            if elapsed >= self.current_yellow_duration:
                self.state = "RED_PHASE"
                self.last_switch_time = now

        elif self.state == "RED_PHASE":
            if elapsed >= RED_HOLD_TIME:
                self.switch_to_next_green(now)

        self._update_signal_map()
        
        # 3. TIMER
        target = 0
        if self.state == "GREEN_PHASE": target = self.green_duration
        elif self.state == "YELLOW_PHASE": target = self.current_yellow_duration
        elif self.state == "RED_PHASE": target = RED_HOLD_TIME
        remaining = int(max(0, target - elapsed))

        # 4. WAIT TIMES
        wait_times = self._calculate_cumulative_wait(remaining)

        # Return Data Structure for Frontend
        return {
            "signal_map": self.signal_map.copy(),
            "timer": remaining,
            "wait_times": wait_times,
            "state": self.state,
            "current_green": self.current_green,
            "mode": self.mode,
            "active_dir": self.current_green, # REQUIRED by TrafficGrid.jsx
            "next_dir": self.next_green       # REQUIRED by StatusBar.jsx
        }

    def _calculate_cumulative_wait(self, current_timer):
        waits = {}
        try: idx = self.cycle_order.index(self.current_green)
        except: idx = 0
        
        step = TIME_SLOTS["medium"] + YELLOW_TIME + RED_HOLD_TIME
        
        # Base accumulation
        cumulative = current_timer
        if self.state == "GREEN_PHASE":
             cumulative += (YELLOW_TIME + RED_HOLD_TIME)

        # Calculate forward
        for i in range(1, 4):
            next_idx = (idx + i) % 4
            next_dir = self.cycle_order[next_idx]
            waits[next_dir] = int(cumulative)
            cumulative += step

        # Current green lane is 0 (or full cycle if red)
        waits[self.current_green] = 0 if self.state == "GREEN_PHASE" else int(cumulative)
        return waits

    def switch_to_next_green(self, now_time):
        self.state = "GREEN_PHASE"
        self.current_green = self.next_green
        self.last_switch_time = now_time

    def handle_manual_command(self, command):
        # FIX: Handle UPPERCASE commands from Frontend
        cmd = command.lower() 
        if cmd == "auto": 
            self.mode = "AUTO"
            return
        
        if cmd == "stop_all":
            self.mode = "MANUAL"
            self.state = "RED_PHASE"
            # Force all Red
            for d in DIRECTIONS: self.signal_map[d] = "RED"
            return

        target = cmd.replace("force_", "")
        if target in DIRECTIONS:
            self.mode = "MANUAL"
            self.last_switch_time = 0
            self.next_green = target
            # If we force a direction, jump to Red Phase to transition safely
            if self.current_green != target:
                self.state = "RED_PHASE" 

    def _update_next_green(self, counts):
        if self.mode == "AUTO":
            curr_idx = self.cycle_order.index(self.current_green)
            self.next_green = self.cycle_order[(curr_idx + 1) % 4]
            self._adjust_green_duration(counts, self.next_green)

    def _adjust_green_duration(self, counts, next_dir):
        count = counts.get(next_dir, 0)
        if count < 5: self.green_duration = TIME_SLOTS["low"]
        elif count < 15: self.green_duration = TIME_SLOTS["medium"]
        else: self.green_duration = TIME_SLOTS["high"]

    def _update_signal_map(self):
        for d in DIRECTIONS: self.signal_map[d] = "RED"
        if self.state == "GREEN_PHASE": self.signal_map[self.current_green] = "GREEN"
        elif self.state == "YELLOW_PHASE": self.signal_map[self.current_green] = "YELLOW"