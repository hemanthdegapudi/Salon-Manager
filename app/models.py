from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
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


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    cash_amount = Column(Numeric(10, 2), default=0)
    digital_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    price_charged = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    staff = relationship("Staff", back_populates="invoice_items")
    service = relationship("Service", back_populates="invoice_items")
