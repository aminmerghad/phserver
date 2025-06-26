import os
import pytest
import tempfile
from uuid import uuid4
from flask import Flask
from flask_jwt_extended import create_access_token

from app import create_app
from app.dataBase import db
from app.services.auth_service.infrastructure.persistence.models.user_model import UserModel
from app.services.inventory_service.infrastructure.persistence.models.product_model import ProductModel
from app.services.inventory_service.infrastructure.persistence.models.inventory_model import InventoryModel
from app.services.inventory_service.domain.enums.product_status import ProductStatus
from datetime import datetime, timedelta, timezone

@pytest.fixture(scope='function')
def app():
    """Create a Flask app for testing"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Set up test config
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'PROPAGATE_EXCEPTIONS': True
    }
    
    # Create the app with test settings
    app = create_app('testing')
    app.config.update(test_config)
    
    # Create tables and context
    with app.app_context():
        db.create_all()
        _populate_test_data(app)
        yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def client(app):
    """Test client for API"""
    return app.test_client()

# @pytest.fixture(scope='function')
# def auth_headers(app):
#     """Authorization headers with JWT token"""
#     with app.app_context():
#         # Get the test user
#         user = db.session.query(UserModel).filter_by(username='testuser').first()
#         access_token = create_access_token(identity=str(user.id))
#         return {'Authorization': f'Bearer {access_token}'}

def _populate_test_data(app):
    """Populate test database with sample data"""
    with app.app_context():
        # Create test user
        test_user = UserModel(
            id=uuid4(),
            username='testuser',
            email='test@example.com',
            password='$2b$12$3fK5VXxDFb/Z1MhPc4UCqeE56rqv0.uXL2KrFfuiLrNZnV7XfDxAy',  # hashed 'password'
            full_name='Test User',
            phone='1234567890',
            is_admin=False,
            is_active=True
        )
        
        # Create test products
        product1 = ProductModel(
            id=uuid4(),
            name='Paracetamol',
            description='Pain reliever and fever reducer',
            brand='Generic',
            dosage_form='Tablet',
            strength='500mg',
            package='Blister pack of 20'
        )
        
        product2 = ProductModel(
            id=uuid4(),
            name='Ibuprofen',
            description='Anti-inflammatory medication',
            brand='Generic',
            dosage_form='Tablet',
            strength='200mg',
            package='Bottle of 50'
        )
        
        # Create inventory for products
        inventory1 = InventoryModel(
            id=uuid4(),
            product_id=product1.id,
            quantity=100,
            price=5.99,
            max_stock=200,
            min_stock=20,
            last_updated_at=datetime.now(timezone.utc),
            expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
            status=ProductStatus.ACTIVE
        )
        
        inventory2 = InventoryModel(
            id=uuid4(),
            product_id=product2.id,
            quantity=50,
            price=8.99,
            max_stock=100,
            min_stock=10,
            last_updated_at=datetime.now(timezone.utc),
            expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
            status=ProductStatus.ACTIVE
        )
        
        # Add to database
        db.session.add(test_user)
        db.session.add(product1)
        db.session.add(product2)
        db.session.add(inventory1)
        db.session.add(inventory2)
        db.session.commit()
        
        # Store IDs for reference in tests
        app.config['TEST_USER_ID'] = str(test_user.id)
        app.config['TEST_PRODUCT1_ID'] = str(product1.id)
        app.config['TEST_PRODUCT2_ID'] = str(product2.id) 