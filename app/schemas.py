from pydantic import BaseModel
from datetime import datetime

class CustomerCreate(BaseModel):
    name: str
    phone_number: str

class CustomerResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    created_at: datetime | None

    class Config:
        from_attributes = True
