from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.core.app import create_app
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.mongo import MongoDBClient


class FakeUsersCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []

    async def find_one(self, query: dict) -> dict | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None

    async def insert_one(self, document: dict) -> SimpleNamespace:
        stored_document = document.copy()
        stored_document["_id"] = ObjectId()
        self.documents.append(stored_document)
        return SimpleNamespace(inserted_id=stored_document["_id"])


class FakeDatabase:
    def __init__(self) -> None:
        self.users = FakeUsersCollection()


@pytest.fixture
def fake_db() -> FakeDatabase:
    original_db = MongoDBClient._db
    database = FakeDatabase()
    MongoDBClient._db = database
    try:
        yield database
    finally:
        MongoDBClient._db = original_db


@pytest.fixture
def client(fake_db: FakeDatabase) -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def add_user(
    fake_db: FakeDatabase,
    *,
    email: str = "user@example.com",
    password: str = "Secret123!",
    name: str = "Test User",
    is_active: bool = True,
) -> dict:
    user = {
        "_id": ObjectId(),
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "is_active": is_active,
    }
    fake_db.users.documents.append(user)
    return user


def test_register_creates_user_with_hashed_password(client: TestClient, fake_db: FakeDatabase) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "User@Example.com",
            "password": "Secret123!",
            "name": "Ada Lovelace",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "email": "user@example.com",
        "name": "Ada Lovelace",
    }
    assert len(fake_db.users.documents) == 1
    stored_user = fake_db.users.documents[0]
    assert stored_user["email"] == "user@example.com"
    assert stored_user["password_hash"] != "Secret123!"
    assert verify_password("Secret123!", stored_user["password_hash"])


def test_register_rejects_duplicate_email(client: TestClient, fake_db: FakeDatabase) -> None:
    add_user(fake_db)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "Secret123!",
            "name": "Ada Lovelace",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "User already exists",
        "error_code": "USER_EXISTS",
    }


def test_login_returns_bearer_token(client: TestClient, fake_db: FakeDatabase) -> None:
    user = add_user(fake_db, email="analyst@example.com", password="Secret123!", name="Analyst")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "Secret123!"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0

    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["sub"] == str(user["_id"])
    assert token_payload["email"] == "analyst@example.com"


def test_login_rejects_invalid_credentials(client: TestClient, fake_db: FakeDatabase) -> None:
    add_user(fake_db, email="analyst@example.com", password="Secret123!")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "WrongPass123!"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
        "error_code": "UNAUTHORIZED",
    }


def test_protected_route_returns_current_user(client: TestClient, fake_db: FakeDatabase) -> None:
    user = add_user(fake_db, email="founder@example.com", name="Founder")
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    response = client.get(
        "/api/v1/protected/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user["_id"]),
        "email": "founder@example.com",
        "name": "Founder",
    }


def test_protected_route_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/protected/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid token",
        "error_code": "UNAUTHORIZED",
    }


def test_protected_route_rejects_expired_token(client: TestClient, fake_db: FakeDatabase) -> None:
    user = add_user(fake_db)
    token = create_access_token(
        {"sub": str(user["_id"]), "email": user["email"]},
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/v1/protected/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Token expired",
        "error_code": "UNAUTHORIZED",
    }
