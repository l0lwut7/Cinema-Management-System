from flask import Flask, session

from app.blueprints.discovery import discovery_bp
from app.blueprints.booking.routes import booking_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.dashboard.routes import dashboard_bp
from app.blueprints.staff.routes import staff_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key_for_flash_messages"
    app.register_blueprint(discovery_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(staff_bp)
    
    @app.context_processor
    def inject_auth():
        return dict(is_authenticated='user_id' in session)
        
    return app
