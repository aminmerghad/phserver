import json
import pytest
from uuid import uuid4


class TestCategoryAdminEndpoints:
    """Test Category Admin-only API endpoints"""

    def test_create_category_admin_only(self, client, admin_headers, auth_headers, valid_category_data):
        """Test that only admins can create categories"""
        # Test admin can create
        admin_response = client.post("/api/categories/",
                                   data=json.dumps(valid_category_data),
                                   content_type='application/json',
                                   headers=admin_headers)
        
        assert admin_response.status_code == 201
        
        # Test regular user cannot create
        user_response = client.post("/api/categories/",
                                  data=json.dumps(valid_category_data),
                                  content_type='application/json',
                                  headers=auth_headers)
        
        assert user_response.status_code == 403

    def test_update_category_admin_only(self, client, admin_headers, auth_headers, valid_category_data, valid_category_update_data):
        """Test that only admins can update categories"""
        # Create a category first
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # Test admin can update
        admin_response = client.put(f"/api/categories/{category_id}",
                                  data=json.dumps(valid_category_update_data),
                                  content_type='application/json',
                                  headers=admin_headers)
        
        assert admin_response.status_code == 200
        
        # Test regular user cannot update
        user_response = client.put(f"/api/categories/{category_id}",
                                 data=json.dumps(valid_category_update_data),
                                 content_type='application/json',
                                 headers=auth_headers)
        
        assert user_response.status_code == 403

    def test_delete_category_admin_only(self, client, admin_headers, auth_headers, valid_category_data):
        """Test that only admins can delete categories"""
        # Create a category first
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # Test regular user cannot delete
        user_response = client.delete(f"/api/categories/{category_id}",
                                    headers=auth_headers)
        
        assert user_response.status_code == 403
        
        # Test admin can delete
        admin_response = client.delete(f"/api/categories/{category_id}",
                                     headers=admin_headers)
        
        assert admin_response.status_code == 200

    def test_bulk_category_operations_admin_only(self, client, admin_headers, auth_headers):
        """Test bulk operations are admin only"""
        # Create multiple categories
        categories = []
        for i in range(3):
            category_data = {
                "category_fields": {
                    "name": f"Bulk Category {i}",
                    "description": f"Description for bulk category {i}",
                    "is_active": True
                }
            }
            
            response = client.post("/api/categories/",
                                 data=json.dumps(category_data),
                                 content_type='application/json',
                                 headers=admin_headers)
            
            assert response.status_code == 201
            categories.append(response.get_json()['data']['id'])
        
        # Test that regular users can still list categories
        list_response = client.get("/api/categories/list",
                                 headers=auth_headers)
        
        assert list_response.status_code == 200
        
        # Clean up categories
        for category_id in categories:
            delete_response = client.delete(f"/api/categories/{category_id}",
                                          headers=admin_headers)
            assert delete_response.status_code == 200

    def test_admin_category_permissions_edge_cases(self, client, valid_category_data):
        """Test edge cases for admin category permissions"""
        # Attempt to create with invalid data and no admin rights (should be 401)
        response = client.post("/api/categories/",
                             data=json.dumps(valid_category_data),
                             content_type='application/json')
        assert response.status_code == 401
        
        # Attempt to update without admin rights
        response = client.put("/api/categories/f4b1b3b3-1b1b-1b1b-1b1b-1b1b1b1b1b1b",
                            data=json.dumps(valid_category_data),
                            content_type='application/json')
        assert response.status_code == 401
        
        # Attempt to delete without admin rights
        response = client.delete("/api/categories/f4b1b3b3-1b1b-1b1b-1b1b-1b1b1b1b1b1b")
        assert response.status_code == 401

    def test_category_validation_admin_operations(self, client, admin_headers):
        """Test validation for admin-only category operations"""
        # Test creating category with missing required fields
        invalid_data = {
            "category_fields": {
                "description": "A category with no name"
            }
        }
        
        response = client.post("/api/categories/",
                             data=json.dumps(invalid_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code in [400, 422]  # Validation should fail
        
        # Test creating category with excessively long description
        long_description = "a" * 1001
        invalid_data_2 = {
            "category_fields": {
                "name": "Long Description Test",
                "description": long_description
            }
        }
        
        response = client.post("/api/categories/",
                             data=json.dumps(invalid_data_2),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code in [400, 422]  # Validation should fail 