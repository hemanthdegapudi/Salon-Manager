from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional


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


# ── Invoice schemas ──────────────────────────────────────────


class InvoiceItemCreate(BaseModel):
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    staff_id: int
    price_charged: float
    discount_percent: float = 0.00
    custom_description: Optional[str] = None

    @field_validator("price_charged")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price_charged must be greater than 0")
        return v

    @field_validator("discount_percent")
    @classmethod
    def discount_in_range(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("discount_percent must be between 0 and 100")
        return v


class InvoiceCreate(BaseModel):
    customer_id: int
    staff_id: int
    cash_amount: float = 0.00
    online_amount: float = 0.00
    discount_percent: float = 0.00
    items: List[InvoiceItemCreate]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: List[InvoiceItemCreate]) -> List[InvoiceItemCreate]:
        if len(v) == 0:
            raise ValueError("items list must not be empty")
        return v


class InvoiceCreateResponse(BaseModel):
    invoice_id: int
    total_amount: float
    gst_amount: float
    payment_status: str
