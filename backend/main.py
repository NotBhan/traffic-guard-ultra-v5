# ============================================================
# main.py - 4-WAY INTEGRATED + VIOLATION LOGGING
# ============================================================
import asyncio
import json
import cv2
import websockets
import time
import serial
import os
import base64
import numpy as np

from config import PORT, SOURCES, DIRECTIONS, ARDUINO_PORT, BAUD_RATE
from detector import VehicleDetector
from controller import TrafficController

# --- HARDWARE ---
class ArduinoController:
    def __init__(self, port, baud):
        self.ser = None
        self.port = port
        self.baud = baud
        self.connect()

    def connect(self):
        try:
            if self.ser: self.ser.close()
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            time.sleep(2)
            print(f"[ARDUINO] ✅ Connected on {self.port}")
        except Exception as e:
            print(f"[ARDUINO] ⚠️ Connection failed: {e}")
            self.ser = None

    def write(self, packet):
        if self.ser is None:
            self.connect()
            if self.ser is None: return 
        try:
            self.ser.write(packet.encode())
        except Exception:
            self.connect()

arduino = ArduinoController(ARDUINO_PORT, BAUD_RATE)
detector = VehicleDetector()
controller = TrafficController()

# --- PACKET GEN ---
def get_arduino_packet(signal_map):
    parts = []
    def get_code(state):
        if state == "GREEN": return "001"
        if state == "YELLOW": return "010"
        return "100" # RED

    # Order: 1=N, 2=E, 3=S, 4=W
    parts.append(f"1{get_code(signal_map.get('north'))}")
    parts.append(f"2{get_code(signal_map.get('east'))}")
    parts.append(f"3{get_code(signal_map.get('south'))}")
    parts.append(f"4{get_code(signal_map.get('west'))}")

    return f"<{','.join(parts)}>\n"

def open_capture(cfg):
    src = cfg.get("value")
    if cfg.get("type") == "video" and not os.path.exists(src): return None
    cap = cv2.VideoCapture(src)
    return cap if cap.isOpened() else None

def generate_black_frame(text="NO SIGNAL"):
    img = np.zeros((360, 640, 3), dtype=np.uint8)
    cv2.putText(img, text, (180, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return img

# --- MAIN LOOP ---
caps = {}

async def broadcast_loop():
    print(f"[SYSTEM] Backend Active on Port {PORT}...")
    frame_counter = 0
    last_sync = 0
    
    last_counts = {d: 0 for d in DIRECTIONS}
    last_counts["rain_trigger"] = 0
    last_feeds = {}
    last_night = False
    
    while True:
        try:
            # 1. CAPTURE
            frames = {}
            for d in DIRECTIONS:
                if d not in caps or caps[d] is None or not caps[d].isOpened():
                    caps[d] = open_capture(SOURCES[d])
                
                cap = caps.get(d)
                frame = None
                if cap:
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                
                if frame is None: frames[d] = generate_black_frame(f"{d} LOST")
                else: frames[d] = frame

            # 2. DETECT
            violation_event = None
            if frame_counter % 3 == 0:
                try:
                    counts, feeds, is_emerg, _, analytics, stalled, is_night = detector.analyze_frames(frames)
                    last_counts, last_feeds, last_night = counts, feeds, is_night
                except: counts, feeds = last_counts, last_feeds
            else:
                counts, feeds, is_night = last_counts, last_feeds, last_night
                for d, fr in frames.items():
                    _, buffer = cv2.imencode('.jpg', cv2.resize(fr, (640, 360)))
                    feeds[d] = base64.b64encode(buffer).decode('utf-8')
            frame_counter += 1

            # 3. LOGIC
            cmd = manual_command_queue.pop(0) if manual_command_queue else None
            if cmd: controller.handle_manual_command(cmd)

            logic_status = controller.update(counts, False, None)

            # --- VIOLATION LOGIC ---
            # If Signal is RED but ROI count > 0 -> Violation
            # We throttle this to avoid spamming 50 logs for one car
            for d in DIRECTIONS:
                if logic_status["signal_map"][d] == "RED":
                    # Check if 'roi_vehicles' count (from detector.py) > 0
                    roi_count = counts.get("roi_vehicles", {}).get(d, 0)
                    
                    # Simple throttle: only log every 20 frames if violation persists
                    if roi_count > 0 and frame_counter % 20 == 0: 
                        violation_event = {
                            "id": int(time.time()*1000),
                            "dir": d,
                            "time": time.strftime("%H:%M:%S"),
                            "img": feeds.get(d) # Send snapshot
                        }

            # 4. HARDWARE
            if time.time() - last_sync >= 1.0:
                arduino.write(get_arduino_packet(logic_status["signal_map"]))
                last_sync = time.time()

            # 5. SEND
            weather = "RAIN" if counts.get("rain_trigger") else ("NIGHT" if is_night else "CLEAR")
            
            payload = {
                "feeds": feeds, 
                "counts": counts, 
                "logic": logic_status,
                "wait_times": logic_status.get("wait_times", {}),
                "analytics": analytics,
                "env": {
                    "obstacle_zone": stalled, 
                    "is_night": is_night, 
                    "weather_mode": weather
                },
            }
            
            # Append Violation if exists (Frontend expects 'violation' key)
            if violation_event:
                payload["violation"] = violation_event

            if clients:
                await asyncio.gather(*[c.send(json.dumps(payload)) for c in clients], return_exceptions=True)

        except Exception as e:
            print(f"[ERROR] {e}")
            await asyncio.sleep(1)
        await asyncio.sleep(0.02)

# --- SERVER ---
clients = set()
manual_command_queue = []

async def ws_handler(ws):
    clients.add(ws)
    try:
        async for msg in ws:
            data = json.loads(msg)
            if "command" in data: manual_command_queue.append(data["command"])
    finally: clients.remove(ws)

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", PORT):
        await broadcast_loop()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass