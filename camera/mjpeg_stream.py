# camera/mjpeg_stream.py

import cv2
import time
from camera.video_feed import get_latest_frame

def generate_stream(direction):
    """
    Ultra-lightweight Streamer.
    No resizing, no detection, no decoding here.
    Just Encode -> Send.
    """
    while True:
        # 1. GET PRE-PROCESSED FRAME
        frame = get_latest_frame(direction)

        if frame is None:
            # If no frame yet (startup), send a black placeholder
            # or wait briefly
            time.sleep(0.1)
            continue

        # 2. ENCODE
        # Quality 60 is optimal for MJPEG speed
        try:
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame_bytes + b"\r\n"
                )
        except:
            pass

        # 3. SYNC
        # Limit stream to ~30 FPS to save bandwidth
        time.sleep(0.033)