import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from fastapi.testclient import TestClient
from app.main import app

# Use a separate test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")  # Must be set in environment or .env (never committed)

# Create a new engine and session for testing
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Drop and recreate all tables before tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="module")
def client(db_session):
    # Override dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides = {}
    app.dependency_overrides["get_db"] = override_get_db
    with TestClient(app) as c:
        yield c
