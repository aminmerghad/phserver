"""
Consolidated conftest.py for all project tests.
This file contains all fixtures needed for testing across all services.
"""

import json
import pytest
import os
from datetime import datetime, timedelta, date
from uuid import uuid4
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Database and shared imports
from app.dataBase import Database, db
from app.config import TestingConfig
from app.shared.application.events.event_bus import EventBus
from app.shared.acl.unified_acl import UnifiedACL

# Auth service imports
from app.services.auth_service.service import AuthService
from app.services.auth_service.domain.entities.user_entity import UserEntity
from app.services.auth_service.domain.entities.access_code_entity import AccessCodeEntity
from app.services.auth_service.domain.entities.health_care_center_entity import HealthCareCenterEntity
from app.services.auth_service.domain.value_objects.email import Email
from app.services.auth_service.domain.value_objects.password import Password
from app.services.auth_service.infrastructure.persistence.models.user_model import UserModel
from app.services.auth_service.infrastructure.persistence.models.access_code_model import AccessCodeModel
from app.services.auth_service.infrastructure.persistence.models.health_care_center_model import HealthCareCenterModel

# Category service imports - add model imports to ensure tables are created  
from app.services.category_service.infrastructure.persistence.models.category import Category

# Product service imports - add model imports to ensure tables are created  
from app.services.product_service.infrastructure.persistence.models.product_model import ProductModel

# Inventory service imports
from app.services.inventory_service.service import InventoryService
from app.services.product_service.domain.enums.product_status import ProductStatus
from app.services.inventory_service.infrastructure.persistence.models.inventory_model import InventoryModel
from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckItemContract

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
TestingConfig.ADMIN_INITIALIZATION_KEY = "test_init_key_12345"

# =============================================================================
# CORE FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["API_TITLE"] = "Test API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Initialize Flask-Smorest API
    from flask_smorest import Api
    api = Api(app)
    
    # Register blueprints
    from app.apis.base_routes import health_bp
    from app.apis import auth_bp, product_bp, category_bp
    
    app.register_blueprint(health_bp)
    api.register_blueprint(auth_bp)
    api.register_blueprint(product_bp)
    api.register_blueprint(category_bp)
    
    # Initialize basic container for testing
    from app.extensions import container
    
    # Store the container reference in app context
    app.container = container
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        yield app
        
        # Clean up after tests
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def database(app):
    """Create a database instance"""
    return Database()

@pytest.fixture
def event_bus():
    """Create a real event bus instance"""
    return EventBus()

@pytest.fixture
def acl():
    """Create a real UnifiedACL instance"""
    return UnifiedACL()

@pytest.fixture(scope="function")
def db_session(app):
    """Create a fresh database session for each test"""
    with app.app_context():
        # Ensure all tables exist
        db.create_all()
        
        yield db.session
        
        # Cleanup - remove all data but keep the session
        db.session.rollback()
        
        # Clear all data from tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

# =============================================================================
# SERVICE FIXTURES
# =============================================================================

@pytest.fixture
def auth_service(database, event_bus):
    """Create a real auth service instance"""
    return AuthService(database, event_bus)

@pytest.fixture
def inventory_service(database, event_bus):
    """Create a real inventory service instance"""
    return InventoryService(database, event_bus)

@pytest.fixture
def product_service(database, event_bus, acl):
    """Create a real product service instance"""
    from app.services.product_service.service import ProductService
    return ProductService(database, event_bus, acl)

# =============================================================================
# AUTH SERVICE FIXTURES
# =============================================================================

@pytest.fixture
def test_health_care_center(app, db_session):
    """Create a test health care center"""
    with app.app_context():
        center = HealthCareCenterModel(
            id=uuid4(),
            name="Test Health Care Center",
            address="123 Test Street, Test City",
            phone="+1234567890",
            email="test@healthcare.com",
            latitude=40.7128,
            longitude=-74.0060,
            is_active=True
        )
        db_session.add(center)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(center)
        return center

@pytest.fixture
def test_access_code(app, db_session, test_health_care_center):
    """Create a test access code"""
    with app.app_context():
        access_code = AccessCodeModel(
            id=uuid4(),
            code="TEST123",
            health_care_center_id=test_health_care_center.id,
            is_used=False,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=7)
        )
        db_session.add(access_code)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(access_code)

        
        return access_code

@pytest.fixture
def test_expired_access_code(app, db_session, test_health_care_center):
    """Create an expired test access code"""
    with app.app_context():
        access_code = AccessCodeModel(
            id=uuid4(),
            code="EXPIRED123",
            health_care_center_id=test_health_care_center.id,
            is_used=False,
            is_active=True,
            expires_at=datetime.now() - timedelta(days=1)
        )
        db_session.add(access_code)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(access_code)
        return access_code

@pytest.fixture
def test_used_access_code(app, db_session, test_health_care_center):
    """Create a used test access code"""
    with app.app_context():
        access_code = AccessCodeModel(
            id=uuid4(),
            code="USED123",
            health_care_center_id=test_health_care_center.id,
            is_used=True,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=7)
        )
        db_session.add(access_code)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(access_code)
        return access_code

@pytest.fixture
def test_user(app, db_session, test_health_care_center):
    """Create a test user"""
    with app.app_context():
        user = UserModel(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            password=Password("TestPass123!").hashed,
            full_name="Test User",
            phone="+1234567890",
            is_admin=False,
            health_care_center_id=test_health_care_center.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(user)
        return user

@pytest.fixture
def test_admin_user(app, db_session) -> UserModel:
    """Create a test admin user"""
    with app.app_context():
        admin = UserModel(
            id=uuid4(),
            username="adminuser",
            email="admin@example.com",
            password=Password("AdminPass123!").hashed,
            full_name="Admin User",
            phone="+0987654321",
            is_admin=True,
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh the object to ensure it's not detached
        db_session.refresh(admin)
        return admin

@pytest.fixture
def test_multiple_users(app,db_session, test_health_care_center):
    """Create multiple test users"""
    with app.app_context():
        users = []
        for i in range(3):
            user = UserModel(
                id=uuid4(),
                username=f"testuser{i}",
                email=f"test{i}@example.com",
                password=Password("TestPass123!").hashed,
                full_name=f"Test User {i}",
                phone=f"+123456789{i}",
                is_admin=False,
                health_care_center_id=test_health_care_center.id,  # Fixed to use .id
                is_active=True
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh all objects to ensure they're not detached
        for user in users:
            db_session.refresh(user)
        return users

@pytest.fixture
def test_multiple_access_codes(app, db_session, test_health_care_center):
    """Create multiple test access codes"""
    with app.app_context():
        codes = []
        for i in range(3):
            access_code = AccessCodeModel(
                id=uuid4(),
                code=f"TEST{i}123",
                health_care_center_id=test_health_care_center.id,  # Fixed to use .id
                is_used=False,
                is_active=True,
                expires_at=datetime.now() + timedelta(days=7)
            )
            codes.append(access_code)
        
        db_session.add_all(codes)
        db_session.commit()  # Commit to make data available to API endpoints
        
        # Refresh all objects to ensure they're not detached
        for code in codes:
            db_session.refresh(code)
        return codes

@pytest.fixture
def valid_user_data():
    """Valid user registration data"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewUserPass123!",
        "full_name": "New User",
        "phone": "+1112223333",
        "access_code": "TEST123"
    }

@pytest.fixture
def valid_admin_data():
    """Valid admin registration data"""
    return {
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "NewAdminPass123!",
        "full_name": "New Admin",
        "phone": "+4445556666",
        "initialization_key": "test_init_key_12345"
    }

@pytest.fixture
def valid_access_code_data():
    """Valid access code creation data"""
    return {
        "referral_email": "referral@example.com",
        "referral_phone": "+7778889999",
        "health_care_center_email": "test@healthcare.com"
    }

@pytest.fixture
def valid_health_care_center_data():
    """Valid health care center data"""
    return {
        "name": "New Health Care Center",
        "address": "456 New Street, New City",
        "phone": "+9998887777",
        "email": "new@healthcare.com",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "is_active": True
    }

@pytest.fixture
def valid_product_data():
    """Valid product creation data"""
    return {
        "product_fields": {
            "name": "Test Medicine",
            "description": "A test medicine for testing purposes",
            "brand": "Test Brand",
            "dosage_form": "Tablet",
            "strength": "500mg",
            "package": "30 tablets",
            "image_url": "https://example.com/test-medicine.jpg",
            "status": "ACTIVE"
        },
        "inventory_fields": {
            "price": 25.50,
            "quantity": 100,
            "max_stock": 200,
            "min_stock": 20,
            "expiry_date": "2025-12-31"
        }
    }

@pytest.fixture
def bulk_products_data():
    """Valid bulk products creation data"""
    return {
        "products": [
            {
                "product_fields": {
                    "name": "Bulk Medicine 1",
                    "description": "First bulk medicine",
                    "brand": "Bulk Brand",
                    "status": "ACTIVE"
                },
                "inventory_fields": {
                    "price": 15.00,
                    "quantity": 50,
                    "max_stock": 100,
                    "min_stock": 10,
                    "expiry_date": "2025-06-30"
                }
            },
            {
                "product_fields": {
                    "name": "Bulk Medicine 2", 
                    "description": "Second bulk medicine",
                    "brand": "Bulk Brand",
                    "status": "ACTIVE"
                },
                "inventory_fields": {
                    "price": 20.00,
                    "quantity": 75,
                    "max_stock": 150,
                    "min_stock": 15,
                    "expiry_date": "2025-08-15"
                }
            }
        ]
    }

@pytest.fixture
def valid_category_data():
    """Valid category creation data"""
    return {
        "category_fields": {
            "name": "Test Category",
            "description": "A test category for testing purposes",
            "image_url": "https://example.com/test-category.jpg",
            "is_active": True
        }
    }

@pytest.fixture
def valid_category_update_data():
    """Valid category update data"""
    return {
        "category_fields": {
            "name": "Updated Test Category",
            "description": "An updated test category description",
            "image_url": "https://example.com/updated-category.jpg",
            "is_active": True
        }
    }

@pytest.fixture
def valid_subcategory_data():
    """Valid subcategory creation data"""
    return {
        "category_fields": {
            "name": "Test Subcategory",
            "description": "A test subcategory for testing purposes",
            "image_url": "https://example.com/test-subcategory.jpg",
            "is_active": True
        }
    }

@pytest.fixture
def auth_headers(app, test_user):
    """Create authorization headers for test user"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(test_user.id))
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(app,client, test_admin_user):
    """Create authorization headers for admin user"""
    login_data = {
            "email": test_admin_user.email,
            "password": "AdminPass123!"  # From the fixture
        }
        
    response = client.post("/api/auth/login",
                             data=json.dumps(login_data),
                             content_type='application/json')
    data=  response.get_json()['data']
    return {"Authorization": f"Bearer {data['access_token']}"}
  

# =============================================================================
# INVENTORY SERVICE FIXTURES
# =============================================================================

@pytest.fixture
def test_products(app, db_session):
    """Create test products in the database"""
    with app.app_context():
        # Product 1: Normal product with sufficient stock
        product1_id = uuid4()
        product1 = ProductModel(
            id=product1_id,
            name="Regular Medicine",
            description="Regular medicine description"
        )
        
        # Product 2: Expired product
        product2_id = uuid4()
        product2 = ProductModel(
            id=product2_id,
            name="Expired Medicine",
            description="Expired medicine description"
        )
        
        # Product 3: Low stock product
        product3_id = uuid4()
        product3 = ProductModel(
            id=product3_id,
            name="Low Stock Medicine",
            description="Low stock medicine description"
        )
        
        # Product 4: Expiring soon product
        product4_id = uuid4()
        product4 = ProductModel(
            id=product4_id,
            name="Expiring Soon Medicine",
            description="Medicine expiring soon"
        )
        
        # Product 5: Inactive product
        product5_id = uuid4()
        product5 = ProductModel(
            id=product5_id,
            name="Inactive Medicine",
            description="Inactive medicine"
        )
        
        # Product 6: Combined issues product
        product6_id = uuid4()
        product6 = ProductModel(
            id=product6_id,
            name="Combined Issues Medicine",
            description="Medicine with multiple issues"
        )
        
        # Add products to session
        db_session.add_all([product1, product2, product3, product4, product5, product6])
        db_session.commit()  # Commit to make data available to API endpoints
        
        return {
            'regular_id': product1_id,
            'expired_id': product2_id,
            'low_stock_id': product3_id,
            'expiring_soon_id': product4_id,
            'inactive_id': product5_id,
            'combined_issues_id': product6_id
        }

@pytest.fixture
def test_inventory(app, db_session, test_products):
    """Create test inventory items in the database"""
    with app.app_context():
        # Regular product inventory
        inventory1 = InventoryModel(
            id=uuid4(),
            product_id=test_products['regular_id'],
            quantity=100,
            price=15.0,
            max_stock=200,
            min_stock=20,
            expiry_date=date.today() + timedelta(days=180),
            status=ProductStatus.ACTIVE
        )
        
        # Expired product inventory
        inventory2 = InventoryModel(
            id=uuid4(),
            product_id=test_products['expired_id'],
            quantity=50,
            price=25.0,
            max_stock=100,
            min_stock=10,
            expiry_date=date.today() - timedelta(days=10),  # Expired 10 days ago
            status=ProductStatus.ACTIVE
        )
        
        # Low stock product inventory
        inventory3 = InventoryModel(
            id=uuid4(),
            product_id=test_products['low_stock_id'],
            quantity=15,  # Already below min_stock
            price=30.0,
            max_stock=100,
            min_stock=20,
            expiry_date=date.today() + timedelta(days=180),
            status=ProductStatus.ACTIVE
        )
        
        # Expiring soon product inventory
        inventory4 = InventoryModel(
            id=uuid4(),
            product_id=test_products['expiring_soon_id'],
            quantity=50,
            price=40.0,
            max_stock=100,
            min_stock=20,
            expiry_date=date.today() + timedelta(days=15),  # Expiring in 15 days
            status=ProductStatus.ACTIVE
        )
        
        # Inactive product inventory
        inventory5 = InventoryModel(
            id=uuid4(),
            product_id=test_products['inactive_id'],
            quantity=75,
            price=20.0,
            max_stock=150,
            min_stock=15,
            expiry_date=date.today() + timedelta(days=180),
            status=ProductStatus.INACTIVE
        )
        
        # Combined issues product inventory
        inventory6 = InventoryModel(
            id=uuid4(),
            product_id=test_products['combined_issues_id'],
            quantity=25,  # Will go below min_stock when ordered
            price=50.0,
            max_stock=100,
            min_stock=20,
            expiry_date=date.today() + timedelta(days=20),  # Expiring soon
            status=ProductStatus.ACTIVE
        )
        
        # Add inventory items to session
        db_session.add_all([inventory1, inventory2, inventory3, inventory4, inventory5, inventory6])
        db_session.commit()  # Commit to make data available to API endpoints
        
        return {
            'regular': inventory1,
            'expired': inventory2,
            'low_stock': inventory3,
            'expiring_soon': inventory4,
            'inactive': inventory5,
            'combined_issues': inventory6
        }

# =============================================================================
# STOCK CHECK FIXTURES
# =============================================================================

@pytest.fixture
def stock_check_request_data(test_products):
    """Create stock check request data"""
    return StockCheckRequestContract(
        items=[
            StockCheckItemContract(
                product_id=test_products['regular_id'],
                requested_quantity=10
            ),
            StockCheckItemContract(
                product_id=test_products['low_stock_id'],
                requested_quantity=20
            )
        ]
    ) 