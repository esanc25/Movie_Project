import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app 
from app.models import Books 
from app.scripts.populate_db import book_data

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def client():
    """A fake browser that sends requests straight to the app, using the test database."""
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def reset_db():
    """Runs before EVERY test: start each one with empty tables."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

@pytest.fixture
def seeded_db():
    """Fill the test database with the same books the real one starts with."""
    with TestingSessionLocal() as db:
        db.add_all(Books(**books) for books in book_data)
        db.commit()
    return book_data

@pytest.fixture
def sample_book():
    return {
        "title" : "Call Down the Hawk",
        "author" : "Maggie Stiefvater",
        "release_year" : 2019, 
        "page_length" : 469,
        "description" : "This is a story about the Lynch brothers- one who knows the magic business inside and out, one who pulls things out of his dreams, and one who is made of dreams himself.",
        "image_url" : "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1550860945i/31373184.jpg",
    }

@pytest.fixture
def updated_book():
    return {
        "title" : "The Perks of Being a Wallflower",
        "author" : "Stephen Chbosky",
        "release_year" : 1999, 
        "page_length" : 213,
        "description" : "The story follows Charlie as he navigates high school with all the school drama, family drama, and emotional turmoil",
        "image_url" : "https://static1.srcdn.com/wordpress/wp-content/uploads/2023/05/perks-of-being-a-wallflower-poster.jpeg",
    }

@pytest.fixture
def created_book(client, sample_book):
    response = client.post("/media/", json=sample_book)
    assert response.status_code == 201
    return response.json()
