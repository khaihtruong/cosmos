import time
import threading
from datetime import datetime
from llm_chat.models import ChatWindow, Report
from llm_chat.extensions import db
from report.unified_report_generator import UnifiedReportGenerator


class ReportScheduler:
    """Scheduler to check for completed windows and generate reports"""

    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.thread = None
        self.check_interval = 60  # Check every minute for testing (change to 3600 for production)

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app

    def start(self):
        """Start the scheduler in a background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("Report scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Report scheduler stopped")

    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                with self.app.app_context():
                    self.check_and_generate_reports()
            except Exception as e:
                print(f"Error in report scheduler: {e}")

            # Sleep for the check interval
            time.sleep(self.check_interval)

    def check_and_generate_reports(self):
        """Check for completed windows and generate reports"""
        now = time.time()

        print(f"Checking for completed windows at {datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')}")

        # Find windows that have ended but don't have reports yet
        windows = ChatWindow.query.filter(
            ChatWindow.end_date <= now,
            ChatWindow.is_active == True
        ).all()

        print(f"Found {len(windows)} windows that have ended and are still active")

        for window in windows:
            print(f"Processing window {window.id}: {window.title} (ended: {datetime.fromtimestamp(window.end_date).strftime('%Y-%m-%d %H:%M:%S')})")

            # Check if any report already exists for this window
            existing_report = Report.query.filter_by(window_id=window.id).first()

            if not existing_report:
                try:
                    # Generate unified report with window's configuration
                    print(f"Generating unified report for window {window.id}")
                    report = UnifiedReportGenerator.save_report(window.id)
                    print(f"✓ Generated unified report for window {window.id}: {window.title}")

                    # Mark window as inactive after report generation
                    window.is_active = False
                    db.session.commit()
                    print(f"✓ Marked window {window.id} as inactive")

                except Exception as e:
                    print(f"✗ Failed to generate unified report for window {window.id}: {e}")
                    print(f"Exception details: {type(e).__name__}: {str(e)}")
                    db.session.rollback()
            else:
                print(f"Report already exists for window {window.id}")

    @staticmethod
    def generate_report_for_window(window_id: int):
        """Manually generate a unified report for a specific window"""
        try:
            report = UnifiedReportGenerator.save_report(window_id)
            return report
        except Exception as e:
            print(f"Error generating unified report for window {window_id}: {e}")
            raise


# Global scheduler instance
report_scheduler = ReportScheduler()