# camera/video_feed.py

import cv2
import time
import threading
from threading import Lock

# -------------------------------
# CONFIG
# -------------------------------
VIDEO_FILES = {
    "north": "videos/north.mp4",
    "south": "videos/south.mp4",
    "east": "videos/east.mp4",
    "west": "videos/west.mp4",
}

# The single "source of truth" for frames
# Format: { "north": resized_frame_array, ... }
_latest_frames = {}
_frame_lock = Lock()

# Control flags
_active_threads = {}
_stop_event = threading.Event()


class VideoStreamWorker(threading.Thread):
    """
    Worker thread that:
    1. Reads 4K Video
    2. Resizes to 360p IMMEDIATELY
    3. Updates the global buffer
    """
    def __init__(self, direction, source_path, is_live=False):
        super().__init__()
        self.direction = direction
        self.source = source_path
        self.is_live = is_live
        self.daemon = True

    def run(self):
        global _latest_frames
        print(f"[VIDEO] Starting worker for {self.direction}")
        
        cap = cv2.VideoCapture(self.source)
        # Buffer optimization
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # FPS Sync
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 120: fps = 30.0
        interval = 1.0 / fps

        while not _stop_event.is_set():
            start = time.time()

            # 1. READ (Decoding)
            success, frame = cap.read()

            # Handle Loop / Reconnect
            if not success:
                if not self.is_live:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(1)
                    cap = cv2.VideoCapture(self.source) # Reconnect live
                    continue

            # 2. RESIZE (CPU Optimization)
            # We resize ONCE here, so Detection & Stream don't have to.
            # Using INTER_NEAREST for speed.
            try:
                frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_NEAREST)
            except:
                continue

            # 3. UPDATE SHARED BUFFER
            with _frame_lock:
                _latest_frames[self.direction] = frame

            # 4. SYNC (Don't consume 100% CPU)
            elapsed = time.time() - start
            delay = interval - elapsed
            if delay > 0:
                time.sleep(delay)

        cap.release()


def start_video_feeds(is_simulation=True):
    """
    Initializes all 4 video threads.
    """
    global _active_threads, _stop_event
    _stop_event.clear()

    directions = ["north", "south", "east", "west"]

    for d in directions:
        # Determine source
        src = 0 if (d == "north" and not is_simulation) else VIDEO_FILES.get(d)
        is_live = (src == 0)
        
        if src is None: continue

        # Start Thread
        if d not in _active_threads:
            worker = VideoStreamWorker(d, src, is_live)
            worker.start()
            _active_threads[d] = worker


def get_latest_frame(direction):
    """
    Instant retrieval from memory. No processing cost.
    """
    with _frame_lock:
        return _latest_frames.get(direction)


def stop_video_feeds():
    _stop_event.set()