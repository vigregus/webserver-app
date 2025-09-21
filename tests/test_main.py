import pytest
from fastapi.testclient import TestClient

import main as m

client = TestClient(m.app)


@pytest.fixture(autouse=True)
def reset_state():
    m.users_db.clear()
    m.user_id_counter = 1


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["service"] == "backend-api"


def test_users_crud_and_stats():
    # initially empty
    r = client.get("/api/users")
    assert r.status_code == 200
    assert r.json() == []

    # create
    u1 = {"name": "Alice", "email": "alice@example.com", "age": 22}
    u2 = {"name": "Bob", "email": "bob@example.com", "age": 35}
    r1 = client.post("/api/users", json=u1)
    r2 = client.post("/api/users", json=u2)
    assert r1.status_code == 200
    assert r2.status_code == 200
    user1 = r1.json()
    user2 = r2.json()
    assert user1["id"] == 1 and user2["id"] == 2

    # get list
    r = client.get("/api/users")
    assert r.status_code == 200
    assert len(r.json()) == 2

    # get by id
    r = client.get("/api/users/1")
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"

    # duplicate email -> 400
    r = client.post(
        "/api/users", json={"name": "X", "email": "alice@example.com", "age": 30}
    )
    assert r.status_code == 400

    # update user 2
    r = client.put(
        "/api/users/2", json={"name": "Bobby", "email": "bob@example.com", "age": 36}
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Bobby"

    # stats
    r = client.get("/api/stats")
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_users"] == 2
    assert isinstance(stats["average_age"], float)
    assert "18-25" in stats["users_by_age_group"]

    # delete
    r = client.delete("/api/users/1")
    assert r.status_code == 200
    r = client.get("/api/users")
    assert len(r.json()) == 1
