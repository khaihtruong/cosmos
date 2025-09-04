from functools import wraps
from flask_login import login_required, current_user
from flask import abort

def role_required(*roles):
    """Decorator to require specific roles for routes"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
