import json


class TestHealthCareCenterAPIEndpoints:
    """Test Health Care Center API endpoints"""

    # Health Care Center endpoints tests
    def test_get_health_care_centers_unauthorized(self, client):
        """Test getting health care centers without authentication"""
        response = client.get("/api/auth/health-care-centers")
        print(f"response: {response.get_json()}")
        assert response.status_code == 401  # Unauthorized
    
    # add test_get_health_care_centers_authorized    
    # add test_create_health_care_center_unauthorized
    # add test_create_health_care_center_authorized
    
   
    