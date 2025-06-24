import pytest
import json

# Test initialization key (updated to match the conftest.py)
INIT_KEY = "test_init_key_12345"

class TestAdminAuthAPIEndpoints:
    def test_admin_registration_success(self, client):
        """Test successful admin registration"""
        admin_data = {
            "initialization_key": INIT_KEY,
            "username": "admin_test",
            "password": "AdminPass123!",
            "email": "admin@test.com",
            "full_name": "Admin User",
            "phone": "+1234567890"
        }
        
        response = client.post("/api/auth/admin/register", 
                             data=json.dumps(admin_data),
                             content_type='application/json')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_data(as_text=True)}")
        
        # Should return 201 for successful creation
        assert response.status_code == 201
    

    
    def test_admin_registration_invalid_key(self, client):
        """Test admin registration with invalid initialization key"""
        admin_data = {
            "initialization_key": "invalid_key",
            "username": "admin_invalid",
            "password": "AdminPass123!",
            "email": "admin2@test.com",
            "full_name": "Admin User",
            "phone": "+1234567891"
        }
        
        response = client.post("/api/auth/admin/register", 
                             data=json.dumps(admin_data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_admin_registration_duplicate_user(self, client):
        """Test admin registration with duplicate username"""
        # First create an admin user
        first_admin_data = {
            "initialization_key": INIT_KEY,
            "username": "duplicate_admin",
            "password": "AdminPass123!",
            "email": "admin1@test.com",
            "full_name": "First Admin",
            "phone": "+1234567891"
        }
        
        # Create the first admin
        first_response = client.post("/api/auth/admin/register", 
                                   data=json.dumps(first_admin_data),
                                   content_type='application/json')
        
        print(f"First admin creation - Status: {first_response.status_code}")
        assert first_response.status_code == 201  # Should succeed
        
        # Now try to create another admin with the same username
        duplicate_admin_data = {
            "initialization_key": INIT_KEY,
            "username": "duplicate_admin",  # Same username as first admin
            "password": "AdminPass123!",
            "email": "admin2@test.com",
            "full_name": "Duplicate Admin",
            "phone": "+1234567892"
        }
        
        duplicate_response = client.post("/api/auth/admin/register", 
                                       data=json.dumps(duplicate_admin_data),
                                       content_type='application/json')
        
        print(f"Duplicate admin test - Status: {duplicate_response.status_code}")
        print(f"Duplicate admin test - Data: {duplicate_response.get_data(as_text=True)}")
        
        assert duplicate_response.status_code == 409  # Should conflict
