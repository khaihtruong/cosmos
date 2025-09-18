import time
from ..extensions import db

class ChatWindow(db.Model):
    """Represents a time-bounded chat window created by a clinician for a patient"""
    __tablename__ = 'chat_windows'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Float, nullable=False)  # Unix timestamp
    end_date = db.Column(db.Float, nullable=False)    # Unix timestamp
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Float, default=lambda: time.time())
    updated_at = db.Column(db.Float, onupdate=lambda: time.time())

    # Relationships
    patient = db.relationship('User', foreign_keys=[patient_id], backref='chat_windows')
    provider = db.relationship('User', foreign_keys=[provider_id])
    templates = db.relationship('ChatTemplate', backref='window', lazy='dynamic', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='chat_window', lazy='dynamic')

    def is_current(self):
        """Check if this window is currently active based on date"""
        now = time.time()
        return self.is_active and self.start_date <= now <= self.end_date

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'provider_id': self.provider_id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'is_current': self.is_current(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class ChatTemplate(db.Model):
    """Predefined chat configuration within a window"""
    __tablename__ = 'chat_templates'

    id = db.Column(db.Integer, primary_key=True)
    window_id = db.Column(db.Integer, db.ForeignKey('chat_windows.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.Text)  # Description of what this chat is for
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    system_prompt_id = db.Column(db.Integer, db.ForeignKey('system_prompts.id'), nullable=True)
    custom_system_prompt = db.Column(db.Text)  # If not using a predefined prompt
    max_messages = db.Column(db.Integer)  # Optional limit on messages in this chat
    order_index = db.Column(db.Integer, default=0)  # Display order
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Float, default=lambda: time.time())

    # Relationships
    model = db.relationship('Model')
    system_prompt = db.relationship('SystemPrompt')

    def get_system_prompt_content(self):
        """Get the actual system prompt content to use"""
        base_content = ""

        # Start with the selected system prompt
        if self.system_prompt:
            base_content = self.system_prompt.content

        # Add custom instructions if provided
        if self.custom_system_prompt and self.custom_system_prompt.strip():
            if base_content:
                # Combine base prompt with custom instructions
                base_content = f"{base_content}\n\nAdditional Instructions: {self.custom_system_prompt.strip()}"
            else:
                # Use only custom instructions if no base prompt selected
                base_content = self.custom_system_prompt.strip()

        return base_content if base_content else None

    def to_dict(self):
        return {
            'id': self.id,
            'window_id': self.window_id,
            'title': self.title,
            'purpose': self.purpose,
            'model': self.model.name if self.model else None,
            'model_id': self.model_id,
            'system_prompt_id': self.system_prompt_id,
            'custom_system_prompt': self.custom_system_prompt,
            'max_messages': self.max_messages,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'created_at': self.created_at
        }