import json
import time
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import (
    User, ProviderPatient, ProviderSettings, SystemPrompt,
    Conversation, Model, Message, SavedSelection, ChatWindow
)
from ..services.llm_interface import LLMInterface

conv_bp = Blueprint("conversations", __name__, url_prefix="")

# -------- User dashboards / pages

@conv_bp.route("/dashboard")
@login_required
def user_dashboard():
    if current_user.is_admin():
        return render_template("admin_dashboard.html")
    elif current_user.is_provider():
        return render_template("provider_dashboard.html")
    # For patients, show the new chat windows interface
    return render_template("user_dashboard.html")

@conv_bp.route("/chat-windows")
@login_required
def new_conversation():
    return render_template("user_chat_windows.html")

@conv_bp.route("/my-reports")
@login_required
def patient_reports():
    return render_template("patient_reports.html")

@conv_bp.route("/api/provider_settings")
@login_required
def get_provider_settings_for_current_user():
    """Provider settings as applied to current patient"""
    if not current_user.is_patient():
        return jsonify(None)

    provider_assignment = ProviderPatient.query.filter_by(patient_id=current_user.id).first()
    if not provider_assignment:
        return jsonify(None)

    settings = (ProviderSettings.query.filter_by(
        provider_id=provider_assignment.provider_id,
        patient_id=current_user.id
    ).first() or ProviderSettings.query.filter_by(
        provider_id=provider_assignment.provider_id,
        patient_id=None
    ).first())

    if not settings:
        return jsonify(None)

    return jsonify({
        'allowed_models': json.loads(settings.allowed_models or '[]'),
        'system_prompt_id': settings.system_prompt_id,
        'time_window_start': settings.time_window_start,
        'time_window_end': settings.time_window_end,
        'max_messages_per_day': settings.max_messages_per_day,
        'custom_instructions': settings.custom_instructions
    })

@conv_bp.route("/conversation/<int:conversation_id>")
@login_required
def view_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not current_user.can_access_patient(conversation.user_id):
        abort(403)

    can_send_messages = conversation.user_id == current_user.id
    is_provider = current_user.is_provider()

    # Check if conversation belongs to an expired window
    if conversation.window_id:
        window = ChatWindow.query.get(conversation.window_id)
        if window:
            now = time.time()
            # Can't send messages if window has ended or isn't active
            if now > window.end_date or not window.is_active:
                can_send_messages = False

    return render_template("conversation.html", conversation_id=conversation_id, can_send_messages=can_send_messages, is_provider=is_provider)

@conv_bp.route("/api/conversation/<int:conversation_id>")
@login_required
def get_conversation_data(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if not current_user.can_access_patient(conversation.user_id):
        abort(403)

    messages = conversation.messages.order_by(Message.timestamp).all()

    # Get window info if conversation belongs to a window
    window_end_date = None
    if conversation.window_id:
        window = ChatWindow.query.get(conversation.window_id)
        if window:
            window_end_date = window.end_date

    return jsonify({
        'id': conversation.id,
        'title': conversation.title or 'New Conversation',
        'model': {
            'id': conversation.model.id,
            'name': conversation.model.name
        },
        'system_prompt': None if not conversation.system_prompt_id else {
            'id': conversation.system_prompt_id,
            'name': SystemPrompt.query.get(conversation.system_prompt_id).name if conversation.system_prompt_id else None
        },
        'window_end_date': window_end_date,
        'messages': [m.to_dict() for m in messages]
    })

@conv_bp.route("/api/conversation/<int:conversation_id>/title", methods=["PUT"])
@login_required
def update_conversation_title(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if conversation.user_id != current_user.id:
        abort(403)
    data = request.json or {}
    conversation.title = data.get('title', '').strip()[:200]
    conversation.updated_at = time.time()
    db.session.commit()
    return jsonify({'status': 'success', 'title': conversation.title})

'''
@conv_bp.route("/api/conversations")
@login_required
def get_conversations():
    conversations = current_user.conversations.order_by(Conversation.updated_at.desc()).all()
    conversations_with_messages = [c for c in conversations if c.messages.count() > 0]
    return jsonify([{
        'id': c.id,
        'title': c.title or 'Untitled Conversation',
        'model': c.model.name,
        'created_at': c.created_at,
        'updated_at': c.updated_at,
        'message_count': c.messages.count()
    } for c in conversations_with_messages])
'''
@conv_bp.route("/api/conversations")
@login_required
def get_conversations():
    conversations = current_user.conversations.order_by(Conversation.updated_at.desc()).all()

    payload = []
    now = time.time()

    for c in conversations:
        msgs = c.messages.order_by(Message.timestamp).all()  # because lazy='dynamic'

        # Determine if conversation is active (can still send messages)
        is_active = True
        window_end_date = None

        if c.window_id:
            window = ChatWindow.query.get(c.window_id)
            if window:
                window_end_date = window.end_date
                # Conversation is inactive if window has ended or is not active
                if now > window.end_date or not window.is_active:
                    is_active = False

        # Skip empty conversations only if they're inactive (past)
        # Active conversations should show even if empty (user can still send messages)
        if len(msgs) == 0 and not is_active:
            continue

        payload.append({
            'id': c.id,
            'title': c.title or 'Untitled Conversation',
            'model': c.model.name,                 # stays a string for .toLowerCase()
            'created_at': c.created_at,
            'updated_at': c.updated_at,
            'message_count': len(msgs),
            'messages': [m.to_dict() for m in msgs],  # <-- include Message.content here
            'is_active': is_active,
            'window_end_date': window_end_date
        })
    return jsonify(payload)


@conv_bp.route("/api/conversation", methods=["POST"])
@login_required
def create_conversation():
    data = request.json or {}
    model_id = data['model_id']
    model = Model.query.get_or_404(model_id)

    # Provider restrictions
    if current_user.is_patient():
        provider_assignment = ProviderPatient.query.filter_by(patient_id=current_user.id).first()
        if provider_assignment:
            settings = ProviderSettings.query.filter_by(
                provider_id=provider_assignment.provider_id,
                patient_id=current_user.id
            ).first()
            if settings and settings.allowed_models:
                allowed = json.loads(settings.allowed_models)
                if model_id not in allowed:
                    return jsonify({'error': 'Model not allowed by provider'}), 403

    # Get system prompt content (with custom instructions applied)
    system_prompt_content = None
    system_prompt_id = data.get('system_prompt_id')
    if system_prompt_id:
        prompts_data = get_system_prompts().get_json()
        for p in prompts_data:
            if p['id'] == system_prompt_id:
                system_prompt_content = p['content']
                break

    conversation = Conversation(
        user_id=current_user.id,
        model_id=model_id,
        system_prompt_id=system_prompt_id,
        system_prompt_content=system_prompt_content
    )
    db.session.add(conversation)
    db.session.commit()
    return jsonify({'id': conversation.id})

@conv_bp.route("/api/conversation/<int:conversation_id>/message", methods=["POST"])
@login_required
def send_message(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    # Access check
    if conversation.user_id != current_user.id and not current_user.can_access_patient(conversation.user_id):
        abort(403)

    # Check if conversation belongs to an expired window
    if conversation.window_id:
        window = ChatWindow.query.get(conversation.window_id)
        if window:
            now = time.time()
            # Can't send messages if window has ended or isn't active
            if now > window.end_date or not window.is_active:
                return jsonify({'error': 'Chat window has expired or is no longer active'}), 403

    # Time window and limits for patients
    if current_user.is_patient():
        provider_assignment = ProviderPatient.query.filter_by(patient_id=current_user.id).first()
        if provider_assignment:
            settings = ProviderSettings.query.filter_by(
                provider_id=provider_assignment.provider_id,
                patient_id=current_user.id
            ).first()
            if settings:
                # Time window check
                if settings.time_window_start and settings.time_window_end:
                    now = datetime.now().strftime('%H:%M')
                    if not (settings.time_window_start <= now <= settings.time_window_end):
                        return jsonify({'error': 'Outside allowed chat hours'}), 403
                # Daily message limit
                if settings.max_messages_per_day:
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                    today_messages = Message.query.join(Conversation).filter(
                        Conversation.user_id == current_user.id,
                        Message.timestamp >= today_start,
                        Message.role == 'user'
                    ).count()
                    if today_messages >= settings.max_messages_per_day:
                        return jsonify({'error': 'Daily message limit reached'}), 403

    data = request.json or {}

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=data['message'],
        timestamp=time.time()
    )
    db.session.add(user_message)

    # Generate title if first message
    if conversation.messages.count() == 0:
        conversation.generate_title()

    # History (last 20)
    history = [{'role': m.role, 'content': m.content}
               for m in conversation.messages.order_by(Message.timestamp).limit(20)]
    history.append({'role': 'user', 'content': data['message']})

    system_prompt = conversation.system_prompt_content
    print(f"Using system prompt for conversation {conversation_id}: {system_prompt}")

    # Call LLM
    response_text, response_time = LLMInterface.call_llm(conversation.model, history, system_prompt)

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=response_text,
        timestamp=time.time(),
        response_time=response_time
    )
    db.session.add(assistant_message)

    conversation.updated_at = time.time()
    db.session.commit()

    return jsonify({'response': response_text, 'message_id': assistant_message.id})

@conv_bp.route("/api/save_selection", methods=["POST"])
@login_required
def save_selection():
    data = request.json or {}
    selection = SavedSelection(
        user_id=current_user.id,
        conversation_id=data['conversation_id'],
        selection_text=data['text'],
        message_ids=json.dumps(data.get('message_ids', [])),
        note=data.get('note')
    )
    db.session.add(selection)
    db.session.commit()
    return jsonify({'status': 'success', 'id': selection.id})

@conv_bp.route("/api/selections")
@login_required
def get_selections():
    selections = current_user.saved_selections.order_by(SavedSelection.created_at.desc()).limit(50).all()
    conversation_titles = {}
    if selections:
        conv_ids = {s.conversation_id for s in selections}
        conversations = Conversation.query.filter(Conversation.id.in_(conv_ids)).all()
        for conv in conversations:
            if conv:
                conversation_titles[conv.id] = (conv.title or f"Conversation {conv.id}").strip() or f"Conversation {conv.id}"

    return jsonify([{
        'id': s.id,
        'text': s.selection_text,
        'note': s.note or conversation_titles.get(s.conversation_id) or f"Conversation {s.conversation_id}",
        'conversation_id': s.conversation_id,
        'created_at': s.created_at
    } for s in selections])

@conv_bp.route("/api/selections/<int:selection_id>", methods=["DELETE"])
@login_required
def delete_selection(selection_id):
    selection = SavedSelection.query.get_or_404(selection_id)
    if selection.user_id != current_user.id:
        abort(403)

    db.session.delete(selection)
    db.session.commit()
    return jsonify({'status': 'deleted', 'id': selection_id})

# -------- Shared APIs: models & system prompts

@conv_bp.route("/api/models")
@login_required
def get_available_models():
    """Get available models based on connectivity and restrictions"""
    models = Model.query.filter_by(is_active=True).all()
    available = []

    for model in models:
        model.is_available = model.check_availability()
        model.last_availability_check = time.time()

        if not model.is_available:
            continue

        # Provider restrictions for patients
        if current_user.is_patient():
            provider_assignment = ProviderPatient.query.filter_by(patient_id=current_user.id).first()
            if provider_assignment:
                settings = ProviderSettings.query.filter_by(
                    provider_id=provider_assignment.provider_id,
                    patient_id=current_user.id
                ).first()
                if settings and settings.allowed_models:
                    allowed = json.loads(settings.allowed_models)
                    if model.id not in allowed:
                        continue

        available.append({'id': model.id, 'name': model.name, 'provider': model.provider})

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    print(f"Available models: {[m['name'] for m in available]}")
    return jsonify(available)

@conv_bp.route("/api/system_prompts")
@login_required
def get_system_prompts():
    """Get available system prompts with provider custom instructions applied"""
    prompts = SystemPrompt.query.filter_by(is_active=True).all()

    provider_custom_instructions = None
    if current_user.is_patient():
        provider_assignment = ProviderPatient.query.filter_by(patient_id=current_user.id).first()
        if provider_assignment:
            settings = (ProviderSettings.query.filter_by(
                provider_id=provider_assignment.provider_id,
                patient_id=current_user.id
            ).first() or ProviderSettings.query.filter_by(
                provider_id=provider_assignment.provider_id,
                patient_id=None
            ).first())
            if settings:
                provider_custom_instructions = settings.custom_instructions
                # If provider forced a specific prompt, only return that one
                if settings.system_prompt_id:
                    prompt = SystemPrompt.query.get(settings.system_prompt_id)
                    if prompt:
                        content = prompt.content
                        if provider_custom_instructions:
                            content = f"{content}\n\nProvider Instructions: {provider_custom_instructions.strip()}"
                        return jsonify([{'id': prompt.id, 'name': prompt.name, 'content': content}])

    result = []
    for p in prompts:
        content = p.content
        if provider_custom_instructions:
            content = f"{content}\n\nProvider Instructions: {provider_custom_instructions.strip()}"
        result.append({'id': p.id, 'name': p.name, 'content': content})

    return jsonify(result)


