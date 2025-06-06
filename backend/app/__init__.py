from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints
    register_routes(app)

    return app
