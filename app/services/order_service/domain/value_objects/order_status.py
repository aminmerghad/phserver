from enum import Enum

class OrderStatus(Enum):
    PENDING = "PENDING"        # Order created but not yet processed
    PROCESSING = "PROCESSING"  # Order being prepared for fulfillment
    SHIPPED = "SHIPPED"        # Order dispatched and in transit
    COMPLETED = "COMPLETED"    # Order successfully delivered/fulfilled
    CANCELLED = "CANCELLED"    # Order cancelled before completion
    FAILED = "FAILED"          # Order failed during fulfillment

    @classmethod
    def can_transition(cls, current: 'OrderStatus', target: 'OrderStatus') -> bool:
        transitions = {
            cls.PENDING: [cls.CANCELLED, cls.PROCESSING],
            cls.PROCESSING: [cls.SHIPPED, cls.COMPLETED, cls.CANCELLED],
            cls.SHIPPED: [cls.COMPLETED, cls.FAILED, cls.CANCELLED],
            cls.COMPLETED: [],
            cls.CANCELLED: [],
            cls.FAILED: []
        }
        return target in transitions.get(current, [])



