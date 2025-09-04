import os
import secrets
from dotenv import load_dotenv
from flask import Flask
from .extensions import db, migrate, login_manager
from .routes.auth import auth_bp
from .routes.auth import auth_blp
from .routes.conversations import conv_bp
from .routes.provider import provider_bp
from .routes.admin import admin_bp
from flask_smorest import Api

# Load variables from .env
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Read from environment (with fallbacks)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///llm_chat.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(
        API_TITLE="My API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    api = Api(app)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # User loader
    from .models.core import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    api.register_blueprint(auth_blp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(conv_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(admin_bp)

    return app
