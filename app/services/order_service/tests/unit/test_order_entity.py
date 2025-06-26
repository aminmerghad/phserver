import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.entities.order_item import OrderItem
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.domain.exceptions.order_errors import OrderValidationError, InvalidOrderStatusTransition

class TestOrderEntity:
    def test_create_order_entity_success(self):
        # Arrange
        order_id = uuid.uuid4()
        user_id = uuid.uuid4()
        product_id = uuid.uuid4()
        
        # Create valid order item
        order_item = OrderItem(
            product_id=product_id,
            quantity=2,
            price=Decimal("10.99")
        )
        
        # Act
        order = OrderEntity(
            id=order_id,
            user_id=user_id,
            items=[order_item],
            status=OrderStatus.PENDING,
            notes="Test order",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Assert
        assert order.id == order_id
        assert order.user_id == user_id
        assert len(order.items) == 1
        assert order.items[0].product_id == product_id
        assert order.status == OrderStatus.PENDING
        assert order.notes == "Test order"
    
    def test_create_order_with_empty_items_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(OrderValidationError, match="Order must have at least one item"):
            OrderEntity(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                items=[],
                status=OrderStatus.PENDING
            )
    
    def test_create_order_with_invalid_item_quantity_raises_error(self):
        # Arrange
        invalid_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=0,  # Invalid quantity
            price=Decimal("10.99")
        )
        
        # Act & Assert
        with pytest.raises(OrderValidationError, match="Item quantity must be greater than 0"):
            OrderEntity(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                items=[invalid_item],
                status=OrderStatus.PENDING
            )
    
    def test_calculate_total(self):
        # Arrange
        item1 = OrderItem(
            product_id=uuid.uuid4(),
            quantity=2,
            price=Decimal("10.99")
        )
        
        item2 = OrderItem(
            product_id=uuid.uuid4(),
            quantity=1,
            price=Decimal("5.99")
        )
        
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[item1, item2],
            status=OrderStatus.PENDING
        )
        
        # Act
        total = order.calculate_total()
        
        # Assert
        expected_total = (Decimal("10.99") * 2) + (Decimal("5.99") * 1)
        assert total.amount == expected_total
    
    def test_add_item_to_pending_order(self):
        # Arrange
        existing_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=2,
            price=Decimal("10.99")
        )
        
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[existing_item],
            status=OrderStatus.PENDING
        )
        
        new_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=1,
            price=Decimal("5.99")
        )
        
        # Act
        order.add_item(new_item)
        
        # Assert
        assert len(order.items) == 2
        assert order.items[1] == new_item
    
    def test_add_existing_item_increments_quantity(self):
        # Arrange
        product_id = uuid.uuid4()
        existing_item = OrderItem(
            product_id=product_id,
            quantity=2,
            price=Decimal("10.99")
        )
        
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[existing_item],
            status=OrderStatus.PENDING
        )
        
        additional_item = OrderItem(
            product_id=product_id,  # Same product ID
            quantity=3,
            price=Decimal("10.99")
        )
        
        # Act
        order.add_item(additional_item)
        
        # Assert
        assert len(order.items) == 1  # Still only one item
        assert order.items[0].quantity == 5  # 2 + 3
    
    def test_add_item_to_non_pending_order_raises_error(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.CONFIRMED  # Not pending
        )
        
        new_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=1,
            price=Decimal("5.99")
        )
        
        # Act & Assert
        with pytest.raises(OrderValidationError, match="Can only add items to pending orders"):
            order.add_item(new_item)
    
    def test_remove_item_from_pending_order(self):
        # Arrange
        product_id = uuid.uuid4()
        item_to_remove = OrderItem(
            product_id=product_id,
            quantity=2,
            price=Decimal("10.99")
        )
        
        other_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=1,
            price=Decimal("5.99")
        )
        
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[item_to_remove, other_item],
            status=OrderStatus.PENDING
        )
        
        # Act
        order.remove_item(product_id)
        
        # Assert
        assert len(order.items) == 1
        assert order.items[0] == other_item
    
    def test_remove_nonexistent_item_raises_error(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.PENDING
        )
        
        nonexistent_product_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(OrderValidationError, match=f"Product {nonexistent_product_id} not found in order"):
            order.remove_item(nonexistent_product_id)
    
    def test_valid_status_transitions(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.PENDING
        )
        
        # Act & Assert - PENDING to CONFIRMED
        order.update_status(OrderStatus.CONFIRMED)
        assert order.status == OrderStatus.CONFIRMED
        
        # Act & Assert - CONFIRMED to COMPLETED
        order.update_status(OrderStatus.COMPLETED)
        assert order.status == OrderStatus.COMPLETED
        assert order.completed_at is not None
    
    def test_invalid_status_transition_raises_error(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.PENDING
        )
        
        # Act & Assert - Cannot go from PENDING to COMPLETED
        with pytest.raises(InvalidOrderStatusTransition):
            order.update_status(OrderStatus.COMPLETED)
        
        # Update to CANCELLED
        order.update_status(OrderStatus.CANCELLED)
        
        # Act & Assert - Cannot transition from CANCELLED
        with pytest.raises(InvalidOrderStatusTransition):
            order.update_status(OrderStatus.CONFIRMED)
    
    def test_cancel_pending_order(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.PENDING
        )
        
        # Act
        order.cancel()
        
        # Assert
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_confirmed_order(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.CONFIRMED
        )
        
        # Act
        order.cancel()
        
        # Assert
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_completed_order_raises_error(self):
        # Arrange
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[OrderItem(
                product_id=uuid.uuid4(),
                quantity=1,
                price=Decimal("10.99")
            )],
            status=OrderStatus.COMPLETED
        )
        
        # Act & Assert
        with pytest.raises(OrderValidationError, match="Order cannot be cancelled in its current state"):
            order.cancel()
    
    def test_update_quantities(self):
        # Arrange
        product1_id = uuid.uuid4()
        product2_id = uuid.uuid4()
        
        item1 = OrderItem(
            product_id=product1_id,
            quantity=2,
            price=Decimal("10.99")
        )
        
        item2 = OrderItem(
            product_id=product2_id,
            quantity=1,
            price=Decimal("5.99")
        )
        
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            items=[item1, item2],
            status=OrderStatus.PENDING
        )
        
        # Act
        order.update_quantities({
            product1_id: 3,  # Increase
            product2_id: 0   # Remove (zero quantity)
        })
        
        # Assert
        assert len(order.items) == 1
        assert order.items[0].product_id == product1_id
        assert order.items[0].quantity == 3 