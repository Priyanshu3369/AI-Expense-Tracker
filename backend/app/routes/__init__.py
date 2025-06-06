from .auth import auth_bp
from .expenses import expenses_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
