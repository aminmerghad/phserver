from pydantic import BaseModel


class HealthCareCenterDto(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    latitude: float
    longitude: float

class UserRegisterDto(BaseModel):
    code:str
    username: str
    password: str
    full_name: str
    phone: str
    email: str
    health_care_center: HealthCareCenterDto = None