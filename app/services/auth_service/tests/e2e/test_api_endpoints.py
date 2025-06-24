import pytest
import json

# Test initialization key (updated to match the conftest.py)
INIT_KEY = "test_init_key_12345"

class TestAuthAPIEndpoints:
    """Test Auth API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['message'] == "Server is running correctly"
        assert 'auth' in data['data']['services']
    
    
    
    def test_user_login_success(self, client, test_user):
        """Test successful user login"""
        print(f"Test user email: {test_user.email}")
        print(f"Test user id: {test_user.id}")
        print(f"Test user active: {test_user.is_active}")
        
        login_data = {
            "email": test_user.email,
            "password": "TestPass123!"  # From the fixture
        }
        
        response = client.post("/api/auth/login",
                             data=json.dumps(login_data),
                             content_type='application/json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_data(as_text=True)}")
        
        # Temporarily change to see what we get
        if response.status_code != 200:
            data = response.get_json()
            print(f"Error response: {data}")
        
        data = response.get_json()
        assert data['code'] == 200
        assert data['message'] == "User logged in successfully"
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['email'] == test_user.email
    
    def test_user_login_invalid_credentials(self, client):
        """Test user login with invalid credentials"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "WrongPass123!"
        }
        
        response = client.post("/api/auth/login",
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_user_registration_success(self, client, test_access_code):
        """Test successful user registration with valid access code"""
        # For now, let's go back to using the fixture and just test that it works
        # We'll address session issues if needed
        registration_data = {
            "code": test_access_code.code,
            "username": "newuser_test", 
            "password": "UserPass123!",
            "email": "newuser@test.com",
            "full_name": "New User",
            "phone": "+1234567893",
            "health_care_center": {
                "name": "New Health Care Center",
                "address": "456 New Street, New City", 
                "phone": "+1234567894",
                "email": "new@healthcare.com",
                "latitude": 40.7589,
                "longitude": -73.9851
            }
        }
        
        response = client.post("/api/auth/register",
                             data=json.dumps(registration_data),
                             content_type='application/json')
        
        print(f"User registration test - Status: {response.status_code}")
        print(f"User registration test - Data: {response.get_data(as_text=True)}")
        
        # For now, let's just check that we get some response
        # We can adjust expectations based on what we see
        assert response.status_code == 201
    
    def test_user_registration_invalid_access_code(self, client):
        """Test user registration with invalid access code"""
        registration_data = {
            "code": "INVALID123",
            "username": "invaliduser",
            "password": "UserPass123!",
            "email": "invalid@test.com",
            "full_name": "Invalid User",
            "phone": "+1234567895"
        }
        
        response = client.post("/api/auth/register",
                             data=json.dumps(registration_data),
                             content_type='application/json')
        print(response.get_data(as_text=True))
        
        assert response.status_code == 400  # Bad request for invalid access code
    
    
    def test_user_registration_used_access_code(self, client, test_used_access_code):
        """Test user registration with already used access code"""
        registration_data = {
            "code": test_used_access_code.code,
            "username": "useduser",
            "password": "UserPass123!",
            "email": "used@test.com",
            "full_name": "Used User",
            "phone": "+1234567897"
        }
        
        response = client.post("/api/auth/register",
                             data=json.dumps(registration_data),
                             content_type='application/json')
        
        assert response.status_code == 400  # Bad request for used access code
    
       
    def test_get_users_list_unauthorized(self, client):
        """Test getting users list without admin privileges"""
        response = client.get("/api/auth/users")
        
        assert response.status_code == 401  # Unauthorized
    
    def test_get_users_list_as_admin(self, client, admin_headers):
        """Test getting users list with admin privileges"""
        response = client.get("/api/auth/users",
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    
    
    