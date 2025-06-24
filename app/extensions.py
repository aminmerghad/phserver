from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from app.container import Container
from app.dataBase import db
from flask_smorest import Api

ma = Marshmallow()
jwt = JWTManager()

container = Container()
api = Api()

def init_resources(app: Flask):
    """Initialize Flask extensions"""
    # Verify database configuration
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError(
            "SQLALCHEMY_DATABASE_URI is not set. Please check your configuration. "
            "For production, set DATABASE_URL environment variable or ensure fallback is configured."
        )
    
    # Initialize database
    try:
        db.init_app(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")
    
    # Initialize other extensions
    ma.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    # Initialize container resources
    container.init_acl()
    
    # Initialize event bus and ensure it's ready for event publishing/subscribing
    event_bus = container.event_bus()
    if event_bus:
        event_bus.init()
    
    # Store initialized resources in app context to prevent garbage collection
    if not hasattr(app, 'extensions_data'):
        app.extensions_data = {}
    
    app.extensions_data['event_bus'] = event_bus

    
    


