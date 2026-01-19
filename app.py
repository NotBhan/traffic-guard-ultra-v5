# app.py

from flask import Flask, render_template, Response, jsonify, request
import atexit

# Core Logic
from core.mode_manager import get_current_mode, set_mode, get_arduino_status, set_arduino_status
from core.traffic_state import get_all_counts, get_current_green

# Pipeline Modules
from camera.video_feed import start_video_feeds, stop_video_feeds
from core.detection_service import DetectionService
from core.signal_controller import TrafficController, get_remaining_time
from camera.mjpeg_stream import generate_stream
from hardware.arduino_serial import send_signal_to_arduino

app = Flask(__name__)

# -------------------------------
# START PIPELINE
# -------------------------------
print("⚡ Starting Pipelined System...")

# 1. Start Video Threads (Producer)
is_sim = (get_current_mode() == "simulation")
start_video_feeds(is_simulation=is_sim)

# 2. Start Detection Service (Consumer 1)
detection_service = DetectionService()
detection_service.start()

# 3. Start Traffic Controller (Consumer 2)
traffic_controller = TrafficController()
traffic_controller.start()


# CLEANUP
def cleanup():
    print("Shutting down pipeline...")
    stop_video_feeds()
    detection_service.stop()
    traffic_controller.stop()

atexit.register(cleanup)

VALID_DIRECTIONS = {"north", "south", "east", "west"}

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html", mode=get_current_mode(), arduino=get_arduino_status())

@app.route("/api/status")
def get_status():
    return jsonify({
        "mode": get_current_mode(),
        "arduino": get_arduino_status(),
        "current_direction": get_current_green(),
        "remaining_time": get_remaining_time(),
        "counts": get_all_counts()
    })

@app.route("/stream/<direction>")
def stream(direction):
    if direction not in VALID_DIRECTIONS: return "Error", 404
    return Response(generate_stream(direction), mimetype="multipart/x-mixed-replace; boundary=frame")

# ... (Existing mode/manual routes remain the same) ...
@app.route("/set_mode", methods=["POST"])
def change_mode():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode")
    if mode in ["simulation", "live"]:
        # Restart feeds based on new mode
        stop_video_feeds()
        set_mode(mode)
        start_video_feeds(is_simulation=(mode == "simulation"))
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route("/set_arduino", methods=["POST"])
def set_arduino():
    data = request.get_json(silent=True) or {}
    set_arduino_status(data.get("enabled", False))
    return jsonify({"status": "success"})

@app.route("/manual_control", methods=["POST"])
def manual_control():
    data = request.get_json(silent=True) or {}
    if get_current_mode() == "simulation" and get_arduino_status():
        try:
            send_signal_to_arduino(data.get("direction"), data.get("color"))
        except: pass
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)