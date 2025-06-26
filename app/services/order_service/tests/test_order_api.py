import json
import pytest
from uuid import uuid4, UUID
from http import HTTPStatus
from flask import Flask
from app.services.order_service.domain.value_objects.order_status import OrderStatus

def test_create_order(client, auth_headers, app):
    """Test creating a new order"""
    # Arrange
    with app.app_context():
        product1_id = app.config['TEST_PRODUCT1_ID']
        product2_id = app.config['TEST_PRODUCT2_ID']
    
    order_data = {
        'items': [
            {
                'product_id': product1_id,
                'quantity': 2
            },
            {
                'product_id': product2_id,
                'quantity': 1
            }
        ],
        'notes': 'Test order'
    }
    
    # Act
    response = client.post(
        '/order/orders',
        json=order_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.CREATED
    data = json.loads(response.data)
    assert data['message'] == 'Order created successfully'
    assert data['data']['status'] == OrderStatus.PENDING.value
    assert len(data['data']['items']) == 2
    assert data['data']['notes'] == 'Test order'
    
    # Save order ID for other tests
    order_id = data['data']['order_id']
    
    # Clean up - Not needed as we're using a function-scoped test database
    
    return order_id

def test_create_order_invalid_data(client, auth_headers, app):
    """Test creating an order with invalid data"""
    # Arrange - Empty items array
    invalid_order_data = {
        'items': [],
        'notes': 'Invalid order with no items'
    }
    
    # Act
    response = client.post(
        '/order/orders',
        json=invalid_order_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data  # Error message format may vary

def test_create_order_invalid_quantity(client, auth_headers, app):
    """Test creating an order with invalid quantity"""
    # Arrange
    with app.app_context():
        product1_id = app.config['TEST_PRODUCT1_ID']
    
    invalid_order_data = {
        'items': [
            {
                'product_id': product1_id,
                'quantity': 0  # Invalid quantity (should be > 0)
            }
        ],
        'notes': 'Invalid order with zero quantity'
    }
    
    # Act
    response = client.post(
        '/order/orders',
        json=invalid_order_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data  # Error message format may vary

def test_create_order_nonexistent_product(client, auth_headers):
    """Test creating an order with a product that doesn't exist"""
    # Arrange
    nonexistent_product_id = str(uuid4())
    
    invalid_order_data = {
        'items': [
            {
                'product_id': nonexistent_product_id,
                'quantity': 1
            }
        ],
        'notes': 'Order with nonexistent product'
    }
    
    # Act
    response = client.post(
        '/order/orders',
        json=invalid_order_data,
        headers=auth_headers
    )
    
    # Assert - Should return a specific error about the product not existing
    assert response.status_code in [HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND]
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data  # Error message format may vary

def test_get_all_orders(client, auth_headers, app):
    """Test retrieving all orders"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    # Act
    response = client.get(
        '/order/orders',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1  # Should have at least the order we created
    
    # Check if our created order is in the list
    order_ids = [order['order_id'] for order in data['data']]
    assert order_id in order_ids

def test_get_order_by_id(client, auth_headers, app):
    """Test retrieving a specific order by ID"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    # Act
    response = client.get(
        f'/order/orders/{order_id}',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert data['message'] == 'Order retrieved successfully'
    assert data['data']['order_id'] == order_id
    assert data['data']['status'] == OrderStatus.PENDING.value
    assert len(data['data']['items']) == 2

def test_get_nonexistent_order(client, auth_headers):
    """Test retrieving an order that doesn't exist"""
    # Arrange
    nonexistent_id = str(uuid4())
    
    # Act
    response = client.get(
        f'/order/orders/{nonexistent_id}',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data

def test_update_order_status(client, auth_headers, app):
    """Test updating an order's status"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    update_data = {
        'status': OrderStatus.CONFIRMED.value
    }
    
    # Act
    response = client.put(
        f'/order/orders/{order_id}',
        json=update_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert data['message'] == 'Order status updated successfully'
    assert data['data']['status'] == OrderStatus.CONFIRMED.value

def test_update_nonexistent_order(client, auth_headers):
    """Test updating an order that doesn't exist"""
    # Arrange
    nonexistent_id = str(uuid4())
    
    update_data = {
        'status': OrderStatus.CONFIRMED.value
    }
    
    # Act
    response = client.put(
        f'/order/orders/{nonexistent_id}',
        json=update_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data

def test_invalid_status_transition(client, auth_headers, app):
    """Test invalid order status transition"""
    # Arrange - Create an order first (which will be in PENDING status)
    order_id = test_create_order(client, auth_headers, app)
    
    # Try to transition directly from PENDING to COMPLETED (which should be invalid)
    invalid_update_data = {
        'status': OrderStatus.COMPLETED.value
    }
    
    # Act
    response = client.put(
        f'/order/orders/{order_id}',
        json=invalid_update_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data

def test_cancel_order(client, auth_headers, app):
    """Test cancelling an order"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    # Act
    response = client.delete(
        f'/order/orders/{order_id}',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert data['message'] == 'Order cancelled successfully'
    assert data['data']['status'] == OrderStatus.CANCELLED.value

def test_cancel_nonexistent_order(client, auth_headers):
    """Test cancelling an order that doesn't exist"""
    # Arrange
    nonexistent_id = str(uuid4())
    
    # Act
    response = client.delete(
        f'/order/orders/{nonexistent_id}',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = json.loads(response.data)
    assert 'error' in data or 'message' in data

def test_get_user_orders(client, auth_headers, app):
    """Test retrieving orders for the current user"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    # Act
    response = client.get(
        '/order/user/orders',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.data)
    assert data['message'] == 'User orders retrieved successfully'
    assert isinstance(data['data'], list)
    
    # Check if our created order is in the list
    order_ids = [order['order_id'] for order in data['data']]
    assert order_id in order_ids

def test_unauthorized_access(client, app):
    """Test accessing endpoints without authentication"""
    # Arrange - No authentication headers
    
    # Act - Try to get all orders without authentication
    response = client.get('/order/orders')
    
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    
    # Act - Try to create an order without authentication
    with app.app_context():
        product1_id = app.config['TEST_PRODUCT1_ID']
    
    order_data = {
        'items': [
            {
                'product_id': product1_id,
                'quantity': 1
            }
        ]
    }
    
    response = client.post('/order/orders', json=order_data)
    
    # Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_order_status_transition_flow(client, auth_headers, app):
    """Test the complete order status transition flow"""
    # Arrange - Create an order first
    order_id = test_create_order(client, auth_headers, app)
    
    # Step 1: Confirm the order
    confirm_data = {
        'status': OrderStatus.CONFIRMED.value
    }
    
    confirm_response = client.put(
        f'/order/orders/{order_id}',
        json=confirm_data,
        headers=auth_headers
    )
    
    assert confirm_response.status_code == HTTPStatus.OK
    confirm_data = json.loads(confirm_response.data)
    assert confirm_data['data']['status'] == OrderStatus.CONFIRMED.value
    
    # Step 2: Complete the order
    complete_data = {
        'status': OrderStatus.COMPLETED.value
    }
    
    complete_response = client.put(
        f'/order/orders/{order_id}',
        json=complete_data,
        headers=auth_headers
    )
    
    assert complete_response.status_code == HTTPStatus.OK
    complete_data = json.loads(complete_response.data)
    assert complete_data['data']['status'] == OrderStatus.COMPLETED.value
    
    # Step 3: Try to cancel a completed order (should fail)
    cancel_response = client.delete(
        f'/order/orders/{order_id}',
        headers=auth_headers
    )
    
    # This should fail as a completed order cannot be cancelled 