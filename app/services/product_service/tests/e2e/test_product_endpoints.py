import json
import pytest
from uuid import uuid4

from app.services.product_service.service import ProductService
from app.services.product_service.application.commands.create_product_command import CreateProductCommand
from app.services.product_service.application.commands.update_product_command import UpdateProductCommand
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto as ProductDTO
from app.services.product_service.domain.enums.product_status import ProductStatus


class TestProductAPIEndpoints:
    """Test Product API endpoints"""

    def test_create_product_success(self, client, admin_headers, valid_product_data):
        """Test successful product creation by admin"""
        response = client.post("/api/products/",
                             data=json.dumps(valid_product_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        print(f"Create product response: {response.get_data(as_text=True)}")
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Product created successfully"
        assert 'id' in data['data']['product_fields']
        assert data['data']['product_fields']['name'] == valid_product_data['product_fields']['name']
        assert data['data']['product_fields']['status'] == ProductStatus.ACTIVE.value
        
        # Return product ID for other tests
        return data['data']['product_fields']['id']

    def test_create_product_unauthorized(self, client, valid_product_data):
        """Test product creation without admin privileges"""
        response = client.post("/api/products/",
                             data=json.dumps(valid_product_data),
                             content_type='application/json')
        
        assert response.status_code == 401  # Unauthorized

    def test_create_product_non_admin(self, client, auth_headers, valid_product_data):
        response = client.post("/api/products/",
                             data=json.dumps(valid_product_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 403

    def test_create_product_invalid_data(self, client, admin_headers, valid_product_data):
        """Test product creation with invalid data"""
        invalid_data = valid_product_data.copy()
        invalid_data['name'] = ''  # Invalid name
        response = client.post("/api/products/",
                             data=json.dumps(invalid_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 422  # Bad request

    def test_get_product_success(self, client, test_products):
        """Test retrieving a product by ID"""
        product_id = test_products[0].id
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == str(product_id)

    def test_get_product_not_found(self, client):
        """Test retrieving a non-existent product"""
        non_existent_id = uuid4()
        response = client.get(f"/api/products/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data['message'].lower()

    def test_update_product_success(self, client, admin_headers, test_products):
        """Test successful product update by admin"""
        product_to_update = test_products[0]
        update_data = {
            "name": "Updated Product Name",
            "description": "Updated description.",
            "price": 150.00,
            "status": ProductStatus.INACTIVE.value
        }
        response = client.put(f"/api/products/{product_to_update.id}",
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['name'] == "Updated Product Name"
        assert data['data']['status'] == ProductStatus.INACTIVE.value

    def test_update_product_unauthorized(self, client, valid_product_data):
        """Test product update without admin privileges"""
        product_id = str(uuid4())
        
        response = client.put(f"/api/products/{product_id}",
                            data=json.dumps(valid_product_data),
                            content_type='application/json')
        
        assert response.status_code == 401  # Unauthorized

    def test_delete_product_success(self, client, admin_headers, test_products):
        """Test successful product deletion by admin"""
        product_to_delete = test_products[0]
        response = client.delete(f"/api/products/{product_to_delete.id}",
                               headers=admin_headers)
        assert response.status_code == 200
        # Optionally, verify the product is marked as deleted or removed
        get_response = client.get(f"/api/products/{product_to_delete.id}")
        assert get_response.status_code == 404

    def test_delete_product_unauthorized(self, client):
        """Test product deletion without admin privileges"""
        product_id = str(uuid4())
        
        response = client.delete(f"/api/products/{product_id}")
        
        assert response.status_code == 401  # Unauthorized

    def test_list_products_paginated(self, client, test_products):
        """Test listing products with pagination"""
        response = client.get("/api/products/list?page=1&items_per_page=2")
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 2
        assert data['data']['page'] == 1

    def test_filter_products_by_status(self, client, test_products):
        """Test listing products with filters"""
        response = client.get("/api/products/list?status=ACTIVE")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"
        for item in data['data']['items']:
            assert item['status'] == ProductStatus.ACTIVE.value

    def test_search_products_by_name(self, client, test_products):
        """Test searching products"""
        response = client.get("/api/products/list?name=Product 1")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Products retrieved successfully"
        assert len(data['data']['items']) > 0
        assert "Product 1" in data['data']['items'][0]['name']

    def test_get_product_stock_status(self, client):
        """Test getting product stock status"""
        # Get a product ID from the list first
        list_response = client.get("/api/products/list")
        if list_response.status_code == 200:
            data = list_response.get_json()
            if data['data']['items']:
                product_id = data['data']['items'][0]['id']
                
                response = client.get(f"/api/products/{product_id}/stock-status")
                assert response.status_code == 200
                data = response.get_json()
                assert data['message'] == "Product stock status retrieved successfully"
                assert 'data' in data

    def test_bulk_create_products_success(self, client, admin_headers, bulk_products_data):
        """Test successful bulk product creation by admin"""
        response = client.post("/api/products/bulk",
                             data=json.dumps({"products": bulk_products_data}),
                             content_type='application/json',
                             headers=admin_headers)
        
        print(f"Bulk create response: {response.get_data(as_text=True)}")
        assert response.status_code == 201
        data = response.get_json()
        assert len(data['data']) == len(bulk_products_data)

    def test_bulk_create_products_unauthorized(self, client, bulk_products_data):
        """Test bulk product creation without admin privileges"""
        response = client.post("/api/products/bulk",
                             data=json.dumps({"products": bulk_products_data}),
                             content_type='application/json')
        
        assert response.status_code == 401  # Unauthorized

    def test_get_low_stock_products_success(self, client, admin_headers):
        """Test getting low stock products by admin"""
        response = client.get("/api/products/low-stock",
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Low stock products retrieved successfully"

    def test_get_low_stock_products_unauthorized(self, client):
        """Test getting low stock products without admin privileges"""
        response = client.get("/api/products/low-stock")
        
        assert response.status_code == 401  # Unauthorized

    def test_get_expiring_products_success(self, client, admin_headers):
        """Test getting expiring products by admin"""
        response = client.get("/api/products/expiring",
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Expiring products retrieved successfully"

    def test_get_expiring_products_unauthorized(self, client):
        """Test getting expiring products without admin privileges"""
        response = client.get("/api/products/expiring")
        
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.xfail(reason="Category filtering not fully implemented")
    def test_get_products_by_category(self, client, test_products, test_category):
        """Test getting products by category"""
        # Associate a product with the category
        product = test_products[0]
        # This requires an endpoint or a direct db update to associate product with category
        # For now, let's assume the test_products fixture handles this
        
        response = client.get(f"/api/products/list?category_id={test_category.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) > 0
        # Further assertions to verify the products belong to the category 