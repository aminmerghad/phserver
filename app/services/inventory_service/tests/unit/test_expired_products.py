# import pytest
# from datetime import date, datetime, timedelta
# from uuid import uuid4
# from unittest.mock import patch, MagicMock

# from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
# from app.services.inventory_service.domain.entities.product_entity import ProductEntity
# from app.services.inventory_service.domain.enums.product_status import ProductStatus
# from app.services.inventory_service.application.use_cases.stock_check import StockCheckUseCase
# from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckItemContract
# from app.shared.contracts.inventory.enums import StockStatusContract


# class TestExpiredProductHandling:
#     """Tests for handling expired products in the inventory system"""
    
#     def test_already_expired_product(self):
#         """Test stock check for a product that is already expired"""
#         # Arrange
#         product_id = uuid4()
#         product = ProductEntity(
#             id=product_id,
#             name="Expired Medicine",
#             description="A medicine that is already expired"
#         )
        
#         # Create inventory with expired date (1 day ago)
#         inventory = InventoryEntity(
#             id=uuid4(),
#             product_id=product_id,
#             quantity=50,
#             price=15.0,
#             max_stock=100,
#             min_stock=10,
#             expiry_date=date.today() - timedelta(days=1),
#             status=ProductStatus.ACTIVE
#         )
        
#         # Act
#         result = inventory.validate_stock_request(10)
        
#         # Assert
#         assert result.is_available == False
#         assert StockStatusContract.EXPIRED in result.status
#         assert result.days_until_expiry == -1  # Negative days means already expired
#         assert any("expired" in warning.lower() for warning in result.warnings)
    
# #     def test_expired_today_product(self):
# #         """Test stock check for a product that expires today"""
# #         # Arrange
# #         product_id = uuid4()
# #         product = ProductEntity(
# #             id=product_id,
# #             name="Today Expiring Medicine",
# #             description="A medicine that expires today",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         # Create inventory with today's expiry date
# #         inventory = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_id,
# #             quantity=50,
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today()
# #         )
        
# #         # Act
# #         result = inventory.validate_stock_request(10)
        
# #         # Assert
# #         assert result.is_available == False
# #         assert result.status == StockStatusContract.EXPIRED
# #         assert result.days_until_expiry == 0
# #         assert any("expired" in warning.lower() for warning in result.warnings)
    
# #     def test_expiring_soon_thresholds(self):
# #         """Test different thresholds for 'expiring soon' status"""
# #         test_cases = [
# #             (1, "tomorrow"),
# #             (7, "in one week"),
# #             (15, "in two weeks"),
# #             (29, "in 29 days"),
# #             (30, "in 30 days - threshold boundary"),
# #         ]
        
# #         for days, description in test_cases:
# #             # Arrange
# #             product_id = uuid4()
# #             product = ProductEntity(
# #                 id=product_id,
# #                 name=f"Medicine Expiring {description}",
# #                 description=f"Test medicine expiring {description}",
# #                 status=ProductStatus.ACTIVE
# #             )
            
# #             inventory = InventoryEntity(
# #                 id=uuid4(),
# #                 product_id=product_id,
# #                 quantity=50,
# #                 price=15.0,
# #                 max_stock=100,
# #                 min_stock=10,
# #                 expiry_date=date.today() + timedelta(days=days)
# #             )
            
# #             # Act
# #             result = inventory.validate_stock_request(10)
            
# #             # Assert
# #             assert result.is_available == True, f"Failed for {description}"
# #             assert result.status == StockStatusContract.EXPIRING_SOON, f"Failed for {description}"
# #             assert result.days_until_expiry == days, f"Failed for {description}"
# #             assert any("expire" in warning.lower() for warning in result.warnings), f"Failed for {description}"
    
# #     def test_not_expiring_soon(self):
# #         """Test product that is not expiring soon (31+ days)"""
# #         # Arrange
# #         product_id = uuid4()
# #         product = ProductEntity(
# #             id=product_id,
# #             name="Fresh Medicine",
# #             description="Medicine with plenty of time before expiry",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         inventory = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_id,
# #             quantity=50,
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today() + timedelta(days=31)  # Just outside the threshold
# #         )
        
# #         # Act
# #         result = inventory.validate_stock_request(10)
        
# #         # Assert
# #         assert result.is_available == True
# #         assert result.status == StockStatusContract.AVAILABLE
# #         assert result.days_until_expiry == 31
# #         assert not any("expire" in warning.lower() for warning in result.warnings)
    
# #     def test_expired_product_priority(self):
# #         """Test that EXPIRED status takes priority over other statuses"""
# #         # Arrange - Product that is EXPIRED and has LOW_STOCK
# #         product_id = uuid4()
# #         product = ProductEntity(
# #             id=product_id,
# #             name="Expired Low Stock Medicine",
# #             description="Medicine that is expired and has low stock",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         inventory = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_id,
# #             quantity=15,  # Low stock (near min_stock)
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today() - timedelta(days=5)  # Expired 5 days ago
# #         )
        
# #         # Act
# #         result = inventory.validate_stock_request(5)
        
# #         # Assert - EXPIRED should take priority
# #         assert result.is_available == False
# #         assert result.status == StockStatusContract.EXPIRED
# #         # Both warnings should be present
# #         assert any("expired" in warning.lower() for warning in result.warnings)
# #         assert any("minimum" in warning.lower() for warning in result.warnings)
    
# #     def test_use_case_with_mixed_expiry_products(self):
# #         """Test stock check use case with a mix of expired and valid products"""
# #         # Arrange
# #         product_ids = [uuid4() for _ in range(3)]
        
# #         # Product 1: Available
# #         product1 = ProductEntity(
# #             id=product_ids[0],
# #             name="Valid Medicine",
# #             description="Medicine that is valid",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         inventory1 = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_ids[0],
# #             quantity=50,
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today() + timedelta(days=90)
# #         )
        
# #         # Product 2: Expired
# #         product2 = ProductEntity(
# #             id=product_ids[1],
# #             name="Expired Medicine",
# #             description="Medicine that is expired",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         inventory2 = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_ids[1],
# #             quantity=50,
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today() - timedelta(days=10)
# #         )
        
# #         # Product 3: Expiring Soon
# #         product3 = ProductEntity(
# #             id=product_ids[2],
# #             name="Expiring Soon Medicine",
# #             description="Medicine that is expiring soon",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         inventory3 = InventoryEntity(
# #             id=uuid4(),
# #             product_id=product_ids[2],
# #             quantity=50,
# #             price=15.0,
# #             max_stock=100,
# #             min_stock=10,
# #             expiry_date=date.today() + timedelta(days=15)
# #         )
        
# #         # Setup mock unit of work
# #         products = {
# #             product_ids[0]: product1,
# #             product_ids[1]: product2,
# #             product_ids[2]: product3
# #         }
        
# #         inventory_items = {
# #             product_ids[0]: inventory1,
# #             product_ids[1]: inventory2,
# #             product_ids[2]: inventory3
# #         }
        
# #         mock_uow = MockUnitOfWork(products, inventory_items)
# #         use_case = StockCheckUseCase(mock_uow)
        
# #         # Create request with all three products
# #         request = StockCheckRequestContract(
# #             items=[
# #                 StockCheckItemContract(product_id=product_ids[0], quantity=10),
# #                 StockCheckItemContract(product_id=product_ids[1], quantity=10),
# #                 StockCheckItemContract(product_id=product_ids[2], quantity=10)
# #             ]
# #         )
        
# #         # Act
# #         response = use_case.execute(request)
        
# #         # Assert
# #         assert response.success == True
# #         assert len(response.data) == 3
        
# #         # Check summary
# #         assert response.summary.total_items == 3
# #         assert response.summary.available_items == 2  # Product 1 and 3
# #         assert response.summary.unavailable_items == 1  # Product 2 (expired)
        
# #         # Check individual results
# #         results_by_product = {item.product_id: item for item in response.data}
        
# #         # Product 1: Available
# #         result1 = results_by_product[product_ids[0]]
# #         assert result1.is_available == True
# #         assert result1.status == StockStatusContract.AVAILABLE
        
# #         # Product 2: Expired
# #         result2 = results_by_product[product_ids[1]]
# #         assert result2.is_available == False
# #         assert result2.status == StockStatusContract.EXPIRED
        
# #         # Product 3: Expiring Soon
# #         result3 = results_by_product[product_ids[2]]
# #         assert result3.is_available == True
# #         assert result3.status == StockStatusContract.EXPIRING_SOON
    
# #     def test_batch_of_expired_products(self):
# #         """Test handling a batch check where all products are expired"""
# #         # Arrange
# #         products = {}
# #         inventory_items = {}
        
# #         # Create 5 expired products
# #         product_ids = [uuid4() for _ in range(5)]
        
# #         for i, product_id in enumerate(product_ids):
# #             product = ProductEntity(
# #                 id=product_id,
# #                 name=f"Expired Medicine {i+1}",
# #                 description=f"Medicine {i+1} that is expired",
# #                 status=ProductStatus.ACTIVE
# #             )
            
# #             # Each expired a different number of days ago
# #             inventory = InventoryEntity(
# #                 id=uuid4(),
# #                 product_id=product_id,
# #                 quantity=50,
# #                 price=15.0,
# #                 max_stock=100,
# #                 min_stock=10,
# #                 expiry_date=date.today() - timedelta(days=i+1)
# #             )
            
# #             products[product_id] = product
# #             inventory_items[product_id] = inventory
        
# #         mock_uow = MockUnitOfWork(products, inventory_items)
# #         use_case = StockCheckUseCase(mock_uow)
        
# #         # Create request with all expired products
# #         request = StockCheckRequestContract(
# #             items=[
# #                 StockCheckItemContract(product_id=pid, quantity=10)
# #                 for pid in product_ids
# #             ]
# #         )
        
# #         # Act
# #         response = use_case.execute(request)
        
# #         # Assert
# #         assert response.success == True
# #         assert len(response.data) == 5
        
# #         # All should be unavailable due to expiry
# #         assert response.summary.available_items == 0
# #         assert response.summary.unavailable_items == 5
        
# #         # Each product should be expired
# #         for item in response.data:
# #             assert item.is_available == False
# #             assert item.status == StockStatusContract.EXPIRED
# #             assert any("expired" in warning.lower() for warning in item.warnings)
    
# #     def test_different_expiry_formats(self):
# #         """Test handling different date formats for expiry dates"""
# #         # Arrange - using string date that needs parsing
# #         product_id = uuid4()
# #         product = ProductEntity(
# #             id=product_id,
# #             name="String Date Medicine",
# #             description="Medicine with date as string",
# #             status=ProductStatus.ACTIVE
# #         )
        
# #         with patch('app.services.inventory_service.domain.entities.inventory_entity.date') as mock_date:
# #             # Mock today's date
# #             mock_today = date(2023, 6, 15)
# #             mock_date.today.return_value = mock_today
            
# #             # Create inventory with yesterday's date
# #             inventory = InventoryEntity(
# #                 id=uuid4(),
# #                 product_id=product_id,
# #                 quantity=50,
# #                 price=15.0,
# #                 max_stock=100,
# #                 min_stock=10,
# #                 # Using date object directly rather than calculating from today
# #                 expiry_date=date(2023, 6, 14)  # One day before mock today
# #             )
            
# #             # Act
# #             result = inventory.validate_stock_request(10)
            
# #             # Assert
# #             assert result.is_available == False
# #             assert result.status == StockStatusContract.EXPIRED
# #             assert result.days_until_expiry == -1  # 1 day in the past 