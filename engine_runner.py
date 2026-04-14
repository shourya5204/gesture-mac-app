import os
import sys
import time
from pathlib import Path
from tempfile import gettempdir

os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"
os.environ["MPLCONFIGDIR"] = "/tmp"

from actions import feedback, scroll_down, scroll_up, swipe_left, swipe_right
from gesture_engine import GestureEngine
from tracker import HandTracker, HandTrackerError


def configure_logging():
    preferred_dir = Path.home() / "Library" / "Logs" / "AirControl"
    fallback_dir = Path(gettempdir()) / "AirControl"

    for directory in (preferred_dir, fallback_dir):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            log_file = directory / "air_control.log"
            log_stream = open(log_file, "a", buffering=1)
            sys.stdout = log_stream
            sys.stderr = log_stream
            print(f"Logging to {log_file}")
            return log_file
        except OSError:
            continue

    return None


def run_engine(stop_event=None, status_callback=None):
    def emit_status(message):
        print(message)
        if status_callback:
            status_callback(message)

    emit_status("Air Control engine starting")

    try:
        tracker = HandTracker()
        emit_status("Camera initialized")
    except HandTrackerError as exc:
        emit_status(f"Startup failed: {exc}")
        return 1

    engine = GestureEngine()

    try:
        while stop_event is None or not stop_event.is_set():
            try:
                hand = tracker.get_hand()
            except Exception as exc:
                emit_status(f"Hand tracking error: {exc}")
                time.sleep(0.1)
                continue

            if not hand:
                time.sleep(0.01)
                continue

            try:
                gesture = engine.update(hand)
            except Exception as exc:
                emit_status(f"Gesture error: {exc}")
                time.sleep(0.1)
                continue

            if gesture == "SCROLL_UP":
                scroll_up()
            elif gesture == "SCROLL_DOWN":
                scroll_down()
            elif gesture == "LEFT":
                swipe_left()
                feedback()
            elif gesture == "RIGHT":
                swipe_right()
                feedback()

            time.sleep(0.01)

    except Exception as exc:
        emit_status(f"Fatal error: {exc}")
        return 1
    finally:
        try:
            tracker.release()
        except Exception:
            pass
        emit_status("Engine stopped")

    return 0
