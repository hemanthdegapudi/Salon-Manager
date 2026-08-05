"""
One-off script to create all 5 tables in MySQL.
Run this ONCE after your .env has real DB credentials.
Run from inside the Salon/ folder:

    python create_tables.py

This uses Base.metadata.create_all — it is safe to re-run (it won't
drop existing tables or data, it only creates what's missing).
"""

from app.database import engine, Base
import app.models  # noqa: F401 — import triggers model registration on Base

Base.metadata.create_all(bind=engine)
print("Tables created (or already existed).")
