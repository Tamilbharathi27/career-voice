import sys
import os
import pytest

# Add backend root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal, engine, Base
from app.db.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database schema is created and demo data is seeded before running tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield
