import time
import json
from ..extensions import db


class Report(db.Model):
    """Reports generated at the end of chat windows"""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    window_id = db.Column(db.Integer, db.ForeignKey('chat_windows.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), default='default')  # default, comprehensive, etc.
    report_data = db.Column(db.Text)  # JSON data containing report details
    generated_at = db.Column(db.Float, default=lambda: time.time())
    file_path = db.Column(db.String(255))  # Path to saved report file if applicable

    # Relationships
    window = db.relationship('ChatWindow', backref='reports')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_reports')
    provider = db.relationship('User', foreign_keys=[provider_id])

    def to_dict(self):
        return {
            'id': self.id,
            'window_id': self.window_id,
            'patient_id': self.patient_id,
            'provider_id': self.provider_id,
            'report_type': self.report_type,
            'report_data': json.loads(self.report_data) if self.report_data else {},
            'generated_at': self.generated_at,
            'file_path': self.file_path
        }