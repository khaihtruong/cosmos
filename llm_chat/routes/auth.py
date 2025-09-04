import time
from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models.core import User
from flask_smorest import Blueprint as SmorestBlueprint

auth_bp = Blueprint("auth1", __name__)
auth_blp = SmorestBlueprint(name = "auth", import_name = "auth", description = "Authentication endpoints")

@auth_blp.route("/")
@auth_blp.response(302, description="Redirects to login or dashboard")
def index():
    """Redirect based on authentication status"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.is_provider():
            return redirect(url_for('provider.provider_dashboard'))
        else:
            return redirect(url_for('conversations.user_dashboard'))
    return redirect(url_for('auth.login'))

@auth_blp.route("/login")
def login():
    """Render the login page"""
    return render_template("login.html")

@auth_blp.route("/logout")
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    return redirect(url_for('auth.login'))

# admin/provider login
@auth_blp.route("/api/login", methods=["POST"])
@auth_blp.response(401, description="Invalid credentials")
def api_login():
    """Perform authentication (check user, password), if valid then log user in"""
    data = request.json or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password', '')):
        login_user(user)
        return jsonify({
            'status': 'success',
            'role': user.role,
            'redirect': url_for('admin.admin_dashboard' if user.is_admin()
                                else 'provider.provider_dashboard' if user.is_provider()
                                else 'conversations.user_dashboard')
        })
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

'''
@auth_bp.route("/")
def index():
    """Redirect to login or dashboard based on auth status"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.is_provider():
            return redirect(url_for('provider.provider_dashboard'))
        else:
            return redirect(url_for('conversations.user_dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route("/login")
def login():
    return render_template("login.html")

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password', '')):
        login_user(user)
        return jsonify({
            'status': 'success',
            'role': user.role,
            'redirect': url_for('admin.admin_dashboard' if user.is_admin()
                                else 'provider.provider_dashboard' if user.is_provider()
                                else 'conversations.user_dashboard')
        })
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
'''
