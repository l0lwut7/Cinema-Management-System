from flask import Flask

from app.blueprints.discovery import discovery_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key_for_flash_messages"
    app.register_blueprint(discovery_bp)
    return app
