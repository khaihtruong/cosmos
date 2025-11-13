import json
import time
from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user
from ..utils.decorators import role_required
from ..extensions import db
from ..models import (
    User, ProviderPatient, Conversation, Message,
    AdminSettings, UserSettings
)

admin_bp = Blueprint("admin", __name__, url_prefix="")

@admin_bp.route("/admin/dashboard")
@role_required('admin')
def admin_dashboard():
    return render_template("admin_dashboard.html")

@admin_bp.route("/api/admin/users")
@role_required('admin')
def get_all_users():
    users = User.query.all()
    user_data = []
    for u in users:
        if u.role == 'user':
            conversation_count = Conversation.query.filter_by(user_id=u.id).count()
        elif u.role == 'provider':
            assigned_patients = ProviderPatient.query.filter_by(provider_id=u.id).all()
            patient_ids = [pp.patient_id for pp in assigned_patients]
            conversation_count = Conversation.query.filter(Conversation.user_id.in_(patient_ids)).count() if patient_ids else 0
        else:
            conversation_count = 0
        user_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'visible': u.visible,
            'created_at': u.created_at,
            'conversation_count': conversation_count
        })
    return jsonify(user_data)

@admin_bp.route("/api/admin/stats")
@role_required('admin')
def get_admin_stats():
    total_users = User.query.count()
    total_providers = User.query.filter_by(role='provider').count()
    total_patients = User.query.filter_by(role='user').count()
    total_conversations = Conversation.query.count()
    return jsonify({
        'total_users': total_users,
        'total_providers': total_providers,
        'total_patients': total_patients,
        'total_conversations': total_conversations
    })

@admin_bp.route("/api/admin/user", methods=['POST'])
@role_required('admin')
def create_user():
    data = request.json or {}
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    user = User(username=data['username'], email=data['email'], role=data['role'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@admin_bp.route("/api/admin/assign_provider", methods=['POST'])
@role_required('admin')
def assign_provider():
    data = request.json or {}
    existing = ProviderPatient.query.filter_by(
        provider_id=data['provider_id'], patient_id=data['patient_id']
    ).first()
    if existing:
        return jsonify({'error': 'Assignment already exists'}), 400
    assignment = ProviderPatient(
        provider_id=data['provider_id'],
        patient_id=data['patient_id'],
        assigned_by=current_user.id  # needs current_user; route is admin-protected
    )
    db.session.add(assignment)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route("/api/admin/provider/<int:provider_id>/patients")
@role_required('admin')
def admin_get_provider_patients(provider_id):
    assignments = ProviderPatient.query.filter_by(provider_id=provider_id).all()
    patient_ids = [a.patient_id for a in assignments]
    patients = User.query.filter(User.id.in_(patient_ids)).all() if patient_ids else []

    def last_active_for(u: User):
        conv = Conversation.query.filter_by(user_id=u.id).order_by(Conversation.updated_at.desc()).first()
        return conv.updated_at if conv else None

    data = []
    for patient in patients:
        conversation_count = Conversation.query.filter_by(user_id=patient.id).count()
        data.append({
            'id': patient.id,
            'username': patient.username,
            'email': patient.email,
            'conversation_count': conversation_count,
            'last_active': last_active_for(patient),
        })
    return jsonify(data)

@admin_bp.route("/api/admin/user/<int:user_id>/conversations")
@role_required('admin')
def get_user_conversations(user_id):
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.created_at.desc()).all()
    payload = []
    for conv in conversations:
        message_count = Message.query.filter_by(conversation_id=conv.id).count()
        payload.append({
            'id': conv.id,
            'title': conv.title,
            'model': conv.model.name if conv.model else None,
            'created_at': conv.created_at,  # (monolith had .timestamp(); fixed: these are floats)
            'updated_at': conv.updated_at,
            'message_count': message_count
        })
    return jsonify(payload)

@admin_bp.route("/api/admin/assignments")
@role_required('admin')
def get_provider_assignments():
    assignment_data = []
    for assignment in ProviderPatient.query.all():
        provider = User.query.get(assignment.provider_id)
        patient = User.query.get(assignment.patient_id)
        assigned_by = User.query.get(assignment.assigned_by)
        assignment_data.append({
            'id': assignment.id,
            'provider_id': assignment.provider_id,
            'provider_name': provider.username if provider else 'Unknown',
            'patient_id': assignment.patient_id,
            'patient_name': patient.username if patient else 'Unknown',
            'assigned_by': assigned_by.username if assigned_by else 'Unknown',
            'created_at': assignment.assigned_at  # (monolith used created_at.timestamp(); fixed)
        })
    return jsonify(assignment_data)

@admin_bp.route("/api/admin/assignment/<int:assignment_id>", methods=['DELETE'])
@role_required('admin')
def remove_assignment(assignment_id):
    assignment = ProviderPatient.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route("/api/admin/settings")
@role_required('admin')
def get_admin_settings():
    settings = AdminSettings.query.all()
    settings_dict = {}
    for setting in settings:
        try:
            settings_dict[setting.setting_name] = json.loads(setting.setting_value) if setting.setting_value else None
        except Exception:
            settings_dict[setting.setting_name] = setting.setting_value
    return jsonify(settings_dict)

@admin_bp.route("/api/admin/settings", methods=['POST'])
@role_required('admin')
def update_admin_settings():
    data = request.json or {}
    for setting_name, setting_value in data.items():
        existing = AdminSettings.query.filter_by(setting_name=setting_name).first()
        value = json.dumps(setting_value) if isinstance(setting_value, (dict, list)) else str(setting_value)
        if existing:
            existing.setting_value = value
            existing.updated_at = time.time()
        else:
            db.session.add(AdminSettings(setting_name=setting_name, setting_value=value))
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route("/api/admin/user/<int:user_id>/settings")
@role_required('admin')
def get_user_settings(user_id):
    user_settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not user_settings:
        return jsonify({
            'user_id': user_id,
            'allowed_models': [],
            'blocked_models': [],
            'can_use_custom_prompts': True,
            'can_save_selections': True,
            'max_conversations_per_day': None,
            'max_messages_per_conversation': None,
            'visible': True
        })
    return jsonify({
        'user_id': user_settings.user_id,
        'allowed_models': json.loads(user_settings.allowed_models) if user_settings.allowed_models else [],
        'blocked_models': json.loads(user_settings.blocked_models) if user_settings.blocked_models else [],
        'can_use_custom_prompts': user_settings.can_use_custom_prompts,
        'can_save_selections': user_settings.can_save_selections,
        'max_conversations_per_day': user_settings.max_conversations_per_day,
        'max_messages_per_conversation': user_settings.max_messages_per_conversation,
        'visible': user_settings.visible
    })

@admin_bp.route("/api/admin/user/<int:user_id>/settings", methods=['POST'])
@role_required('admin')
def update_user_settings(user_id):
    data = request.json or {}
    user_settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=user_id)
        db.session.add(user_settings)

    if 'allowed_models' in data:
        user_settings.allowed_models = json.dumps(data['allowed_models'])
    if 'blocked_models' in data:
        user_settings.blocked_models = json.dumps(data['blocked_models'])
    if 'can_use_custom_prompts' in data:
        user_settings.can_use_custom_prompts = data['can_use_custom_prompts']
    if 'can_save_selections' in data:
        user_settings.can_save_selections = data['can_save_selections']
    if 'max_conversations_per_day' in data:
        user_settings.max_conversations_per_day = data['max_conversations_per_day']
    if 'max_messages_per_conversation' in data:
        user_settings.max_messages_per_conversation = data['max_messages_per_conversation']
    if 'visible' in data:
        user_settings.visible = data['visible']
    elif 'is_active' in data:
        user_settings.visible = data['is_active']

    user_settings.updated_at = time.time()
    db.session.commit()
    return jsonify({'status': 'success'})
