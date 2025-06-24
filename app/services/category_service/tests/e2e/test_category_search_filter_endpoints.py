import json
import pytest
from uuid import uuid4


class TestCategorySearchFilterEndpoints:
    """Test Category Search and Filter API endpoints"""

    def test_search_categories_by_name(self, client, admin_headers, valid_category_data):
        """Test searching categories by name"""
        # First create a category with a specific name
        category_data = valid_category_data.copy()
        category_data['category_fields']['name'] = "Special Test Category"
        
        create_response = client.post("/api/categories/",
                                    data=json.dumps(category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        
        # Search for the category by name
        response = client.get("/api/categories/list?name=Special")
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"
        
        # Verify the created category is in results
        found = any(item['category_fields']['name'] == "Special Test Category" 
                   for item in data['data']['items'])
        assert found

    def test_search_categories_case_insensitive(self, client, admin_headers, valid_category_data):
        """Test case insensitive category search"""
        # Create a category with mixed case
        category_data = valid_category_data.copy()
        category_data['category_fields']['name'] = "MixedCase Category"
        
        create_response = client.post("/api/categories/",
                                    data=json.dumps(category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        
        # Search with lowercase
        response = client.get("/api/categories/list?name=mixedcase")
        assert response.status_code == 200
        data = response.get_json()
        
        # Should find the category regardless of case
        found = any("mixedcase" in item['category_fields']['name'].lower() 
                   for item in data['data']['items'])
        assert found

    def test_filter_categories_by_active_status(self, client, admin_headers):
        """Test filtering categories by active status"""
        # Filter for active categories only
        response = client.get("/api/categories/list?is_active=true")
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"

    def test_filter_categories_by_parent(self, client, admin_headers, valid_category_data, valid_subcategory_data):
        """Test filtering categories by parent ID"""
        # Create a parent category
        parent_response = client.post("/api/categories/",
                                    data=json.dumps(valid_category_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert parent_response.status_code == 201
        parent_id = parent_response.get_json()['data']['id']
        
        # Create a subcategory
        subcategory_data = valid_subcategory_data.copy()
        subcategory_data['category_fields']['parent_id'] = parent_id
        
        sub_response = client.post("/api/categories/",
                                 data=json.dumps(subcategory_data),
                                 content_type='application/json',
                                 headers=admin_headers)
        assert sub_response.status_code == 201
        
        # Filter by parent ID
        response = client.get(f"/api/categories/list?parent_id={parent_id}")
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify all returned categories have the correct parent
        for item in data['data']['items']:
            if item['category_fields']['parent_id']:
                assert item['category_fields']['parent_id'] == parent_id

    def test_category_pagination(self, client):
        """Test category list pagination"""
        # Test first page
        response = client.get("/api/categories/list?page=1&items_per_page=5")
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['data']['page'] == 1
        assert data['message'] == "Categories retrieved successfully"

    def test_category_sorting(self, client):
        """Test category list sorting"""
        # Test ascending sort
        response = client.get("/api/categories/list?sort_by=name&sort_direction=asc")
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Categories retrieved successfully"

    def test_combined_filters(self, client, admin_headers):
        """Test combining multiple filters"""
        # Create categories with different attributes
        test_categories = [
            {"name": "Active Filter Test", "is_active": True},
            {"name": "Inactive Filter Test", "is_active": False},
            {"name": "Another Active", "is_active": True}
        ]
        
        category_ids = []
        for cat in test_categories:
            category_data = {
                "category_fields": {
                    "name": cat["name"],
                    "description": "Combined filter test category",
                    "is_active": cat["is_active"]
                }
            }
            
            response = client.post("/api/categories/",
                                 data=json.dumps(category_data),
                                 content_type='application/json',
                                 headers=admin_headers)
            assert response.status_code == 201
            category_ids.append(response.get_json()['data']['id'])
        
        # Combine name and active status filters
        response = client.get("/api/categories/list?name=Filter&is_active=true")
        assert response.status_code == 200
        data = response.get_json()
        
        # Should only return active categories with "Filter" in the name
        for item in data['data']['items']:
            if "Filter" in item['category_fields']['name']:
                assert item['category_fields']['is_active'] == True
        
        # Clean up created categories
        for category_id in category_ids:
            client.delete(f"/api/categories/{category_id}", headers=admin_headers)

    def test_empty_search_results(self, client):
        """Test search with no matching results"""
        response = client.get("/api/categories/list?name=NonExistentCategoryName12345")
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "Categories retrieved successfully"
        assert len(data['data']['items']) == 0
        assert data['data']['total_items'] == 0

    def test_invalid_filter_parameters(self, client):
        """Test handling of invalid filter parameters"""
        # Test invalid sort direction
        response = client.get("/api/categories/list?sort_direction=invalid")
        assert response.status_code == 422
        
        # Test invalid page number
        response = client.get("/api/categories/list?page=-1")
        assert response.status_code == 422
        
        # Test invalid items_per_page
        response = client.get("/api/categories/list?items_per_page=0")
        assert response.status_code == 422 