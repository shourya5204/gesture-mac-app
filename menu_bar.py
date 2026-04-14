import queue
import threading

import rumps

from engine_runner import configure_logging, run_engine


class EngineWorker:
    def __init__(self, on_status):
        self.on_status = on_status
        self.stop_event = None
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return False

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def _run(self):
        exit_code = run_engine(
            stop_event=self.stop_event,
            status_callback=self.on_status,
        )
        if exit_code != 0:
            self.on_status("Engine exited with an error")

    def stop(self):
        if not self.thread:
            return

        self.stop_event.set()
        self.thread.join(timeout=2)
        self.thread = None
        self.stop_event = None

    def is_running(self):
        return bool(self.thread and self.thread.is_alive())


class AirControlApp(rumps.App):
    def __init__(self):
        super().__init__("Air Control", quit_button=None)
        configure_logging()

        self.status_queue = queue.SimpleQueue()
        self.worker = EngineWorker(self.status_queue.put)
        self.status_item = rumps.MenuItem("Status: Off")
        self.toggle_item = rumps.MenuItem("Toggle")
        self.menu = [
            self.status_item,
            self.toggle_item,
            None,
            "Quit",
        ]
        self.status_timer = rumps.Timer(self._drain_status_queue, 0.2)
        self.status_timer.start()

    def _set_status(self, text):
        self.status_item.title = f"Status: {text}"

    def _handle_status(self, message):
        lowered = message.lower()

        if "camera initialized" in lowered:
            self.title = "● Air Control"
            self._set_status("Running")
            return

        if "startup failed" in lowered:
            self.title = "Air Control"
            self._set_status("Camera Permission Required")
            rumps.notification(
                "Air Control",
                "Camera access is required",
                "Enable camera access in System Settings > Privacy & Security > Camera.",
            )
            return

        if "engine stopped" in lowered:
            self.title = "Air Control"
            if self.status_item.title == "Status: Stopping":
                self._set_status("Off")
            return

        if "error" in lowered:
            self.title = "Air Control"
            self._set_status("Error")
            rumps.notification("Air Control", "Engine error", message)

    def _drain_status_queue(self, _):
        while True:
            try:
                message = self.status_queue.get_nowait()
            except queue.Empty:
                return
            self._handle_status(message)

    @rumps.clicked("Start")
    def toggle_engine(self, _):
        if self.worker.is_running():
            self._set_status("Stopping")
            self.worker.stop()
            self._set_status("Off")
            self.title = "Air Control"
            return

        self._set_status("Starting")
        self.worker.start()

    @rumps.clicked("Quit")
    def quit_app(self, _):
        if self.worker.is_running():
            self._set_status("Stopping")
            self.worker.stop()
        rumps.quit_application()


if __name__ == "__main__":
    AirControlApp().run()
