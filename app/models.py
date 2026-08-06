from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="customer")


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice_items = relationship("InvoiceItem", back_populates="staff")


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    invoice_items = relationship("InvoiceItem", back_populates="service")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    type = Column(Enum("for_sale", "shop_use", name="product_type"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice_items = relationship("InvoiceItem", back_populates="product")


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    cash_amount = Column(Numeric(10, 2), default=0)
    online_amount = Column(Numeric(10, 2), default=0)       # renamed from digital_amount
    payment_status = Column(
        Enum("pending", "paid", name="payment_status_enum"),
        default="pending",
        nullable=False,
    )
    gst_percent = Column(Numeric(5, 2), default=0)
    gst_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)   # relaxed: NULL allowed
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)   # new FK
    custom_description = Column(String(150), nullable=True)
    price_charged = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "service_id IS NOT NULL OR product_id IS NOT NULL OR custom_description IS NOT NULL",
            name="chk_item_has_service_or_product",
        ),
    )

    invoice = relationship("Invoice", back_populates="items")
    staff = relationship("Staff", back_populates="invoice_items")
    service = relationship("Service", back_populates="invoice_items")
    product = relationship("Product", back_populates="invoice_items")
