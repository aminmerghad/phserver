import json


class TestAccessCodesAPIEndpoints:
    """Test Access Codes API endpoints"""

    def test_access_code_validation_valid(self, client, test_access_code):
        """Test access code validation with valid code"""

        print(f"test_access_code: {test_access_code}")	
        response = client.get(f"/api/auth/access-code/{test_access_code.code}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Access code validation completed"
        assert data['data']['is_valid'] == True
    
    def test_access_code_validation_invalid(self, client):
        """Test access code validation with invalid code"""
        response = client.get("/api/auth/access-code/INVALID123")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Access code validation completed"
        assert data['data']['is_valid'] == False
 

    # # Access Code generation tests (admin only)
    def test_generate_access_code_unauthorized(self, client):
        """Test generating access code without admin privileges"""
        code_data = {
            "referral_email": "test@example.com",
            "expiry_days": 7
        }
        
        response = client.post("/api/auth/access-code",
                             data=json.dumps(code_data),
                             content_type='application/json')
        
        assert response.status_code == 401  # Unauthorized
    def test_generate_access_code_as_admin(self, client, admin_headers, test_user):
        """Test generating access code with admin privileges"""
        code_data = {
            "referral_email": test_user.email,
            "expiry_days": 7
        }
        
        response = client.post("/api/auth/access-code",
                             data=json.dumps(code_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Access code generated successfully"
        assert 'code' in data['data']
        assert data['data']['is_active'] == True
    
    def test_list_access_codes_unauthorized(self, client):
        """Test listing access codes without admin privileges"""
        response = client.get("/api/auth/access-codes")
        
        assert response.status_code == 401  # Unauthorized
        
    #add test for list access codes as admin
   
    
    def test_delete_access_code_unauthorized(self, client, test_access_code):
        """Test deleting access code without admin privileges"""
        response = client.delete(f"/api/auth/access-code/{test_access_code.code}")
        
        assert response.status_code == 401  # Unauthorized
    
    def test_delete_access_code_as_admin(self, client, admin_headers, test_access_code):
        """Test deleting access code with admin privileges"""
        response = client.delete(f"/api/auth/access-code/{test_access_code.code}",
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Access code deleted successfully" 