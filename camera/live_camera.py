# camera/live_camera.py

import cv2
from threading import Lock

# -------------------------------
# SINGLE CAMERA INSTANCE
# -------------------------------
_camera = None
_lock = Lock()


def get_live_camera(direction=None):
    """
    Returns a singleton VideoCapture object.
    direction parameter is ignored for now
    (extend later for multi-camera setup)
    """
    global _camera

    with _lock:
        if _camera is None or not _camera.isOpened():
            _camera = cv2.VideoCapture(0)
            _camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            _camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        return _camera
