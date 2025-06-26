import logging
from typing import List
from uuid import UUID

from app.services.order_service.application.commands.bulk_update_order_command import (
    BulkUpdateOrderCommand, 
    BulkUpdateOrderItemCommand
)
from app.services.order_service.application.commands.update_order_command import UpdateOrderCommand
from app.services.order_service.application.dtos.bulk_update_dto import (
    BulkUpdateOrderResponse,
    BulkUpdateOrderItemResult
)
from app.services.order_service.application.events.order_updated_event import OrderUpdatedEvent
from app.services.order_service.application.use_cases.update_order import UpdateOrderUseCase
from app.services.order_service.domain.exceptions.order_errors import (
    OrderNotFoundError,
    OrderValidationError,
    InvalidOrderStatusTransition
)
from app.services.order_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.order_service.infrastructure.query_services.order_query_service import OrderQueryService

logger = logging.getLogger(__name__)

class BulkUpdateOrderUseCase:
    """Use case for bulk updating multiple orders"""
    
    def __init__(self, uow: UnitOfWork, query_service: OrderQueryService):
        self._uow = uow
        self._query_service = query_service
        self._update_order_use_case = UpdateOrderUseCase(uow, query_service)
    
    def execute(self, command: BulkUpdateOrderCommand) -> BulkUpdateOrderResponse:
        """
        Execute bulk update operation.
        
        Uses individual order updates with partial success handling.
        Each order update is attempted independently, allowing some to succeed
        while others fail.
        """
        logger.info(f"Starting bulk update for {len(command.updates)} orders")
        
        results = []
        successful_count = 0
        failed_count = 0
        
        for update_item in command.updates:
            result = self._update_single_order(update_item)
            results.append(result)
            
            if result.success:
                successful_count += 1
            else:
                failed_count += 1
        
        response = BulkUpdateOrderResponse(
            total_attempted=len(command.updates),
            total_successful=successful_count,
            total_failed=failed_count,
            results=results
        )
        
        logger.info(
            f"Bulk update completed: {successful_count} successful, "
            f"{failed_count} failed out of {len(command.updates)} orders"
        )
        
        return response
    
    def _update_single_order(self, update_item: BulkUpdateOrderItemCommand) -> BulkUpdateOrderItemResult:
        """Update a single order and return the result"""
        try:
            logger.debug(f"Updating order {update_item.order_id}")
            
            # Get current order to track old status
            order = self._uow.order_repository.get(update_item.order_id)
            if not order:
                return BulkUpdateOrderItemResult(
                    order_id=update_item.order_id,
                    success=False,
                    error_message=f"Order {update_item.order_id} not found",
                    error_code="ORDER_NOT_FOUND"
                )
            
            old_status = order.status
            
            # Create update command
            update_command = UpdateOrderCommand(
                id=update_item.order_id,
                status=update_item.status,
                notes=update_item.notes
            )
            
            # Execute update using existing use case
            result = self._update_order_use_case.execute(update_command)
            
            return BulkUpdateOrderItemResult(
                order_id=update_item.order_id,
                success=True,
                old_status=old_status,
                new_status=result.new_status
            )
            
        except OrderNotFoundError:
            return BulkUpdateOrderItemResult(
                order_id=update_item.order_id,
                success=False,
                error_message=f"Order {update_item.order_id} not found",
                error_code="ORDER_NOT_FOUND"
            )
            
        except InvalidOrderStatusTransition as e:
            return BulkUpdateOrderItemResult(
                order_id=update_item.order_id,
                success=False,
                error_message=str(e),
                error_code="INVALID_STATUS_TRANSITION"
            )
            
        except OrderValidationError as e:
            return BulkUpdateOrderItemResult(
                order_id=update_item.order_id,
                success=False,
                error_message=str(e),
                error_code="VALIDATION_ERROR"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error updating order {update_item.order_id}: {str(e)}")
            return BulkUpdateOrderItemResult(
                order_id=update_item.order_id,
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                error_code="INTERNAL_ERROR"
            ) 