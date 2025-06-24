from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class HealthCareCenterEntity:
    id: Optional[UUID]
    name: str
    address: str
    phone: str
    email: str
    is_active: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def update(self, name=None, address=None, phone=None, email=None, latitude=None, longitude=None):
        """Update health care center properties"""
        return HealthCareCenterEntity(
            id=self.id,
            name=name if name is not None else self.name,
            address=address if address is not None else self.address,
            phone=phone if phone is not None else self.phone,
            email=email if email is not None else self.email,
            latitude=latitude if latitude is not None else self.latitude,
            longitude=longitude if longitude is not None else self.longitude,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    def deactivate(self):
        """Deactivate a health care center"""
        return HealthCareCenterEntity(
            id=self.id,
            name=self.name,
            address=self.address,
            phone=self.phone,
            email=self.email,
            latitude=self.latitude,
            longitude=self.longitude,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now()
        ) 