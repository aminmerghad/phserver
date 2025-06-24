# import pytest
# from datetime import date, datetime, timedelta
# from uuid import uuid4

# from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
# from app.services.inventory_service.domain.entities.product_entity import ProductEntity
# from app.services.inventory_service.domain.enums.product_status import ProductStatus
# from app.services.inventory_service.application.use_cases.stock_check import StockCheckUseCase
# from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckItemContract
# from app.shared.contracts.inventory.enums import StockStatusContract

# # Mock Unit of Work for testing
# class MockUnitOfWork:
#     def __init__(self, products=None, inventory_items=None):
#         self.products = products or {}
#         self.inventory_items = inventory_items or {}
#         self.committed = False
        
#     def __enter__(self):
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         pass
        
#     def commit(self):
#         self.committed = True
        
#     @property
#     def inventory(self):
#         return self
        
#     @property
#     def product(self):
#         return self
        
#     def get_by_id(self, product_id):
#         return self.products.get(product_id)
        
#     def get_by_product_id(self, product_id):
#         return self.inventory_items.get(product_id)

# # Test fixtures
# @pytest.fixture
# def product_id():
#     """Generate a unique product ID for testing"""
#     return uuid4()

# @pytest.fixture
# def base_product(product_id):
#     """Create a basic product entity for testing"""
#     return ProductEntity(
#         id=product_id,
#         name="Test Product",
#         description="Test product description",
#         status=ProductStatus.ACTIVE
#     )

# @pytest.fixture
# def base_inventory(product_id):
#     """Create a basic inventory entity for testing"""
#     return InventoryEntity(
#         id=uuid4(),
#         product_id=product_id,
#         quantity=100,
#         price=10.0,
#         max_stock=200,
#         min_stock=20,
#         expiry_date=date.today() + timedelta(days=180)
#     )

# @pytest.fixture
# def mock_uow(base_product, base_inventory):
#     """Create a mock unit of work with a product and inventory"""
#     return MockUnitOfWork(
#         products={base_product.id: base_product},
#         inventory_items={base_product.id: base_inventory}
#     )

# # Tests for stock validation
# class TestStockValidation:
#     """Test the stock validation functionality"""
    
#     def test_validate_available_stock(self, base_inventory):
#         """Test validation when stock is available with no warnings"""
#         # Arrange
#         requested_quantity = 30  # Well above min_stock threshold
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == True
#         assert result.remaining_stock == 70
#         assert not result.warnings
#         assert result.status == StockStatusContract.AVAILABLE
    
#     def test_validate_low_stock(self, base_inventory):
#         """Test validation when request would leave stock below minimum level"""
#         # Arrange
#         requested_quantity = 85  # Leaves 15 units (below min_stock of 20)
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == True
#         assert result.remaining_stock == 15
#         assert any("below minimum level" in warning for warning in result.warnings)
#         assert result.status == StockStatusContract.LOW_STOCK
    
#     def test_validate_insufficient_stock(self, base_inventory):
#         """Test validation when requested quantity exceeds available stock"""
#         # Arrange
#         requested_quantity = 150  # More than available (100)
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == False
#         assert result.remaining_stock == 100  # Should remain unchanged
#         assert any("Insufficient stock" in warning for warning in result.warnings)
#         assert result.status == StockStatusContract.INSUFFICIENT_STOCK
    
#     def test_validate_out_of_stock(self, base_inventory):
#         """Test validation when inventory has zero quantity"""
#         # Arrange
#         base_inventory.quantity = 0
#         requested_quantity = 10
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == False
#         assert result.remaining_stock == 0
#         assert any("out of stock" in warning.lower() for warning in result.warnings)
#         assert result.status == StockStatusContract.OUT_OF_STOCK
    
#     def test_validate_expired_product(self, base_inventory):
#         """Test validation when product is expired"""
#         # Arrange
#         base_inventory.expiry_date = date.today() - timedelta(days=1)
#         requested_quantity = 10
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == False
#         assert any("expired" in warning.lower() for warning in result.warnings)
#         assert result.status == StockStatusContract.EXPIRED
#         assert result.days_until_expiry < 0
    
#     def test_validate_expiring_soon(self, base_inventory):
#         """Test validation when product is expiring soon (within 90 days)"""
#         # Arrange
#         base_inventory.expiry_date = date.today() + timedelta(days=30)
#         requested_quantity = 10
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == True
#         assert any("expiring soon" in warning.lower() for warning in result.warnings)
#         assert result.status == StockStatusContract.EXPIRING_SOON
#         assert 0 < result.days_until_expiry <= 90
    
#     def test_validate_inactive_product(self, base_inventory):
#         """Test validation when product is inactive"""
#         # Arrange
#         base_inventory.status = ProductStatus.INACTIVE
#         requested_quantity = 10
        
#         # Act
#         result = base_inventory.validate_stock_request(requested_quantity)
        
#         # Assert
#         assert result.is_available == False
#         assert any("not active" in warning.lower() for warning in result.warnings)
#         assert result.status == StockStatusContract.INACTIVE

# # Tests for StockCheckUseCase
# class TestStockCheckUseCase:
#     """Test the stock check use case"""
    
#     def test_execute_with_available_product(self, product_id, mock_uow):
#         """Test the stock check use case with available product"""
#         # Arrange
#         use_case = StockCheckUseCase(mock_uow)
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=product_id,
#                     quantity=30
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == True
#         assert len(response.data) == 1
#         assert response.data[0].stock_validation_result.is_available == True
#         assert response.data[0].stock_validation_result.status == StockStatusContract.AVAILABLE
#         assert response.summary.available_items == 1
#         assert response.summary.unavailable_items == 0
    
#     def test_execute_with_insufficient_stock(self, product_id, mock_uow):
#         """Test the stock check use case with insufficient stock"""
#         # Arrange
#         use_case = StockCheckUseCase(mock_uow)
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=product_id,
#                     quantity=150  # More than available (100)
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == True
#         assert len(response.data) == 1
#         assert response.data[0].stock_validation_result.is_available == False
#         assert response.data[0].stock_validation_result.status == StockStatusContract.INSUFFICIENT_STOCK
#         assert response.summary.available_items == 0
#         assert response.summary.unavailable_items == 1
    
#     def test_execute_with_nonexistent_product(self, mock_uow):
#         """Test the stock check use case with nonexistent product"""
#         # Arrange
#         use_case = StockCheckUseCase(mock_uow)
#         nonexistent_id = uuid4()
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=nonexistent_id,
#                     quantity=10
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == False
#         assert len(response.errors) == 1
#         assert "Product not found" in response.errors[0].message
    
#     def test_execute_with_multiple_items(self, product_id, mock_uow, base_inventory):
#         """Test the stock check use case with multiple items"""
#         # Arrange
#         # Create a second product and inventory
#         second_product_id = uuid4()
#         second_product = ProductEntity(
#             id=second_product_id,
#             name="Second Product",
#             description="Second product description",
#             status=ProductStatus.ACTIVE
#         )
        
#         second_inventory = InventoryEntity(
#             id=uuid4(),
#             product_id=second_product_id,
#             quantity=5,
#             price=20.0,
#             max_stock=100,
#             min_stock=10,
#             expiry_date=date.today() + timedelta(days=180)
#         )
        
#         # Add them to the mock UoW
#         mock_uow.products[second_product_id] = second_product
#         mock_uow.inventory_items[second_product_id] = second_inventory
        
#         use_case = StockCheckUseCase(mock_uow)
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=product_id,
#                     quantity=30  # Available
#                 ),
#                 StockCheckItemContract(
#                     product_id=second_product_id,
#                     quantity=10  # Insufficient
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == True
#         assert len(response.data) == 2
#         assert response.data[0].stock_validation_result.is_available == True
#         assert response.data[1].stock_validation_result.is_available == False
#         assert response.data[1].stock_validation_result.status == StockStatusContract.INSUFFICIENT_STOCK
#         assert response.summary.available_items == 1
#         assert response.summary.unavailable_items == 1

#     def test_low_stock_and_expiring_separately(self, product_id, mock_uow):
#         """Test that low stock and expiring soon are handled as separate statuses"""
#         # Arrange - Create two separate products
        
#         # Low stock product
#         low_stock_id = uuid4()
#         low_stock_product = ProductEntity(
#             id=low_stock_id,
#             name="Low Stock Product",
#             description="Low stock product description",
#             status=ProductStatus.ACTIVE
#         )
        
#         low_stock_inventory = InventoryEntity(
#             id=uuid4(),
#             product_id=low_stock_id,
#             quantity=25,
#             price=10.0,
#             max_stock=100,
#             min_stock=20,
#             expiry_date=date.today() + timedelta(days=180)  # Not expiring soon
#         )
        
#         # Expiring soon product
#         expiring_id = uuid4()
#         expiring_product = ProductEntity(
#             id=expiring_id,
#             name="Expiring Product",
#             description="Expiring product description",
#             status=ProductStatus.ACTIVE
#         )
        
#         expiring_inventory = InventoryEntity(
#             id=uuid4(),
#             product_id=expiring_id,
#             quantity=100,  # Plenty of stock
#             price=15.0,
#             max_stock=200,
#             min_stock=20,
#             expiry_date=date.today() + timedelta(days=30)  # Expiring soon
#         )
        
#         # Add them to the mock UoW
#         test_uow = MockUnitOfWork(
#             products={
#                 low_stock_id: low_stock_product,
#                 expiring_id: expiring_product
#             },
#             inventory_items={
#                 low_stock_id: low_stock_inventory,
#                 expiring_id: expiring_inventory
#             }
#         )
        
#         use_case = StockCheckUseCase(test_uow)
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=low_stock_id,
#                     quantity=10  # Will trigger low stock
#                 ),
#                 StockCheckItemContract(
#                     product_id=expiring_id,
#                     quantity=10  # Will trigger expiring soon
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == True
#         assert len(response.data) == 2
        
#         # First item should be LOW_STOCK
#         assert response.data[0].stock_validation_result.is_available == True
#         assert response.data[0].stock_validation_result.status == StockStatusContract.LOW_STOCK
        
#         # Second item should be EXPIRING_SOON
#         assert response.data[1].stock_validation_result.is_available == True
#         assert response.data[1].stock_validation_result.status == StockStatusContract.EXPIRING_SOON

#     def test_product_both_low_stock_and_expiring_soon(self, product_id, mock_uow):
#         """Test a product that is both low on stock and expiring soon"""
#         # Arrange
#         # Create a product that has both conditions
#         test_id = uuid4()
#         test_product = ProductEntity(
#             id=test_id,
#             name="Low Stock and Expiring Product",
#             description="Product with both low stock and expiring soon conditions",
#             status=ProductStatus.ACTIVE
#         )
        
#         test_inventory = InventoryEntity(
#             id=uuid4(),
#             product_id=test_id,
#             quantity=25,  # Current quantity
#             price=10.0,
#             max_stock=100,
#             min_stock=20,  # Taking 10 will put it below this
#             expiry_date=date.today() + timedelta(days=30)  # Expiring soon (within 90 days)
#         )
        
#         # Add to a test UoW
#         test_uow = MockUnitOfWork(
#             products={test_id: test_product},
#             inventory_items={test_id: test_inventory}
#         )
        
#         # First test direct validation
#         result = test_inventory.validate_stock_request(10)
        
#         # Should prioritize one status (in the existing code, LOW_STOCK takes precedence)
#         assert result.is_available == True
#         # Check that the warnings contain both conditions
#         assert any("minimum level" in warning.lower() for warning in result.warnings)
#         assert any("expiring soon" in warning.lower() for warning in result.warnings)
        
#         # One status should be returned, not a combined status
#         # As per the current implementation, one status takes precedence 
#         assert result.status in [StockStatusContract.LOW_STOCK, StockStatusContract.EXPIRING_SOON]
        
#         # Now test through the use case
#         use_case = StockCheckUseCase(test_uow)
#         request = StockCheckRequestContract(
#             items=[
#                 StockCheckItemContract(
#                     product_id=test_id,
#                     quantity=10
#                 )
#             ]
#         )
        
#         # Act
#         response = use_case.execute(request)
        
#         # Assert
#         assert response.success == True
#         assert len(response.data) == 1
#         result_item = response.data[0]
        
#         # The validation result should be the same as above
#         assert result_item.stock_validation_result.is_available == True
        
#         # Should contain both warnings
#         assert any("minimum level" in warning.lower() for warning in result_item.stock_validation_result.warnings)
#         assert any("expiring soon" in warning.lower() for warning in result_item.stock_validation_result.warnings)
        
#         # Should have a single status, not a combined one
#         assert result_item.stock_validation_result.status in [
#             StockStatusContract.LOW_STOCK, 
#             StockStatusContract.EXPIRING_SOON
#         ]