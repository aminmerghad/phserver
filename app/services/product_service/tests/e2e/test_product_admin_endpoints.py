import json
import pytest
from uuid import uuid4


class TestProductAdminEndpoints:
    """Test Product Admin-only API endpoints"""

    def test_get_low_stock_products_success(self, client, admin_headers):
        """Test getting low stock products as admin"""
        response = client.get("/api/products/low-stock",
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Low stock products retrieved successfully"
        assert 'data' in data
        assert 'items' in data['data']

    def test_get_low_stock_products_with_threshold(self, client, admin_headers):
        """Test getting low stock products with custom threshold"""
        filters = {
            "threshold_percentage": 50,
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/low-stock",
                            query_string=filters,
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Low stock products retrieved successfully"

    def test_get_low_stock_products_unauthorized(self, client):
        """Test getting low stock products without admin privileges"""
        response = client.get("/api/products/low-stock")
        
        assert response.status_code == 401  # Unauthorized

    def test_get_expiring_products_success(self, client, admin_headers):
        """Test getting expiring products as admin"""
        response = client.get("/api/products/expiring",
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Expiring products retrieved successfully"
        assert 'data' in data
        assert 'items' in data['data']

    def test_get_expiring_products_with_days_threshold(self, client, admin_headers):
        """Test getting expiring products with custom days threshold"""
        filters = {
            "days_threshold": 30,
            "page": 1,
            "page_size": 10
        }
        
        response = client.get("/api/products/expiring",
                            query_string=filters,
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Expiring products retrieved successfully"

    def test_get_expiring_products_unauthorized(self, client):
        """Test getting expiring products without admin privileges"""
        response = client.get("/api/products/expiring")
        
        assert response.status_code == 401  # Unauthorized

    def test_bulk_create_products_success(self, client, admin_headers, bulk_products_data):
        """Test successful bulk product creation"""
        response = client.post("/api/products/bulk",
                             data=json.dumps(bulk_products_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        print(f"Bulk create response: {response.get_data(as_text=True)}")
        assert response.status_code == 201
        data = response.get_json()
        assert "Successfully created" in data['message']
        assert 'data' in data

    def test_bulk_create_products_unauthorized(self, client, bulk_products_data):
        """Test bulk product creation without admin privileges"""
        response = client.post("/api/products/bulk",
                             data=json.dumps(bulk_products_data),
                             content_type='application/json')
        
        assert response.status_code == 401  # Unauthorized

    def test_bulk_create_products_invalid_data(self, client, admin_headers):
        """Test bulk product creation with invalid data"""
        invalid_bulk_data = {
            "products": [
                {
                    "product_fields": {
                        "name": "",  # Empty name should fail
                        "description": "Invalid product"
                    },
                    "inventory_fields": {
                        "price": -10,  # Negative price should fail
                        "quantity": -5,
                        "max_stock": 100,
                        "min_stock": 10,
                        "expiry_date": "2025-12-31"
                    }
                }
            ]
        }
        
        response = client.post("/api/products/bulk",
                             data=json.dumps(invalid_bulk_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400  # Bad request

    def test_bulk_create_empty_products_list(self, client, admin_headers):
        """Test bulk product creation with empty products list"""
        empty_bulk_data = {"products": []}
        
        response = client.post("/api/products/bulk",
                             data=json.dumps(empty_bulk_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400  # Bad request

    def test_bulk_create_too_many_products(self, client, admin_headers):
        """Test bulk product creation with too many products"""
        # Create more than 100 products (if that's the limit)
        too_many_products = {
            "products": []
        }
        
        # Create 101 products
        for i in range(101):
            product = {
                "product_fields": {
                    "name": f"Product {i}",
                    "description": f"Product {i} description",
                    "status": "ACTIVE"
                },
                "inventory_fields": {
                    "price": 10.0,
                    "quantity": 50,
                    "max_stock": 100,
                    "min_stock": 10,
                    "expiry_date": "2025-12-31"
                }
            }
            too_many_products["products"].append(product)
        
        response = client.post("/api/products/bulk",
                             data=json.dumps(too_many_products),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400  # Bad request

    def test_create_product_as_admin_success(self, client, admin_headers, valid_product_data):
        """Test creating a product as admin user"""
        response = client.post("/api/products/",
                             data=json.dumps(valid_product_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Product created successfully"
        assert 'data' in data
        assert data['data']['product_fields']['name'] == valid_product_data['product_fields']['name']

    def test_update_product_as_admin_success(self, client, admin_headers, valid_product_data):
        """Test updating a product as admin user"""
        # First create a product
        create_response = client.post("/api/products/",
                                    data=json.dumps(valid_product_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        product_id = create_response.get_json()['data']['id']
        
        # Update the product
        update_data = {
            "product_fields": {
                "name": "Updated Medicine Name",
                "description": "Updated description",
                "brand": "Updated Brand",
                "status": "ACTIVE"
            },
            "inventory_fields": {
                "price": 35.00,
                "quantity": 200,
                "max_stock": 400,
                "min_stock": 30,
                "expiry_date": "2026-06-01"
            }
        }
        
        response = client.put(f"/api/products/{product_id}",
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product updated successfully"
        assert data['data']['product_fields']['name'] == "Updated Medicine Name"

    def test_delete_product_as_admin_success(self, client, admin_headers, valid_product_data):
        """Test deleting a product as admin user"""
        # First create a product
        create_response = client.post("/api/products/",
                                    data=json.dumps(valid_product_data),
                                    content_type='application/json',
                                    headers=admin_headers)
        assert create_response.status_code == 201
        product_id = create_response.get_json()['data']['id']
        
        # Delete the product
        response = client.delete(f"/api/products/{product_id}",
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Product deleted successfully"
        
        # Verify product is deleted
        get_response = client.get(f"/api/products/{product_id}")
        assert get_response.status_code == 404 