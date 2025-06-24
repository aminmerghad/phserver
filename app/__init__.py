#!/usr/bin/env python3
"""
Pharmacy Management System Application Factory
"""

import logging
from flask import Flask
from app.config import get_config
from app.extensions import init_resources, container,api as apiX
from app.dataBase import db
# Import all models for SQLAlchemy to recognize them
from app.shared.infrastructure.persistence.models import *
# Import the health check blueprint
from app.apis.base_routes import health_bp

def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions and resources
    init_resources(app)
    
    with app.app_context():       
        # Create database tables with robust error handling
        try:
            # Log database URI for debugging (mask sensitive parts)
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            if 'password' in db_uri.lower():
                # Mask password in logs
                masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + db_uri.split('@')[1] if '@' in db_uri else db_uri
                app.logger.info(f"Database URI: {masked_uri}")
            else:
                app.logger.info(f"Database URI: {db_uri}")
            
            # Simple connection test without inspection to avoid encoding issues
            try:
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    # Just test if we can connect
                    conn.execute(text("SELECT 1"))
                app.logger.info("Database connection test successful")
                
                # Try to create tables without inspecting existing ones
                try:
                    db.create_all()
                    app.logger.info("Database tables creation attempted")
                except Exception as table_error:
                    if "already exists" in str(table_error).lower():
                        app.logger.info("Tables already exist - continuing with existing database")
                    else:
                        app.logger.warning(f"Table creation issue (continuing anyway): {table_error}")
                        
            except (UnicodeDecodeError, UnicodeError) as unicode_error:
                app.logger.warning(f"Database encoding issue detected: {unicode_error}")
                app.logger.info("Skipping database initialization due to encoding issues - API will work with existing setup")
            except Exception as conn_error:
                app.logger.warning(f"Database connection issue: {conn_error}")
                app.logger.info("Continuing without database initialization - check your database connection")
                
        except Exception as e:
            app.logger.error(f"Database setup error: {e}")
            app.logger.info("Application will continue without database initialization")
                    
    # Register blueprints
    register_blueprints(app)
    
    app.logger.info(f"Application created with {config_name} configuration")
    
    return app

def setup_logging(app: Flask) -> None:
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Production logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    else:
        # Development logging
        logging.basicConfig(level=logging.DEBUG)

def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.apis import bp_list
    
    # Register health check
    app.register_blueprint(health_bp)
    
    # Register API blueprints
    for bp in bp_list:
        apiX.register_blueprint(bp)
    app.logger.info("Blueprints registered successfully") 