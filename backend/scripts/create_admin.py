import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import getpass
import sys

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User
from app.services.auth import hash_password


def main() -> None:
    print("=== VendorBridge Admin Setup ===")

    email = input("Admin email: ").strip().lower()
    if not email or "@" not in email:
        print("Please enter a valid email.")
        sys.exit(1)

    full_name = input("Admin full name: ").strip()
    if len(full_name) < 2:
        print("Full name must contain at least 2 characters.")
        sys.exit(1)

    password = getpass.getpass("Admin password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")

    if len(password) < 12:
        print("Password must be at least 12 characters.")
        sys.exit(1)

    if password != confirmation:
        print("Passwords do not match.")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == email))

        if existing:
            print("An account with this email already exists.")
            print("No account or role was changed.")
            sys.exit(1)

        admin = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()

        print(f"Admin account created successfully for {email}.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
