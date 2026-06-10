import pytest
from fastapi.testclient import TestClient
from main import app
import httpx

client = TestClient(app)

# ── Auth ───────────────────────────────────────────────────────────────

SUPABASE_URL = "https://tuuwgfawttwmljxsitnv.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1dXdnZmF3dHR3bWxqeHNpdG52Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5MDczNTAsImV4cCI6MjA5NjQ4MzM1MH0.p-OsHynYnbymupQ7QePZU473-KLQThn1JA2E5Vt7G7E"

def get_token():
    """Get a fresh JWT token for test@test.com."""
    response = httpx.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
        json={"email": "test@test.com", "password": "Test1234"}
    )
    return response.json()["access_token"]


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def auth_headers():
    """
    A fixture is a reusable setup block.
    scope="module" means the token is fetched once for all tests in this file.
    """
    token = get_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_habit(auth_headers):
    """
    Creates a habit before a test and deletes it after.
    This is called a setup/teardown pattern.
    """
    # SETUP — runs before the test
    response = client.post(
        "/habits",
        json={"name": "Test Habit"},
        headers=auth_headers
    )
    habit = response.json()

    yield habit  # the test runs here, with access to this habit

    # TEARDOWN — runs after the test, even if the test fails
    client.delete(f"/habits/{habit['id']}", headers=auth_headers)


# ── Tests ──────────────────────────────────────────────────────────────

def test_server_is_alive():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_habits_requires_auth():
    """A fake token should return 401."""
    response = client.get("/habits", headers={"Authorization": "Bearer faketoken"})
    assert response.status_code == 401


def test_get_habits_returns_list(auth_headers):
    """Authenticated request should return a list."""
    response = client.get("/habits", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_habit(auth_headers):
    """Creating a habit should return 201 and the habit data."""
    response = client.post(
        "/habits",
        json={"name": "Exercise"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Exercise"

    # Cleanup — delete the habit we just created
    client.delete(f"/habits/{response.json()['id']}", headers=auth_headers)


def test_delete_habit(auth_headers, created_habit):
    """Deleting a habit should return 204."""
    response = client.delete(
        f"/habits/{created_habit['id']}",
        headers=auth_headers
    )
    assert response.status_code == 204


def test_complete_habit(auth_headers, created_habit):
    """Marking a habit done should return 201."""
    response = client.post(
        f"/completions/{created_habit['id']}",
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["habit_id"] == created_habit["id"]

    # Cleanup — undo the completion
    client.delete(f"/completions/{created_habit['id']}", headers=auth_headers)


def test_cannot_complete_habit_twice(auth_headers, created_habit):
    """Completing the same habit twice today should return 400."""
    # First completion
    client.post(f"/completions/{created_habit['id']}", headers=auth_headers)

    # Second completion — should fail
    response = client.post(
        f"/completions/{created_habit['id']}",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Already completed today"

    # Cleanup
    client.delete(f"/completions/{created_habit['id']}", headers=auth_headers)