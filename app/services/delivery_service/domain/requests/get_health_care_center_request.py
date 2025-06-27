from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetHealthCareCenterRequest:
    """Request to get health care center by ID"""
    center_id: UUID


@dataclass
class GetUserHealthCareCenterRequest:
    """Request to get health care center for a user"""
    user_id: UUID 