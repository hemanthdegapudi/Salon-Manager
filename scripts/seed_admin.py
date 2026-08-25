"""
Run this ONCE to create the first admin user.
Usage: python scripts/seed_admin.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.utils.auth import hash_password

# Import all models so create_all works
from app.models import *  # noqa


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("Admin user already exists. Skipping.")
        db.close()
        return

    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("Admin user created: username=admin, password=admin123")
    print("CHANGE THIS PASSWORD BEFORE GOING LIVE.")
    db.close()


if __name__ == "__main__":
    seed()
