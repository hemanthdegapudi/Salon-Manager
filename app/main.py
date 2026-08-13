from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models import Customer, Invoice, InvoiceItem, Settings
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    InvoiceCreate,
    InvoiceCreateResponse,
)

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(
        name=customer.name,
        phone_number=customer.phone_number,
    )
    db.add(new_customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone number already exists")
    db.refresh(new_customer)
    return new_customer


@app.get("/customers", response_model=List[CustomerResponse])
def search_customers(phone: str, db: Session = Depends(get_db)):
    results = (
        db.query(Customer)
        .filter(Customer.phone_number.like(f"{phone}%"))
        .limit(10)
        .all()
    )
    return results


@app.post("/invoices", response_model=InvoiceCreateResponse, status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    # Step 1 — Fetch gst_rate from settings
    row = db.query(Settings).filter(Settings.setting_key == "gst_rate").first()
    if not row:
        raise HTTPException(status_code=500, detail="gst_rate not found in settings")
    gst_rate = float(row.setting_value)

    # Step 2 & 3 — Compute line totals and subtotal
    subtotal = 0.0
    for item in payload.items:
        line_total = item.price_charged * (1 - item.discount_percent / 100)
        subtotal += line_total

    gst_amount = round(subtotal * (gst_rate / 100), 2)
    total_amount = round(subtotal + gst_amount, 2)

    # Step 4 — Payment status
    if payload.cash_amount + payload.online_amount >= total_amount:
        payment_status = "paid"
    else:
        payment_status = "pending"

    # Step 5 — Save invoice + items in one transaction
    try:
        invoice = Invoice(
            customer_id=payload.customer_id,
            total_amount=total_amount,
            cash_amount=payload.cash_amount,
            online_amount=payload.online_amount,
            payment_status=payment_status,
            gst_percent=gst_rate,
            gst_amount=gst_amount,
            discount_amount=round(
                sum(
                    i.price_charged * (i.discount_percent / 100)
                    for i in payload.items
                ),
                2,
            ),
        )
        db.add(invoice)
        db.flush()  # get invoice.id without committing

        for item in payload.items:
            db.add(
                InvoiceItem(
                    invoice_id=invoice.id,
                    staff_id=item.staff_id,
                    service_id=item.service_id,
                    product_id=item.product_id,
                    custom_description=item.custom_description,
                    price_charged=item.price_charged,
                    discount_percent=item.discount_percent,
                )
            )

        db.commit()
        db.refresh(invoice)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return InvoiceCreateResponse(
        invoice_id=invoice.id,
        total_amount=float(invoice.total_amount),
        gst_amount=float(invoice.gst_amount),
        payment_status=invoice.payment_status,
    )
