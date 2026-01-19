# core/vehicle_counter.py

import cv2
import numpy as np

# -------------------------------
# CONFIGURATION
# -------------------------------
# Optimized for 640x360 resolution
MIN_VEHICLE_AREA = 500  
MAX_VEHICLE_AREA = 15000

# Background Subtractor
# detectShadows=True is critical for accuracy but slightly slower.
# Since we pipeline, we can afford it now.
_bg = cv2.createBackgroundSubtractorMOG2(
    history=500,
    varThreshold=25,
    detectShadows=True
)

_WARMUP_FRAMES = 10
_frame_index = 0

def count_vehicles(frame):
    """
    Pure Detection Logic. No drawing/visuals.
    Returns: integer count
    """
    global _frame_index
    _frame_index += 1

    if frame is None:
        return 0

    # 1. PRE-PROCESS
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. SUBTRACT BACKGROUND
    mask = _bg.apply(blurred)

    # 3. SHADOW REMOVAL & CLEANING
    _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # Warmup
    if _frame_index < _WARMUP_FRAMES:
        return 0

    # 4. COUNT OBJECTS
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Filter by Size
        if MIN_VEHICLE_AREA < area < MAX_VEHICLE_AREA:
            # Filter by Shape (Aspect Ratio)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = float(w) / h
            if 0.2 < aspect < 4.0:
                count += 1
                # NO cv2.rectangle calls here!

    return count