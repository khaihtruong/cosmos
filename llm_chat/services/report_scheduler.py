import time
import threading
from llm_chat.services.report_utils import finalize_expired_windows


class ReportScheduler:
    """Background scheduler that checks chat windows every 5 minutes."""

    def __init__(self, app=None, interval_seconds: int = 300):
        self.app = app
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None

    def init_app(self, app):
        self.app = app

    def start(self):
        if self.running or not self.app:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("Report scheduler started (5-minute interval)")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None

    def _run(self):
        while self.running:
            try:
                with self.app.app_context():
                    processed = finalize_expired_windows()
                    if processed:
                        print(f"Report scheduler processed windows: {processed}")
            except Exception as exc:
                print(f"Report scheduler error: {exc}")
            time.sleep(self.interval_seconds)


report_scheduler = ReportScheduler()
