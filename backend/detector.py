# ============================================================
# detector.py - Fixed Resolution (16:9)
# ============================================================
import base64
import cv2
import numpy as np
from ultralytics import YOLO
from config import (
    MODEL_NAME, VEHICLE_CLASSES, CLASS_MAP, RAIN_CLASS, PERSON_CLASS,
    DIRECTIONS, EMERGENCY_CLASSES, NIGHT_BRIGHTNESS_THRESHOLD,
    STALLED_COUNT_THRESHOLD, STALLED_FRAME_LIMIT, ROI_RECTS
)

class VehicleDetector:
    def __init__(self):
        print(f"[INFO] Loading YOLO model: {MODEL_NAME}")
        self.model = YOLO(MODEL_NAME)
        self.congest_counter = {d: 0 for d in DIRECTIONS}
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def _encode_frame_to_base64(self, frame):
        if frame is None: return None
        
        # FIX: Standardize to 640x360 (16:9) to match main.py
        target_w, target_h = 640, 360 
        frame = cv2.resize(frame, (target_w, target_h))

        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return base64.b64encode(buffer).decode("utf-8")

    def _enhance_night(self, frame):
        try:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            y, cr, cb = cv2.split(ycrcb)
            y = self.clahe.apply(y)
            ycrcb = cv2.merge([y, cr, cb])
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        except: return frame

    def analyze_frames(self, frames_by_dir):
        counts = {d: 0 for d in DIRECTIONS}
        counts["rain_trigger"] = 0
        roi_vehicles = {d: 0 for d in DIRECTIONS}
        feeds_base64 = {}
        analytics = {"car": 0, "bike": 0, "bus": 0, "truck": 0}
        stalled_zone = None
        global_is_night = False
        emergency_detected = False
        emergency_zone = None

        batch_frames = []
        batch_dirs = []
        
        for d in DIRECTIONS:
            frame = frames_by_dir.get(d)
            if frame is None: continue
            
            # Use smaller size for detection to speed up FPS
            frame_small = cv2.resize(frame, (640, 360))
            
            if not global_is_night:
                hsv = cv2.cvtColor(frame_small, cv2.COLOR_BGR2HSV)
                if np.mean(hsv[:, :, 2]) < NIGHT_BRIGHTNESS_THRESHOLD:
                    global_is_night = True

            if global_is_night:
                frame_small = self._enhance_night(frame_small)

            batch_frames.append(frame_small)
            batch_dirs.append(d)
            feeds_base64[d] = self._encode_frame_to_base64(frame_small)

        results_list = []
        if batch_frames:
            try:
                results_list = self.model(batch_frames, conf=0.35, verbose=False)
            except: pass

        for i, res in enumerate(results_list):
            direction = batch_dirs[i]
            cnt = 0
            if res.boxes:
                for box, cls in zip(res.boxes.xyxy, res.boxes.cls):
                    cid = int(cls)
                    if cid in VEHICLE_CLASSES:
                        cnt += 1
                        vtype = CLASS_MAP.get(cid, "car")
                        if vtype == "motorcycle": vtype = "bike"
                        analytics[vtype] = analytics.get(vtype, 0) + 1
                        
                        rect = ROI_RECTS.get(direction)
                        if rect:
                            cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
                            if rect[0]<=cx<=rect[2] and rect[1]<=cy<=rect[3]:
                                roi_vehicles[direction] += 1
                    elif cid == RAIN_CLASS: counts["rain_trigger"] = 1
                    elif cid in EMERGENCY_CLASSES:
                        emergency_detected = True
                        emergency_zone = direction

            counts[direction] = cnt
            
            if cnt >= STALLED_COUNT_THRESHOLD: self.congest_counter[direction] += 1
            else: self.congest_counter[direction] = 0
            
            if self.congest_counter[direction] >= STALLED_FRAME_LIMIT:
                stalled_zone = direction
            
        counts["roi_vehicles"] = roi_vehicles
        return (counts, feeds_base64, emergency_detected, emergency_zone, analytics, stalled_zone, global_is_night)