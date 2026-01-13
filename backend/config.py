# ============================================================
# config.py - FINAL 4-WAY CONFIGURATION
# ============================================================
import os

# 1. PATH SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "videos")

# 2. HARDWARE
ARDUINO_PORT = "/dev/ttyUSB0" 
BAUD_RATE = 115200

# 3. DIRECTIONS (ALL 4 LANES)
DIRECTIONS = ["north", "east", "south", "west"]

# 4. SERVER
PORT = 5500

# 5. VIDEO SOURCES
# Ensure these files exist in backend/videos/ or use Camera IDs (0, 1, 2)
SOURCES = {
    "north": {
        "type": "camera", 
        "value": "rtsp://admin:123456@192.168.0.55:554/profile2"
    },
    # "north":  {"type": "video", "value": os.path.join(VIDEO_DIR, "north.mp4")},
    "east":  {"type": "video", "value": os.path.join(VIDEO_DIR, "east.mp4")},
    "south": {"type": "video", "value": os.path.join(VIDEO_DIR, "south.mp4")},
    "west":  {"type": "video", "value": os.path.join(VIDEO_DIR, "west.mp4")},
}

# 6. TIMING
TIME_SLOTS = {"low": 10, "medium": 20, "high": 30}
YELLOW_TIME = 4       
SAFETY_YELLOW_TIME = 6
RED_HOLD_TIME = 2      # Safety buffer

# 7. YOLO MODEL
MODEL_NAME = "yolov8n.pt"
CLASS_MAP = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
VEHICLE_CLASSES = list(CLASS_MAP.keys())
EMERGENCY_CLASSES = [5]
RAIN_CLASS = 25
PERSON_CLASS = 0

# 8. ROI RECTANGLES (For Violation Detection)
# [x1, y1, x2, y2] - Define the "Stop Line" area for each camera
ROI_RECTS = {
    "north": (220, 140, 420, 260),
    "east":  (360, 220, 620, 340),
    "south": (220, 260, 420, 380),
    "west":  (0, 220, 280, 340),
}

# 9. THRESHOLDS
NIGHT_BRIGHTNESS_THRESHOLD = 50 
STALLED_COUNT_THRESHOLD = 8
STALLED_FRAME_LIMIT = 30