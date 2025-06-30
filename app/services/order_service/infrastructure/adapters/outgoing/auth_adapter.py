from typing import Dict, Any, Optional, List
from uuid import UUID

from app.shared.acl.unified_acl import UnifiedACL, ServiceContext
from app.shared.domain.enums.enums import ServiceType


class AuthServiceAdapter:
    """
    Adapter for communicating with the auth service from the order service.
    """
    
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID from the auth service.
        
        Args:
            user_id: The UUID of the user to fetch
            
        Returns:
            User information as a dictionary, or None if not found
        """
        try:
            result = self._acl.execute_service_operation(
                ServiceContext(
                    service_type=ServiceType.AUTH,
                    operation="GET_USER_BY_ID",
                    data={"user_id": str(user_id)}
                )
            )
            
            if result.success and result.data:
                return result.data
            else:
                return None
                
        except Exception as e:
            # Log the error but don't raise to avoid breaking order queries
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch user {user_id} from auth service: {str(e)}")
            return None

    def get_health_care_center_by_id(self, center_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get health care center information by ID from the auth service.
        
        Args:
            center_id: The UUID of the health care center to fetch
            
        Returns:
            Health care center information as a dictionary, or None if not found
        """
        try:
            result = self._acl.execute_service_operation(
                ServiceContext(
                    service_type=ServiceType.AUTH,
                    operation="GET_HEALTH_CARE_CENTER_BY_ID",
                    data={"center_id": str(center_id)}
                )
            )
            
            if result.success and result.data:
                return result.data
            else:
                return None
                
        except Exception as e:
            # Log the error but don't raise to avoid breaking order queries
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch health care center {center_id} from auth service: {str(e)}")
            return None

    def get_users_by_ids(self, user_ids: List[UUID]) -> Dict[UUID, Dict[str, Any]]:
        """
        Get multiple users by their IDs from the auth service.
        
        Args:
            user_ids: List of user UUIDs to fetch
            
        Returns:
            Dictionary mapping user_id to user information
        """
        users = {}
        
        for user_id in user_ids:
            try:
                user = self.get_user_by_id(user_id)
                if user:
                    users[user_id] = user
            except Exception as e:
                # Log error but continue with other users
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to fetch user {user_id}: {str(e)}")
                
        return users