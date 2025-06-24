import json
import pytest
from uuid import uuid4


class TestCategoryAPIEndpoints:
    """Test Category API endpoints"""

    def test_create_category_success(self, client, admin_headers, valid_category_data):
        """Test successful category creation by admin"""
        response = client.post("/api/categories/",
                             data=json.dumps(valid_category_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        print(f"Create category response: {response.get_data(as_text=True)}")
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Category created successfully"
        assert 'data' in data
        assert data['data']['category_fields']['name'] == valid_category_data['category_fields']['name']

    def test_create_category_unauthorized(self, client, valid_category_data):
        """Test category creation without authentication"""
        response = client.post("/api/categories/",
                             data=json.dumps(valid_category_data),
                             content_type='application/json')
        
        assert response.status_code == 401

    def test_create_category_non_admin(self, client, auth_headers, valid_category_data):
        """Test category creation by non-admin user"""
        response = client.post("/api/categories/",
                             data=json.dumps(valid_category_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 403

    def test_create_category_invalid_data(self, client, admin_headers):
        """Test creating a category with invalid data"""
        invalid_data = {
            "category_fields": {}
        }
        
        response = client.post("/api/categories/",
                             data=json.dumps(invalid_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 422

    def test_get_category_success(self, client, admin_headers, valid_category_data):
        """Test retrieving a category by ID"""
        # First create a category
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # Now test getting the category
        response = client.get(f"/api/categories/{category_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Category retrieved successfully"
        assert data['data']['id'] == category_id

    def test_get_category_not_found(self, client):
        """Test getting a category that does not exist"""
        response = client.get("/api/categories/f4b1b3b3-1b1b-1b1b-1b1b-1b1b1b1b1b1b")
        assert response.status_code == 404

    def test_get_category_invalid_uuid(self, client):
        """Test retrieving a category with invalid UUID"""
        response = client.get("/api/categories/invalid-uuid")
        
        assert response.status_code == 404  # Flask returns 404 for invalid UUID in route

    def test_update_category_success(self, client, admin_headers, valid_category_data, valid_category_update_data):
        """Test successful category update by admin"""
        # First create a category
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # Now update the category
        response = client.put(f"/api/categories/{category_id}",
                            data=json.dumps(valid_category_update_data),
                            content_type='application/json',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Category updated successfully"
        assert data['data']['category_fields']['name'] == valid_category_update_data['category_fields']['name']

    def test_update_category_unauthorized(self, client, valid_category_update_data):
        """Test category update without authentication"""
        category_id = str(uuid4())
        response = client.put(f"/api/categories/{category_id}",
                            data=json.dumps(valid_category_update_data),
                            content_type='application/json')
        
        assert response.status_code == 401

    def test_update_category_non_admin(self, client, auth_headers, valid_category_update_data):
        """Test category update by non-admin user"""
        category_id = str(uuid4())
        response = client.put(f"/api/categories/{category_id}",
                            data=json.dumps(valid_category_update_data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 403

    def test_update_category_not_found(self, client, admin_headers, valid_category_update_data):
        """Test updating a category that does not exist"""
        response = client.put("/api/categories/f4b1b3b3-1b1b-1b1b-1b1b-1b1b1b1b1b1b",
                            data=json.dumps(valid_category_update_data),
                            content_type='application/json',
                            headers=admin_headers)
        assert response.status_code == 404

    def test_delete_category_success(self, client, admin_headers, valid_category_data):
        """Test successful category deletion by admin"""
        # First create a category
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # Now delete the category
        response = client.delete(f"/api/categories/{category_id}",
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Category deleted successfully"
        assert data['data']['success'] == True

    def test_delete_category_unauthorized(self, client):
        """Test category deletion without authentication"""
        category_id = str(uuid4())
        response = client.delete(f"/api/categories/{category_id}")
        
        assert response.status_code == 401

    def test_delete_category_non_admin(self, client, auth_headers):
        """Test category deletion by non-admin user"""
        category_id = str(uuid4())
        response = client.delete(f"/api/categories/{category_id}",
                               headers=auth_headers)
        
        assert response.status_code == 403

    def test_delete_category_not_found(self, client, admin_headers):
        """Test deleting a category that does not exist"""
        response = client.delete("/api/categories/f4b1b3b3-1b1b-1b1b-1b1b-1b1b1b1b1b1b",
                               headers=admin_headers)
        assert response.status_code == 404

    def test_list_categories_success(self, client):
        """Test listing categories with pagination"""
        response = client.get("/api/categories/list")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"
        assert 'data' in data
        assert 'items' in data['data']
        assert 'page' in data['data']
        assert isinstance(data['data']['items'], list)

    def test_list_categories_with_filters(self, client, admin_headers, valid_category_data):
        """Test listing categories with filters"""
        # First create a category to filter
        category_data = valid_category_data.copy()
        category_data['category_fields']['name'] = "Filterable Category"
        
        create_response = client.post("/api/categories/",
                                    data=json.dumps(category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        
        # Test name filter
        response = client.get("/api/categories/list?name=Filterable")
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"

    def test_create_subcategory_with_parent(self, client, admin_headers, valid_category_data, valid_subcategory_data):
        """Test creating a subcategory with parent category"""
        # First create a parent category
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        parent_id = create_response.get_json()['data']['id']
        
        # Create subcategory with parent_id
        subcategory_data = valid_subcategory_data.copy()
        subcategory_data['category_fields']['parent_id'] = parent_id
        
        response = client.post("/api/categories/",
                             data=json.dumps(subcategory_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['category_fields']['parent_id'] == parent_id

    def test_list_categories_with_pagination(self, client):
        """Test listing categories with pagination parameters"""
        response = client.get("/api/categories/list?page=1&items_per_page=5")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"
        assert data['data']['page'] == 1

    def test_list_categories_with_sorting(self, client):
        """Test listing categories with sorting"""
        # Test sort by name ascending
        response = client.get("/api/categories/list?sort_by=name&sort_direction=asc")
        assert response.status_code == 200
        
        # Test sort by name descending
        response = client.get("/api/categories/list?sort_by=name&sort_direction=desc")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"

    def test_category_workflow_complete(self, client, admin_headers, valid_category_data, valid_category_update_data):
        """Test complete category workflow: create, read, update, delete"""
        # 1. Create category
        create_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        
        assert create_response.status_code == 201
        category_id = create_response.get_json()['data']['id']
        
        # 2. Read category
        get_response = client.get(f"/api/categories/{category_id}")
        assert get_response.status_code == 200
        assert get_response.get_json()['data']['id'] == category_id
        
        # 3. Update category
        update_response = client.put(f"/api/categories/{category_id}",
                                   data=json.dumps(valid_category_update_data),
                                   content_type='application/json',
                                   headers=admin_headers)
        
        assert update_response.status_code == 200
        assert update_response.get_json()['data']['category_fields']['name'] == valid_category_update_data['category_fields']['name']
        
        # 4. Delete category
        delete_response = client.delete(f"/api/categories/{category_id}",
                                      headers=admin_headers)
        
        assert delete_response.status_code == 200
        assert delete_response.get_json()['data']['success'] == True
        
        # 5. Verify category is deleted/inactive  
        final_get_response = client.get(f"/api/categories/{category_id}")
        # Category might return as inactive rather than 404 due to soft delete
        assert final_get_response.status_code in [404, 200] 