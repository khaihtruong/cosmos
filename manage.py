import json
import time
from flask import Flask
from sqlalchemy import text
from llm_chat import create_app
from llm_chat.extensions import db
from llm_chat.models import (
    User, ProviderPatient, ProviderSettings, SystemPrompt,
    Model, Conversation
)
from llm_chat.services.llm_interface import LLMInterface

app: Flask = create_app()

def check_and_migrate_database():
    """Minimal, safe check to ensure 'role' exists; uses SQL for SQLite compatibility."""
    with app.app_context():
        try:
            # Try simple query that depends on 'role'
            User.query.filter_by(role='admin').first()
            print("Database schema is up to date")
        except Exception as e:
            msg = str(e)
            if "no such column: users.role" in msg:
                print("Database schema needs migration. Adding new columns...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
                db.session.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL"))
                db.session.commit()
                print("Schema migration completed")
            else:
                print(f"Database error: {e}")
                raise

def initialize_database():
    """Initialize database with default data (idempotent)."""
    with app.app_context():
        db.create_all()
        check_and_migrate_database()

        # Initialize LLM clients once
        LLMInterface.initialize_clients()

        # Create default admin
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created default admin user")

        # Demo provider
        if not User.query.filter_by(username='provider1').first():
            provider = User(username='provider1', email='provider1@example.com', role='provider')
            provider.set_password('provider123')
            db.session.add(provider)
            print("Created demo provider")

        # Demo users
        demo_users = ['user1', 'user2', 'user3']
        for username in demo_users:
            if not User.query.filter_by(username=username).first():
                u = User(username=username, email=f'{username}@example.com', role='user')
                u.set_password('user123')
                db.session.add(u)
                print(f"Created demo user: {username}")

        db.session.commit()

        # Assign provider to demo users
        provider = User.query.filter_by(username='provider1').first()
        admin = User.query.filter_by(role='admin').first()
        if provider and admin:
            for username in demo_users:
                patient = User.query.filter_by(username=username).first()
                if patient and not ProviderPatient.query.filter_by(provider_id=provider.id, patient_id=patient.id).first():
                    db.session.add(ProviderPatient(provider_id=provider.id, patient_id=patient.id, assigned_by=admin.id))
                    print(f"Created provider assignment for {username}")

        # Default models
        if not Model.query.first():
            models = [
                Model(name='GPT-4', provider='openai', model_identifier='gpt-4',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 1000})),
                Model(name='GPT-3.5 Turbo', provider='openai', model_identifier='gpt-3.5-turbo',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 1000})),
                Model(name='Claude 3 Opus', provider='anthropic', model_identifier='claude-3-opus-20240229',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 1000})),
                Model(name='Claude 3.5 Sonnet', provider='anthropic', model_identifier='claude-3-5-sonnet-20241022',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 1000})),
                Model(name='Gemini 1.5 Pro', provider='google', model_identifier='gemini-1.5-pro',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 1000})),
                Model(name='Local Llama', provider='local', api_endpoint='http://localhost:8000/v1/chat/completions',
                      config=json.dumps({'temperature': 0.7, 'max_tokens': 2000})),
            ]
            for m in models:
                db.session.add(m)

        # Default system prompts
        if not SystemPrompt.query.first():
            prompts = [
                SystemPrompt(name='Default Assistant', content='You are a helpful AI assistant. Respond in appropriate chat format.'),
                SystemPrompt(name='Medical Assistant', content='You are a medical AI assistant. Provide helpful health information while reminding users to consult healthcare professionals. Respond in appropriate chat format.'),
                SystemPrompt(name='Mental Health Support', content='You are a supportive mental health companion. Provide empathetic responses and coping strategies. Respond in appropriate chat format.'),
                SystemPrompt(name='Research Assistant', content='You are a research assistant. Provide detailed, well-sourced responses. Respond in appropriate chat format.')
            ]
            for p in prompts:
                db.session.add(p)

        db.session.commit()
        print("Initialization complete.")

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, host="0.0.0.0", port=5001)
