from enum import Enum


class DeliveryStatus(Enum):
    """
    Enum representing the possible statuses of a delivery route.
    """
    PENDING = "PENDING"           # Route created but not yet assigned
    ASSIGNED = "ASSIGNED"         # Route assigned to delivery personnel
    IN_TRANSIT = "IN_TRANSIT"     # Delivery in progress
    DELIVERED = "DELIVERED"       # Successfully delivered
    FAILED = "FAILED"             # Delivery failed
    CANCELLED = "CANCELLED"       # Delivery cancelled
    RETURNED = "RETURNED"         # Package returned to sender

    def __str__(self):
        return self.value
    
    @classmethod
    def active_statuses(cls) -> list:
        """Return statuses that indicate active delivery"""
        return [cls.ASSIGNED, cls.IN_TRANSIT]
    
    @classmethod
    def completed_statuses(cls) -> list:
        """Return statuses that indicate completed delivery"""
        return [cls.DELIVERED, cls.FAILED, cls.CANCELLED, cls.RETURNED]
    
    @classmethod
    def can_transition(cls, current: 'DeliveryStatus', target: 'DeliveryStatus') -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            cls.PENDING: [cls.ASSIGNED, cls.CANCELLED],
            cls.ASSIGNED: [cls.IN_TRANSIT, cls.CANCELLED],
            cls.IN_TRANSIT: [cls.DELIVERED, cls.FAILED, cls.RETURNED],
            cls.DELIVERED: [],
            cls.FAILED: [cls.ASSIGNED],  # Can retry
            cls.CANCELLED: [],
            cls.RETURNED: [cls.ASSIGNED]  # Can retry
        }
        
        return target in valid_transitions.get(current, []) 