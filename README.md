# Salon Manager — POS Backend for Aniq Unisex Salon

A production-shaped Point-of-Sale backend system built with Python and FastAPI,
designed to solve a real business problem: a small salon with no reliable way to
track daily sales, customer history, or staff performance.

This project is actively deployed using Docker and is part of my engineering portfolio,
built to demonstrate backend engineering skills as I transition into product engineering.

---

## The Problem It Solves

Aniq Unisex Salon (Gudur, Andhra Pradesh) was running entirely on memory and paper.
No customer records. No invoice history. No way to know which staff member drove which
revenue. This system changes that.

**Core business problems addressed:**
- No reliable sales tracking → fixed by structured invoice + invoice_item tables
- No customer retention data → fixed by customer profiles with phone-number lookup
- No payment audit trail → fixed by a two-column model tracking cash and online separately
- No GST compliance → fixed by a configurable settings table (default 18%)

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Language    | Python 3.11                       |
| Framework   | FastAPI                           |
| ORM         | SQLAlchemy (declarative models)   |
| Database    | MySQL (via PyMySQL driver)        |
| Container   | Docker + Docker Compose           |
| Migrations  | Alembic                           |
| Config      | python-dotenv                     |

---

## Architecture Overview

```
Client (curl / frontend)
        │
        ▼
  FastAPI Router Layer
        │
        ▼
  Service / Business Logic
  (GST calc, payment status, totals)
        │
        ▼
  SQLAlchemy ORM
        │
        ▼
  MySQL (salon_pos database)
```

The system follows a flat, single-service architecture — intentionally simple for a
single-location salon, no microservices overhead.

---

## Database Schema

**6 tables + 1 settings table:**

| Table          | Purpose                                              |
|----------------|------------------------------------------------------|
| `customer`     | Customer profiles with phone as unique identifier    |
| `invoice`      | One record per salon visit / billing session         |
| `invoice_item` | Line items (service or product) per invoice          |
| `service`      | Service catalog (haircut, facial, etc.)              |
| `product`      | Retail product catalog                               |
| `staff`        | Staff records for attribution                        |
| `settings`     | Key-value store for config (e.g., GST rate)          |

**Key design decisions:**
- `invoice_item.custom_description` — supports one-off services not in the catalog
- `cash_amount + online_amount` — reflects real checkout behavior (split payments)
- `payment_status` is derived server-side, never trusted from the client
- `total_amount` (with GST) is computed server-side on every invoice creation

---

## API Endpoints

### Health

| Method | Path      | Description               |
|--------|-----------|---------------------------|
| GET    | `/health` | Returns DB + app status   |

### Customers

| Method | Path             | Description                                   |
|--------|------------------|-----------------------------------------------|
| POST   | `/customers`     | Create a new customer record                  |
| GET    | `/customers`     | List all customers                            |

### Invoices

| Method | Path             | Description                                              |
|--------|------------------|----------------------------------------------------------|
| POST   | `/invoices`      | Create invoice with line items, GST auto-calculated      |
| GET    | `/invoices`      | List invoices — filterable by `date` and/or `phone`      |

**Invoice GET filters:**
```
GET /invoices?date=2025-08-15
GET /invoices?phone=9876543210
GET /invoices?date=2025-08-15&phone=9876543210
```

**Invoice POST — sample request body:**
```json
{
  "customer_phone": "9876543210",
  "staff_id": 1,
  "cash_amount": 300,
  "online_amount": 200,
  "items": [
    {
      "service_id": 2,
      "quantity": 1,
      "unit_price": 500,
      "discount_percent": 0
    }
  ]
}
```

**Invoice POST — response includes:**
- `subtotal` — sum of line items after discounts
- `gst_amount` — computed at current GST rate (from settings)
- `total_amount` — subtotal + GST
- `payment_status` — `"paid"`, `"partial"`, or `"unpaid"` (derived server-side)

---

## Running Locally

### With Docker (recommended)

```bash
git clone https://github.com/hemanthdegapudi/Salon-Manager.git
cd Salon-Manager
cp .env.example .env          # fill in your DB credentials
docker compose up --build
```

The app starts on `http://localhost:8000`.

### Without Docker

**Prerequisites:** Python 3.11+, MySQL running locally

```bash
git clone https://github.com/hemanthdegapudi/Salon-Manager.git
cd Salon-Manager

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env          # set DB_HOST=localhost and credentials

uvicorn app.main:app --reload
```

---

## Environment Variables

```env
DB_HOST=db              # use 'db' for Docker, 'localhost' for local
DB_PORT=3306
DB_NAME=salon_pos
DB_USER=your_user
DB_PASSWORD=your_password
```

---

## Interactive API Docs

FastAPI ships with auto-generated docs. Once the server is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Project Status

| Phase | Description                          | Status        |
|-------|--------------------------------------|---------------|
| 1     | Core schema + FastAPI skeleton       | ✅ Complete   |
| 2     | 4 core endpoints, tested locally     | ✅ Complete   |
| 3     | Dockerization                        | 🔄 In Progress|
| 4     | CI pipeline (GitHub Actions)         | ⬜ Planned    |
| 5     | Cloud deployment                     | ⬜ Planned    |
| 6     | Auth + RBAC (JWT, 3 roles)           | ⬜ Planned    |
| 7     | Frontend (HTML + Tailwind + Vanilla JS)| ⬜ Planned  |

---

## Planned Features

- **JWT authentication** with role-based access (Admin, Receptionist, Staff)
- **Staff commission tracking** — daily revenue attribution per staff member
- **Membership / loyalty cards** — repeat customer discounts
- **Dashboard summary endpoint** — daily totals, top services, top staff
- **Frontend** — invoice creation UI, customer management, invoice history

---

## Why This Stack

FastAPI + SQLAlchemy + MySQL was chosen because:
1. Matches existing professional experience (faster to ship)
2. FastAPI's auto-generated OpenAPI docs mean zero extra documentation work
3. SQLAlchemy's ORM makes schema migrations and model changes manageable
4. Docker containerization is a key resume gap this project explicitly closes

---

## About This Project

Built by **Hemanth Degapudi** as a portfolio project during a career transition
from support/maintenance engineering into product engineering.

The system solves a real problem for a real business — it is not a tutorial clone.
Every design decision maps to either a business requirement or a demonstrable
engineering skill.

**GitHub:** [hemanthdegapudi/Salon-Manager](https://github.com/hemanthdegapudi/Salon-Manager)
