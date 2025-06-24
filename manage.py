#!/usr/bin/env python3
"""
Management script for the Pharmacy Management System.
Handles database migrations, initialization, and other administrative tasks.
"""

import os
import sys
import logging
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade, downgrade
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.product_service.infrastructure.persistence.models.product_model import ProductModel

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_migration_app():
    """Create Flask app for migrations."""
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    migrate_instance = Migrate(app, db)
    return app, migrate_instance

def init_db():
    """Initialize the database with migrations."""
    logger.info("Initializing database with Flask-Migrate...")
    app, migrate_instance = create_migration_app()
    
    with app.app_context():
        try:
            # Initialize migration repository
            init()
            logger.info("Migration repository initialized successfully")
        except Exception as e:
            logger.warning(f"Migration repository may already exist: {e}")
        
        try:
            # Create initial migration
            migrate(message="Initial migration")
            logger.info("Initial migration created successfully")
        except Exception as e:
            logger.warning(f"Migration creation may have failed: {e}")
        
        try:
            # Apply migrations
            upgrade()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to apply migrations: {e}")
            raise

def create_tables():
    """Create database tables directly (alternative to migrations)."""
    logger.info("Creating database tables directly...")
    app, _ = create_migration_app()
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

def drop_tables():
    """Drop all database tables."""
    logger.warning("Dropping all database tables...")
    app, _ = create_migration_app()
    
    with app.app_context():
        try:
            db.drop_all()
            logger.info("All tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

def reset_db():
    """Reset database by dropping and recreating tables."""
    logger.info("Resetting database...")
    drop_tables()
    create_tables()
    logger.info("Database reset completed")

def upgrade_db():
    """Apply database migrations."""
    logger.info("Applying database migrations...")
    app, migrate_instance = create_migration_app()
    
    with app.app_context():
        try:
            upgrade()
            logger.info("Database upgraded successfully")
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            raise

def downgrade_db(revision=''):
    """Downgrade database to a specific revision."""
    logger.info(f"Downgrading database to revision: {revision or 'previous'}")
    app, migrate_instance = create_migration_app()
    
    with app.app_context():
        try:
            downgrade(revision=revision)
            logger.info("Database downgraded successfully")
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            raise

def create_migration(message):
    """Create a new migration."""
    logger.info(f"Creating migration: {message}")
    app, migrate_instance = create_migration_app()
    
    with app.app_context():
        try:
            migrate(message=message)
            logger.info(f"Migration '{message}' created successfully")
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise

def seed_data():
    """Seed the database with sample data."""
    logger.info("Seeding database with sample data...")
    app, _ = create_migration_app()
    
    with app.app_context():
        try:
            # Add sample products
            sample_products = [
                {
                    'name': 'Paracetamol 500mg',
                    'description': 'Pain relief and fever reducer',
                    'brand': 'Acme Pharma',
                    'dosage_form': 'Tablet',
                    'strength': '500mg',
                    'package': 'Box of 20'
                },
                {
                    'name': 'Amoxicillin 250mg',
                    'description': 'Antibiotic for bacterial infections',
                    'brand': 'Beta Medical',
                    'dosage_form': 'Capsule',
                    'strength': '250mg',
                    'package': 'Box of 15'
                },
                {
                    'name': 'Vitamin C 1000mg',
                    'description': 'Immune system support',
                    'brand': 'Health Plus',
                    'dosage_form': 'Tablet',
                    'strength': '1000mg',
                    'package': 'Bottle of 60'
                }
            ]
            
            for product_data in sample_products:
                product = ProductModel(**product_data)
                db.session.add(product)
            
            db.session.commit()
            logger.info(f"Added {len(sample_products)} sample products")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to seed data: {e}")
            raise

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands:")
        print("  init-db      - Initialize database with migrations")
        print("  create-tables - Create tables directly")
        print("  drop-tables  - Drop all tables")
        print("  reset-db     - Reset database (drop and recreate)")
        print("  upgrade      - Apply migrations")
        print("  downgrade [revision] - Downgrade to revision")
        print("  migrate <message> - Create new migration")
        print("  seed-data    - Add sample data")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'init-db':
            init_db()
        elif command == 'create-tables':
            create_tables()
        elif command == 'drop-tables':
            drop_tables()
        elif command == 'reset-db':
            reset_db()
        elif command == 'upgrade':
            upgrade_db()
        elif command == 'downgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else ''
            downgrade_db(revision)
        elif command == 'migrate':
            if len(sys.argv) < 3:
                print("Error: Migration message required")
                sys.exit(1)
            message = sys.argv[2]
            create_migration(message)
        elif command == 'seed-data':
            seed_data()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 