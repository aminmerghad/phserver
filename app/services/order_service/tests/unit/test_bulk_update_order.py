import pytest
import uuid
from unittest.mock import Mock, patch
from app.services.order_service.application.commands.bulk_update_order_command import (
    BulkUpdateOrderCommand,
    BulkUpdateOrderItemCommand
)
from app.services.order_service.application.dtos.bulk_update_dto import (
    BulkUpdateOrderResponse,
    BulkUpdateOrderItemResult
)
from app.services.order_service.application.use_cases.bulk_update_order import BulkUpdateOrderUseCase
from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.entities.order_item import OrderItem
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.domain.value_objects.money import Money
from app.services.order_service.domain.exceptions.order_errors import (
    OrderNotFoundError,
    InvalidOrderStatusTransition,
    OrderValidationError
)
from decimal import Decimal

class TestBulkUpdateOrderCommand:
    def test_create_bulk_update_command_success(self):
        # Arrange
        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        
        updates = [
            BulkUpdateOrderItemCommand(
                order_id=order_id1,
                status=OrderStatus.CONFIRMED
            ),
            BulkUpdateOrderItemCommand(
                order_id=order_id2,
                status=OrderStatus.COMPLETED,
                notes="Completed successfully"
            )
        ]
        
        # Act
        command = BulkUpdateOrderCommand(updates=updates)
        
        # Assert
        assert len(command.updates) == 2
        assert command.updates[0].order_id == order_id1
        assert command.updates[0].status == OrderStatus.CONFIRMED
        assert command.updates[1].order_id == order_id2
        assert command.updates[1].status == OrderStatus.COMPLETED
        assert command.updates[1].notes == "Completed successfully"
    
    def test_create_bulk_update_command_empty_updates_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="At least one order update is required"):
            BulkUpdateOrderCommand(updates=[])
    
    def test_create_bulk_update_command_too_many_updates_raises_error(self):
        # Arrange - Create 101 updates (over the limit)
        updates = [
            BulkUpdateOrderItemCommand(
                order_id=uuid.uuid4(),
                status=OrderStatus.CONFIRMED
            ) for _ in range(101)
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Maximum 100 orders can be updated"):
            BulkUpdateOrderCommand(updates=updates)

class TestBulkUpdateOrderUseCase:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.order_repository = Mock()
        return uow
    
    @pytest.fixture
    def mock_query_service(self):
        return Mock()
    
    @pytest.fixture
    def mock_update_use_case(self):
        return Mock()
    
    @pytest.fixture
    def bulk_update_use_case(self, mock_uow, mock_query_service):
        return BulkUpdateOrderUseCase(mock_uow, mock_query_service)
    
    def test_bulk_update_all_successful(self, bulk_update_use_case, mock_uow, monkeypatch):
        # Arrange
        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        
        # Mock orders
        order1 = self._create_mock_order(order_id1, OrderStatus.PENDING)
        order2 = self._create_mock_order(order_id2, OrderStatus.PENDING)
        
        mock_uow.order_repository.get.side_effect = [order1, order2]
        
        # Mock successful update results
        mock_update_result1 = Mock()
        mock_update_result1.new_status = OrderStatus.CONFIRMED
        mock_update_result2 = Mock()
        mock_update_result2.new_status = OrderStatus.COMPLETED
        
        mock_update_use_case = Mock()
        mock_update_use_case.execute.side_effect = [mock_update_result1, mock_update_result2]
        
        monkeypatch.setattr(bulk_update_use_case, '_update_order_use_case', mock_update_use_case)
        
        updates = [
            BulkUpdateOrderItemCommand(order_id=order_id1, status=OrderStatus.CONFIRMED),
            BulkUpdateOrderItemCommand(order_id=order_id2, status=OrderStatus.COMPLETED)
        ]
        command = BulkUpdateOrderCommand(updates=updates)
        
        # Act
        result = bulk_update_use_case.execute(command)
        
        # Assert
        assert result.total_attempted == 2
        assert result.total_successful == 2
        assert result.total_failed == 0
        assert result.success_rate == 100.0
        assert len(result.results) == 2
        assert all(r.success for r in result.results)
    
    def test_bulk_update_partial_success(self, bulk_update_use_case, mock_uow, monkeypatch):
        # Arrange
        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        order_id3 = uuid.uuid4()
        
        # Mock orders - one doesn't exist
        order1 = self._create_mock_order(order_id1, OrderStatus.PENDING)
        order3 = self._create_mock_order(order_id3, OrderStatus.PENDING)
        
        mock_uow.order_repository.get.side_effect = [order1, None, order3]
        
        # Mock update results
        mock_update_result1 = Mock()
        mock_update_result1.new_status = OrderStatus.CONFIRMED
        mock_update_result3 = Mock()
        mock_update_result3.new_status = OrderStatus.COMPLETED
        
        mock_update_use_case = Mock()
        mock_update_use_case.execute.side_effect = [mock_update_result1, mock_update_result3]
        
        monkeypatch.setattr(bulk_update_use_case, '_update_order_use_case', mock_update_use_case)
        
        updates = [
            BulkUpdateOrderItemCommand(order_id=order_id1, status=OrderStatus.CONFIRMED),
            BulkUpdateOrderItemCommand(order_id=order_id2, status=OrderStatus.CONFIRMED),
            BulkUpdateOrderItemCommand(order_id=order_id3, status=OrderStatus.COMPLETED)
        ]
        command = BulkUpdateOrderCommand(updates=updates)
        
        # Act
        result = bulk_update_use_case.execute(command)
        
        # Assert
        assert result.total_attempted == 3
        assert result.total_successful == 2
        assert result.total_failed == 1
        assert result.success_rate == pytest.approx(66.67, rel=1e-2)
        assert len(result.results) == 3
        
        # Check specific results
        assert result.results[0].success is True
        assert result.results[1].success is False
        assert result.results[1].error_code == "ORDER_NOT_FOUND"
        assert result.results[2].success is True
    
    def test_bulk_update_all_failed(self, bulk_update_use_case, mock_uow):
        # Arrange - No orders exist
        mock_uow.order_repository.get.return_value = None
        
        order_id1 = uuid.uuid4()
        order_id2 = uuid.uuid4()
        
        updates = [
            BulkUpdateOrderItemCommand(order_id=order_id1, status=OrderStatus.CONFIRMED),
            BulkUpdateOrderItemCommand(order_id=order_id2, status=OrderStatus.COMPLETED)
        ]
        command = BulkUpdateOrderCommand(updates=updates)
        
        # Act
        result = bulk_update_use_case.execute(command)
        
        # Assert
        assert result.total_attempted == 2
        assert result.total_successful == 0
        assert result.total_failed == 2
        assert result.success_rate == 0.0
        assert all(not r.success for r in result.results)
        assert all(r.error_code == "ORDER_NOT_FOUND" for r in result.results)
    
    def test_bulk_update_invalid_status_transition(self, bulk_update_use_case, mock_uow, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        order = self._create_mock_order(order_id, OrderStatus.COMPLETED)  # Already completed
        
        mock_uow.order_repository.get.return_value = order
        
        # Mock update use case to raise InvalidOrderStatusTransition
        mock_update_use_case = Mock()
        mock_update_use_case.execute.side_effect = InvalidOrderStatusTransition(
            message="Cannot transition from COMPLETED to PENDING"
        )
        
        monkeypatch.setattr(bulk_update_use_case, '_update_order_use_case', mock_update_use_case)
        
        updates = [
            BulkUpdateOrderItemCommand(order_id=order_id, status=OrderStatus.PENDING)
        ]
        command = BulkUpdateOrderCommand(updates=updates)
        
        # Act
        result = bulk_update_use_case.execute(command)
        
        # Assert
        assert result.total_attempted == 1
        assert result.total_successful == 0
        assert result.total_failed == 1
        assert result.results[0].success is False
        assert result.results[0].error_code == "INVALID_STATUS_TRANSITION"
    
    def _create_mock_order(self, order_id: uuid.UUID, status: OrderStatus) -> OrderEntity:
        """Helper method to create a mock order entity"""
        order_item = OrderItem(
            product_id=uuid.uuid4(),
            quantity=1,
            price=Money(Decimal("10.99"))
        )
        
        return OrderEntity(
            id=order_id,
            user_id=uuid.uuid4(),
            items=[order_item],
            status=status,
            total_amount=Decimal("10.99")
        )

class TestBulkUpdateOrderResponse:
    def test_success_rate_calculation(self):
        # Arrange
        results = [
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=True),
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=True),
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=False),
        ]
        
        response = BulkUpdateOrderResponse(
            total_attempted=3,
            total_successful=2,
            total_failed=1,
            results=results
        )
        
        # Act & Assert
        assert response.success_rate == pytest.approx(66.67, rel=1e-2)
    
    def test_get_successful_orders(self):
        # Arrange
        successful_id1 = uuid.uuid4()
        successful_id2 = uuid.uuid4()
        failed_id = uuid.uuid4()
        
        results = [
            BulkUpdateOrderItemResult(order_id=successful_id1, success=True),
            BulkUpdateOrderItemResult(order_id=failed_id, success=False),
            BulkUpdateOrderItemResult(order_id=successful_id2, success=True),
        ]
        
        response = BulkUpdateOrderResponse(
            total_attempted=3,
            total_successful=2,
            total_failed=1,
            results=results
        )
        
        # Act
        successful_orders = response.get_successful_orders()
        
        # Assert
        assert len(successful_orders) == 2
        assert successful_id1 in successful_orders
        assert successful_id2 in successful_orders
        assert failed_id not in successful_orders
    
    def test_get_errors_summary(self):
        # Arrange
        results = [
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=True),
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=False, error_code="ORDER_NOT_FOUND"),
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=False, error_code="INVALID_STATUS_TRANSITION"),
            BulkUpdateOrderItemResult(order_id=uuid.uuid4(), success=False, error_code="ORDER_NOT_FOUND"),
        ]
        
        response = BulkUpdateOrderResponse(
            total_attempted=4,
            total_successful=1,
            total_failed=3,
            results=results
        )
        
        # Act
        errors_summary = response.get_errors_summary()
        
        # Assert
        assert errors_summary["ORDER_NOT_FOUND"] == 2
        assert errors_summary["INVALID_STATUS_TRANSITION"] == 1 