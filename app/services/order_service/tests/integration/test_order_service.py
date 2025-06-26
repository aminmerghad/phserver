import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

from app.dataBase import Database
from app.services.order_service.service import OrderService
from app.services.order_service.application.commands.create_order_command import CreateOrderCommand
from app.services.order_service.application.commands.update_order_command import UpdateOrderCommand
from app.services.order_service.application.commands.cancel_order_command import CancelOrderCommand
from app.services.order_service.application.dtos.order_dto import CreateOrderItemDTO
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.domain.exceptions.order_errors import OrderNotFoundError, OrderValidationError
from app.shared.application.events.event_bus import EventBus
from app.shared.acl.unified_acl import UnifiedACL

@pytest.fixture
def db_session():
    """Mock database session for testing"""
    return Mock()

@pytest.fixture
def database(db_session):
    """Mock Database instance"""
    db = Mock(spec=Database)
    db.get_session.return_value = db_session
    return db

@pytest.fixture
def event_bus():
    """Mock EventBus instance"""
    return Mock(spec=EventBus)

@pytest.fixture
def acl():
    """Mock UnifiedACL instance"""
    return Mock(spec=UnifiedACL)

@pytest.fixture
def order_service(database, event_bus, acl):
    """Create OrderService with mocked dependencies"""
    return OrderService(database, event_bus, acl)

class TestOrderService:
    def test_create_order_success(self, order_service, monkeypatch):
        # Arrange
        user_id = uuid.uuid4()
        product_id1 = uuid.uuid4()
        product_id2 = uuid.uuid4()
        
        # Create command
        command = CreateOrderCommand(
            user_id=user_id,
            items=[
                CreateOrderItemDTO(product_id=product_id1, quantity=2, unit_price=Decimal("10.99")),
                CreateOrderItemDTO(product_id=product_id2, quantity=1, unit_price=Decimal("5.99"))
            ],
            notes="Test order"
        )
        
        # Mock create_order_use_case execution
        mock_result = Mock()
        mock_result.order_id = uuid.uuid4()
        mock_result.status = OrderStatus.PENDING
        mock_execute = Mock(return_value=mock_result)
        
        # Apply monkeypatch
        monkeypatch.setattr(order_service._create_order_use_case, 'execute', mock_execute)
        
        # Act
        result = order_service.create_order(command)
        
        # Assert
        assert result is mock_result
        mock_execute.assert_called_once_with(command)

    def test_create_order_validation_error(self, order_service, monkeypatch):
        # Arrange
        mock_execute = Mock(side_effect=OrderValidationError("Invalid order data"))
        monkeypatch.setattr(order_service._create_order_use_case, 'execute', mock_execute)
        
        command = CreateOrderCommand(
            items=[CreateOrderItemDTO(product_id=uuid.uuid4(), quantity=-1, unit_price=Decimal("10.99"))],
        )
        
        # Act & Assert
        with pytest.raises(OrderValidationError, match="Invalid order data"):
            order_service.create_order(command)
        
        # Verify rollback was called
        order_service._uow.rollback.assert_called_once()

    def test_get_order_by_id_found(self, order_service, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        mock_order = Mock()
        mock_order_dto = Mock()
        mock_order_dto.to_dict.return_value = {"id": str(order_id), "status": "PENDING"}
        
        # Mock dependencies
        monkeypatch.setattr(order_service._query_service, 'get_order_by_id', Mock(return_value=mock_order))
        monkeypatch.setattr(order_service._mapper, 'to_dto', Mock(return_value=mock_order_dto))
        
        # Act
        result = order_service.get_order(order_id)
        
        # Assert
        assert result == {"id": str(order_id), "status": "PENDING"}
        order_service._query_service.get_order_by_id.assert_called_once_with(order_id)
        order_service._mapper.to_dto.assert_called_once_with(mock_order)

    def test_get_order_by_id_not_found(self, order_service, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        
        # Mock dependencies
        monkeypatch.setattr(order_service._query_service, 'get_order_by_id', Mock(return_value=None))
        
        # Act
        result = order_service.get_order(order_id)
        
        # Assert
        assert result is None
        order_service._query_service.get_order_by_id.assert_called_once_with(order_id)

    def test_update_order_status_success(self, order_service, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        command = UpdateOrderCommand(
            id=order_id,
            status=OrderStatus.CONFIRMED
        )
        
        # Mock update_order_use_case execution
        mock_result = Mock()
        mock_result.to_dict.return_value = {
            "id": str(order_id),
            "status": OrderStatus.CONFIRMED.value
        }
        mock_execute = Mock(return_value=mock_result)
        
        # Apply monkeypatch
        monkeypatch.setattr(order_service._update_order_use_case, 'execute', mock_execute)
        
        # Act
        result = order_service.update_order_status(command)
        
        # Assert
        assert result == {"id": str(order_id), "status": OrderStatus.CONFIRMED.value}
        mock_execute.assert_called_once_with(command)

    def test_update_order_status_not_found(self, order_service, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        command = UpdateOrderCommand(
            id=order_id,
            status=OrderStatus.CONFIRMED
        )
        
        # Mock update_order_use_case execution to raise OrderNotFoundError
        mock_execute = Mock(side_effect=OrderNotFoundError(f"Order {order_id} not found"))
        
        # Apply monkeypatch
        monkeypatch.setattr(order_service._update_order_use_case, 'execute', mock_execute)
        
        # Act & Assert
        with pytest.raises(OrderNotFoundError, match=f"Order {order_id} not found"):
            order_service.update_order_status(command)
        
        # Verify rollback was called
        order_service._uow.rollback.assert_called_once()

    def test_cancel_order_success(self, order_service, monkeypatch):
        # Arrange
        order_id = uuid.uuid4()
        command = CancelOrderCommand(
            order_id=order_id,
            reason="Customer request"
        )
        
        # Mock cancel_order_use_case execution
        mock_result = Mock()
        mock_result.to_dict.return_value = {
            "id": str(order_id),
            "status": OrderStatus.CANCELLED.value
        }
        mock_execute = Mock(return_value=mock_result)
        
        # Apply monkeypatch
        monkeypatch.setattr(order_service._cancel_order_use_case, 'execute', mock_execute)
        
        # Act
        result = order_service.cancel_order(command)
        
        # Assert
        assert result == {"id": str(order_id), "status": OrderStatus.CANCELLED.value}
        mock_execute.assert_called_once_with(command)

    def test_get_user_orders(self, order_service, monkeypatch):
        # Arrange
        user_id = uuid.uuid4()
        mock_orders = [Mock(), Mock()]
        mock_dto1 = Mock()
        mock_dto1.to_dict.return_value = {"id": str(uuid.uuid4()), "status": "PENDING"}
        mock_dto2 = Mock()
        mock_dto2.to_dict.return_value = {"id": str(uuid.uuid4()), "status": "COMPLETED"}
        
        # Mock dependencies
        monkeypatch.setattr(order_service._query_service, 'get_orders_by_user_id', Mock(return_value=mock_orders))
        monkeypatch.setattr(order_service._mapper, 'to_dto', Mock(side_effect=[mock_dto1, mock_dto2]))
        
        # Act
        result = order_service.get_user_orders(user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0] == {"id": mock_dto1.to_dict()["id"], "status": "PENDING"}
        assert result[1] == {"id": mock_dto2.to_dict()["id"], "status": "COMPLETED"}
        order_service._query_service.get_orders_by_user_id.assert_called_once_with(user_id)
        assert order_service._mapper.to_dto.call_count == 2 