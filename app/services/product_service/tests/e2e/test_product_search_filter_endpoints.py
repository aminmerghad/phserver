import json
import pytest
from uuid import uuid4


class TestProductSearchFilterEndpoints:
    """Test Product Search and Filter API endpoints"""

    def test_search_products_by_name(self, client, admin_headers, valid_product_data):
        """Test searching products by name"""
        # First create a product with a specific name
        product_data = valid_product_data.copy()
        product_data['product_fields']['name'] = "Aspirin Special Test"
        
        create_response = client.post("/api/products/",
                                    data=json.dumps(product_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        
        # Search for the product
        search_params = {
            "search": "Aspirin",
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"
        assert 'data' in data

    def test_search_products_by_brand(self, client, admin_headers, valid_product_data):
        """Test searching products by brand"""
        # Create a product with specific brand
        product_data = valid_product_data.copy()
        product_data['product_fields']['brand'] = "TestBrand Pharmaceuticals"
        
        create_response = client.post("/api/products/",
                                    data=json.dumps(product_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        
        # Search by brand
        search_params = {
            "brand": "TestBrand",
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"

    def test_search_products_with_price_range(self, client):
        """Test searching products within price range"""
        search_params = {
            "min_price": 10.0,
            "max_price": 50.0,
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"

    def test_search_products_in_stock_only(self, client):
        """Test searching only products in stock"""
        search_params = {
            "in_stock_only": True,
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"

    def test_list_products_with_name_filter(self, client):
        """Test listing products with name filter"""
        filters = {
            "name": "medicine",
            "page": 1,
            "items_per_page": 10
        }
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"

    def test_list_products_with_brand_filter(self, client):
        """Test listing products with brand filter"""
        filters = {
            "brand": "test",
            "page": 1,
            "items_per_page": 10
        }
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"

    def test_list_products_with_status_filter(self, client):
        """Test listing products with status filter"""
        filters = {
            "status": "ACTIVE",
            "page": 1,
            "items_per_page": 10
        }
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"

    def test_list_products_with_sorting(self, client):
        """Test listing products with different sorting options"""
        # Test sorting by name ascending
        filters = {
            "sort_by": "name",
            "sort_direction": "asc",
            "page": 1,
            "items_per_page": 10
        }
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"
        
        # Test sorting by name descending
        filters['sort_direction'] = "desc"
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200

    def test_list_products_pagination(self, client):
        """Test product list pagination"""
        # Test first page
        filters = {
            "page": 1,
            "items_per_page": 5
        }

        
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        print(data)
        assert data['message'] == "Products retrieved successfully"
        assert data['data']['page'] == 1
        # assert data['data']['total_pages'] == 5

        # Test second page if there are enough items
        filters['page'] = 2
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['page'] == 2

    def test_search_with_empty_query(self, client):
        """Test search with empty search term"""
        search_params = {
            "search": "",
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"

    def test_search_with_invalid_page(self, client):
        """Test search with invalid page number"""
        search_params = {
            "search": "test",
            "page": -1,  # Invalid page
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        # Should handle gracefully or return appropriate error

    def test_search_with_large_page_size(self, client):
        """Test search with very large page size"""
        search_params = {
            "search": "test",
            "page": 1,
            "page_size": 1000  # Very large page size
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"

    def test_list_products_with_multiple_filters(self, client):
        """Test listing products with multiple filters combined"""
        filters = {
            "name": "medicine",
            "brand": "test",
            "sort_by": "name",
            "sort_direction": "asc",
            "page": 1,
            "items_per_page": 10
        }
        
        response = client.get("/api/products/list", query_string=filters)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"

    def test_search_products_no_results(self, client):
        """Test search that returns no results"""
        search_params = {
            "search": "nonexistentproductthatdoesnotexist",
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/search", query_string=search_params)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product search completed successfully"
        # Should return empty items list
        # assert data['data']['total_items'] == 0 