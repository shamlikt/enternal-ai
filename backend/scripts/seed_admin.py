"""seed_admin.py — Create the initial admin user if no users exist.

Run after Alembic migrations:
    python backend/scripts/seed_admin.py

Environment variables read from .env (via pydantic-settings):
    DATABASE_URL, JWT_SECRET_KEY (indirectly via app.config)
"""

import asyncio
import os
import sys

# Allow running as `python scripts/seed_admin.py` from the backend/ dir.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.modules.auth.models import Role, User


async def seed_admin() -> None:
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@enternal.health")
    admin_password = os.getenv("ADMIN_PASSWORD", "changeme")

    async with async_session_factory() as session:
        result = await session.execute(select(User).limit(1))
        existing = result.scalar_one_or_none()

        if existing is not None:
            print(f"[seed_admin] Users already exist — skipping seed.")
            return

        admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            role=Role.ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"[seed_admin] Created admin user: {admin_email}")
        print("[seed_admin] IMPORTANT: Change the default password immediately.")


if __name__ == "__main__":
    asyncio.run(seed_admin())
