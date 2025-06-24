import os
from datetime import timedelta

class Config:
    """Base configuration for the Pharmacy Management System."""
    
    # Flask Core Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'echo': False,  # Set to True for SQL query logging
        'connect_args': {
            'client_encoding': 'utf8',
            'connect_timeout': 10
        }
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_HOURS', 24)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_DAYS', 30)))
    
    # API Documentation Configuration
    API_TITLE = os.getenv('API_TITLE', 'Pharmacy Management API')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    OPENAPI_VERSION = os.getenv('OPENAPI_VERSION', '3.0.3')
    PROPAGATE_EXCEPTIONS = True
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    # APISPEC_STRICT_VALIDATION = True    
        # Security Configuration
    ADMIN_INITIALIZATION_KEY = os.getenv('ADMIN_INITIALIZATION_KEY', 'admin-init-key-change-this')
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))

    
class DevelopmentConfig(Config):
    """Development configuration - optimized for local development."""
    DEBUG = True
    TESTING = False
    
    # PostgreSQL Database - use environment variable or fallback to existing with encoding fix
    database_url = os.getenv(
        'DATABASE_URL', 
        "postgresql://pharmacy_db_ghv6_user:XbzLX3BJDC4770h7vbdWWdaZK0Fp13KK@dpg-d0opaimuk2gs738u3o80-a.oregon-postgres.render.com/pharmacy_db_ghv6"
    )
    
    # Add charset parameter if not present
    if '?' not in database_url:
        SQLALCHEMY_DATABASE_URI = f"{database_url}?client_encoding=utf8&connect_timeout=10"
    else:
        SQLALCHEMY_DATABASE_URI = database_url
    
    # Development-specific settings
    BCRYPT_LOG_ROUNDS = 4  # Faster password hashing for development
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': False,  # Disable SQL logging to avoid encoding issues
        'connect_args': {
            'client_encoding': 'utf8',
            'connect_timeout': 10,
        }
    }


class TestingConfig(Config):
    """Testing configuration - optimized for running tests."""
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite for fast tests or dedicated test database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )
    
    # Testing-specific settings
    BCRYPT_LOG_ROUNDS = 4  # Fast password hashing for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    
    # Disable database connection pooling for tests
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': False,
        'pool_recycle': -1,
        'echo': False
    }


class ProductionConfig(Config):
    """Production configuration - optimized for deployment."""
    DEBUG = False
    TESTING = False
    
    # PostgreSQL Database - must be provided via environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable must be set for production")
    
    # Add charset parameter if not present
    if '?' not in database_url:
        SQLALCHEMY_DATABASE_URI = f"{database_url}?client_encoding=utf8&connect_timeout=10"
    else:
        SQLALCHEMY_DATABASE_URI = database_url
    
    # Production-specific security settings
    BCRYPT_LOG_ROUNDS = 12  # Strong password hashing
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'echo': False,
        'connect_args': {
            'client_encoding': 'utf8',
            'connect_timeout': 10,
        }
    }


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Helper function to get config
def get_config(config_name=None):
    """Get configuration class by name."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig) 