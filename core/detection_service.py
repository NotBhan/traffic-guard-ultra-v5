# core/detection_service.py

import time
import threading
from camera.video_feed import get_latest_frame
from core.vehicle_counter import count_vehicles
from core.traffic_state import update_count

class DetectionService(threading.Thread):
    """
    Background service that continuously:
    1. Grabs latest resized frame
    2. Counts vehicles
    3. Updates traffic state
    """
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        print("[AI] Detection Service Started")
        
        directions = ["north", "south", "east", "west"]
        
        while self.running:
            start_time = time.time()

            for d in directions:
                # 1. GET FRAME (Instant)
                frame = get_latest_frame(d)
                
                if frame is not None:
                    # 2. RUN DETECTION (Heavy Task)
                    # Running this in background keeps Video & Timer smooth
                    count = count_vehicles(frame)
                    
                    # 3. UPDATE STATE
                    update_count(d, count)
            
            # Throttle Detection
            # We don't need 30 FPS detection. 10 FPS is enough for traffic.
            # This saves massive CPU overhead.
            elapsed = time.time() - start_time
            if elapsed < 0.1:
                time.sleep(0.1 - elapsed)

    def stop(self):
        self.running = False