# """
# Integration tests for the stock check functionality.

# These tests focus on the integration between the StockCheckUseCase and repositories.
# """
# import pytest
# from datetime import datetime, timedelta
# from uuid import uuid4

# from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckItemContract
# from app.shared.contracts.inventory.enums import StockStatusContract
# from app.services.inventory_service.service import InventoryService
# from app.services.inventory_service.domain.entities.product_entity import ProductEntity
# from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity

# class TestStockCheckIntegration:
#     """Integration tests for stock check functionality"""
    
#     def test_stock_check_with_repositories(self, app, inventory_service, database):
#         """Test stock check integration with repositories"""
#         with app.app_context():
#             # Arrange - Create test product and inventory directly in the database
#             product_id = uuid4()
            
#             # Create product
#             product = ProductEntity(
#                 id=product_id,
#                 name="Integration Test Product",
#                 description="A product for integration testing",
#                 category="Test Category",
#                 created_at=datetime.now(),
#                 updated_at=datetime.now()
#             )
            
#             # Create inventory
#             inventory = InventoryEntity(
#                 id=uuid4(),
#                 product_id=product_id,
#                 quantity=100,
#                 price=10.99,
#                 max_stock=200,
#                 min_stock=20,
#                 expiry_date=datetime.now() + timedelta(days=90),
#                 status="ACTIVE"
#             )
            
#             # Save to database
#             session = database.get_session()
#             session.add(product)
#             session.add(inventory)
#             session.commit()
            
#             # Create stock check request
#             request = StockCheckRequestContract(
#                 items=[
#                     StockCheckItemContract(product_id=product_id, quantity=15)
#                 ]
#             )
            
#             # Act
#             response = inventory_service.stock_check(request)
            
#             # Assert
#             assert response.success is True
#             # assert len(response.data) == 1
#             # assert response.data[0].stock_validation_result.is_available is True
#             # assert response.data[0].stock_validation_result.status == StockStatusContract.AVAILABLE
#             # assert response.data[0].stock_validation_result.remaining_stock == 85  # 100 - 15
#             # assert response.data[0].product_name == "Integration Test Product"
    
#     # def test_stock_check_with_multiple_items(self, app, inventory_service, database):
#     #     """Test stock check with multiple items in the database"""
#     #     with app.app_context():
#     #         # Arrange - Create multiple products with inventory
#     #         products = []
#     #         inventories = []
#     #         product_ids = []
            
#     #         for i in range(5):
#     #             product_id = uuid4()
#     #             product_ids.append(product_id)
                
#     #             product = ProductEntity(
#     #                 id=product_id,
#     #                 name=f"Integration Product {i}",
#     #                 description=f"Description for product {i}",
#     #                 category="Integration Tests",
#     #                 status=ProductStatusContract.ACTIVE,
#     #                 created_at=datetime.now(),
#     #                 updated_at=datetime.now()
#     #             )
#     #             products.append(product)
                
#     #             inventory = InventoryEntity(
#     #                 id=uuid4(),
#     #                 product_id=product_id,
#     #                 quantity=50 + i * 10,  # Different quantities
#     #                 price=9.99 + i,
#     #                 max_stock=100,
#     #                 min_stock=20,
#     #                 expiry_date=datetime.now() + timedelta(days=60 + i * 10),
#     #                 status="ACTIVE"
#     #             )
#     #             inventories.append(inventory)
            
#     #         # Save to database
#     #         session = database.get_session()
#     #         for product in products:
#     #             session.add(product)
#     #         for inventory in inventories:
#     #             session.add(inventory)
#     #         session.commit()
            
#     #         # Create stock check request with multiple items
#     #         request_items = [
#     #             StockCheckItemContract(product_id=product_id, quantity=10)
#     #             for product_id in product_ids[:3]  # Use first 3 products
#     #         ]
#     #         request = StockCheckRequestContract(items=request_items)
            
#     #         # Act
#     #         response = inventory_service.stock_check(request)
            
#     #         # Assert
#     #         assert response.success is True
#     #         assert len(response.data) == 3
#     #         assert response.summary.total_items == 3
#     #         assert response.summary.available_items == 3
#     #         assert response.summary.unavailable_items == 0
            
#     #         # Check each item
#     #         for i, item in enumerate(response.data):
#     #             assert item.stock_validation_result.is_available is True
#     #             assert item.stock_validation_result.status == StockStatusContract.AVAILABLE
#     #             assert item.product_name == f"Integration Product {i}"
#     #             assert item.stock_validation_result.remaining_stock == (50 + i * 10) - 10  # Initial quantity - 10
    
#     # def test_stock_check_expiring_product(self, app, inventory_service, database):
#     #     """Test stock check with a product that is expiring soon"""
#     #     with app.app_context():
#     #         # Arrange - Create product that's expiring soon
#     #         product_id = uuid4()
            
#     #         product = ProductEntity(
#     #             id=product_id,
#     #             name="Expiring Integration Product",
#     #             description="A product that's expiring soon",
#     #             category="Integration Tests",
#     #             status=ProductStatusContract.ACTIVE,
#     #             created_at=datetime.now(),
#     #             updated_at=datetime.now()
#     #         )
            
#     #         # Create inventory with expiry date very soon
#     #         inventory = InventoryEntity(
#     #             id=uuid4(),
#     #             product_id=product_id,
#     #             quantity=75,
#     #             price=15.99,
#     #             max_stock=100,
#     #             min_stock=20,
#     #             expiry_date=datetime.now() + timedelta(days=15),  # Expiring in 15 days
#     #             status="ACTIVE"
#     #         )
            
#     #         # Save to database
#     #         session = database.get_session()
#     #         session.add(product)
#     #         session.add(inventory)
#     #         session.commit()
            
#     #         # Create stock check request
#     #         request = StockCheckRequestContract(
#     #             items=[
#     #                 StockCheckItemContract(product_id=product_id, quantity=20)
#     #             ]
#     #         )
            
#     #         # Act
#     #         response = inventory_service.stock_check(request)
            
#     #         # Assert
#     #         assert response.success is True
#     #         assert len(response.data) == 1
#     #         assert response.data[0].stock_validation_result.is_available is True
#     #         assert response.data[0].stock_validation_result.status == StockStatusContract.EXPIRING_SOON
#     #         assert response.data[0].stock_validation_result.days_until_expiry == 15
#     #         assert any("expir" in warning.lower() for warning in 
#     #                   response.data[0].stock_validation_result.warnings)
    
#     # def test_stock_check_nonexistent_product(self, app, inventory_service):
#     #     """Test stock check with a product that doesn't exist in the database"""
#     #     with app.app_context():
#     #         # Arrange - Use a random UUID that doesn't exist
#     #         nonexistent_id = uuid4()
            
#     #         request = StockCheckRequestContract(
#     #             items=[
#     #                 StockCheckItemContract(product_id=nonexistent_id, quantity=5)
#     #             ]
#     #         )
            
#     #         # Act
#     #         response = inventory_service.stock_check(request)
            
#     #         # Assert
#     #         assert response.success is False
#     #         assert response.errors is not None
#     #         assert len(response.errors) == 1
#     #         error_message = response.errors[0].message.lower()
#     #         assert "product" in error_message and "not found" in error_message 