"""
# Tests for the StockCheck functionality using real service implementation
# """
# import pytest
# from uuid import uuid4

# from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckItemContract
# from app.shared.contracts.inventory.enums import StockStatusContract

# class TestStockCheckReal:
#     """Tests for stock check using real service implementation"""
    
#     def test_available_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for a product with sufficient stock"""
#         with app.app_context():
#             # Arrange
            
#             product_id = test_products['regular_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             assert response.data[0].stock_validation_result.is_available is True
#             assert StockStatusContract.AVAILABLE in response.data[0].stock_validation_result.status
#             assert response.data[0].stock_validation_result.remaining_stock == 90  # 100 - 10
#             assert len(response.data[0].stock_validation_result.warnings) == 0  # No warnings
    
#     def test_expired_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for an expired product"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['expired_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=5)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             # assert response.data[0].stock_validation_result.is_available is False
#             assert StockStatusContract.EXPIRED in response.data[0].stock_validation_result.status
#             assert response.data[0].product_name == "Expired Medicine"
#             assert any("expired" in warning.lower() for warning in response.data[0].stock_validation_result.warnings)
#             # Days until expiry should be negative for expired products
#             assert response.data[0].stock_validation_result.days_until_expiry < 0
    
#     def test_low_stock_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for a product with low stock"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['low_stock_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=5)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             # Low stock is still available
#             assert response.data[0].stock_validation_result.is_available is True
#             assert StockStatusContract.LOW_STOCK in response.data[0].stock_validation_result.status
#             assert response.data[0].stock_validation_result.remaining_stock == 10  # 15 - 5
#             # Should have low stock warning
#             assert any("minimum" in warning.lower() for warning in response.data[0].stock_validation_result.warnings)
    
#     def test_expiring_soon_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for a product expiring soon"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['expiring_soon_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             # Expiring soon is still available
#             assert response.data[0].stock_validation_result.is_available is True
#             assert StockStatusContract.EXPIRING_SOON in response.data[0].stock_validation_result.status
#             assert response.data[0].stock_validation_result.days_until_expiry == 15
#             # Should have expiry warning
#             assert any("expir" in warning.lower() for warning in response.data[0].stock_validation_result.warnings)
    
#     def test_inactive_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for an inactive product"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['inactive_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             assert response.data[0].stock_validation_result.is_available is False
#             assert StockStatusContract.INACTIVE in response.data[0].stock_validation_result.status
#             # Should have inactive warning
#             assert any("inactive" in warning.lower() or "not active" in warning.lower() 
#                   for warning in response.data[0].stock_validation_result.warnings)
    
#     def test_combined_issues_product(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for a product with multiple issues (low stock and expiring soon)"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['combined_issues_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             assert response.data[0].stock_validation_result.is_available is True
            
#             # Status should be either LOW_STOCK or EXPIRING_SOON depending on prioritization
#             assert StockStatusContract.EXPIRING_SOON in response.data[0].stock_validation_result.status 
#             assert StockStatusContract.LOW_STOCK in response.data[0].stock_validation_result.status 
#             # Should have remaining stock of 15 (25 - 10)
#             assert response.data[0].stock_validation_result.remaining_stock == 15
            
#             # Should have both warnings
#             warnings = response.data[0].stock_validation_result.warnings
#             has_expiry_warning = any("expir" in warning.lower() for warning in warnings)
#             has_stock_warning = any("minimum" in warning.lower() for warning in warnings)
            
#             assert has_expiry_warning, "Missing expiry warning"
#             assert has_stock_warning, "Missing stock warning"
    
#     def test_insufficient_stock(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for a product with insufficient stock"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['regular_id']
#             # Request more than available (100)
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=150)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             assert response.data[0].stock_validation_result.is_available is False
#             assert StockStatusContract.INSUFFICIENT_STOCK in response.data[0].stock_validation_result.status
            
#             # Warning message should mention insufficient stock
#             assert any("insufficient" in warning.lower() for warning in 
#                       response.data[0].stock_validation_result.warnings)
    
#     def test_nonexistent_product(self, app, inventory_service):
#         """Test stock check for a nonexistent product"""
#         with app.app_context():
#             # Arrange
#             nonexistent_id = uuid4()
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=nonexistent_id, quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is False
#             assert response.errors is not None
#             assert len(response.errors) == 1
#             assert "not found" in response.errors[0].message.lower()
    
#     def test_multiple_products(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check for multiple products in a single request"""
#         with app.app_context():
#             # Arrange
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=test_products['regular_id'], quantity=10),
#                     StockCheckItemContract(product_id=test_products['expired_id'], quantity=5),
#                     StockCheckItemContract(product_id=test_products['low_stock_id'], quantity=5),
#                     StockCheckItemContract(product_id=test_products['expiring_soon_id'], quantity=10)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 4
            
#             # Check summary information
#             assert response.summary.total_items == 4
#             assert response.summary.available_items == 3  # All except expired
#             assert response.summary.unavailable_items == 1  # Expired product
            
#             # Convert results to dictionary for easy access by product ID
#             results_by_product = {str(item.product_id): item for item in response.data}
            
#             # Check regular product
#             regular = results_by_product[str(test_products['regular_id'])]
#             assert StockStatusContract.AVAILABLE in regular.stock_validation_result.status
#             assert regular.stock_validation_result.is_available is True
            
#             # Check expired product
#             expired = results_by_product[str(test_products['expired_id'])]
#             assert StockStatusContract.EXPIRED in expired.stock_validation_result.status
#             assert expired.stock_validation_result.is_available is False
            
#             # Check low stock product
#             low_stock = results_by_product[str(test_products['low_stock_id'])]
#             assert StockStatusContract.LOW_STOCK in low_stock.stock_validation_result.status
#             assert low_stock.stock_validation_result.is_available is True
            
#             # Check expiring soon product
#             expiring = results_by_product[str(test_products['expiring_soon_id'])]
#             assert StockStatusContract.EXPIRING_SOON in expiring.stock_validation_result.status
#             assert expiring.stock_validation_result.is_available is True
    
#     def test_zero_quantity_request(self, app, inventory_service, test_products, test_inventory):
#         """Test stock check with zero quantity requested"""
#         with app.app_context():
#             # Arrange
#             product_id = test_products['regular_id']
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=0)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             assert len(response.data) == 1
#             assert response.data[0].stock_validation_result.is_available is True
#             assert StockStatusContract.AVAILABLE in response.data[0].stock_validation_result.status
#             assert response.data[0].stock_validation_result.remaining_stock == 100  # Unchanged
#             assert len(response.data[0].stock_validation_result.warnings) == 0  # No warnings 