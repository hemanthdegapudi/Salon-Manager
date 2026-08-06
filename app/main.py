from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerResponse

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
