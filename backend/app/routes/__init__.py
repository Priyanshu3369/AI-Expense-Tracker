from .auth import auth_bp
from .expenses import expenses_bp
from .budgets import budgets_bp
from .dashboard import dashboard_bp
from .ai_insights import ai_bp 

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ai_bp)