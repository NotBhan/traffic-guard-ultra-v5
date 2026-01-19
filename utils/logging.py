# utils/logger.py

from utils.helpers import current_timestamp


def log_info(message):
    print(f"[INFO] {current_timestamp()} | {message}")


def log_warning(message):
    print(f"[WARN] {current_timestamp()} | {message}")


def log_error(message):
    print(f"[ERROR] {current_timestamp()} | {message}")
