from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routers import login, signup, users

# Create a FastAPI app instance and include routers
app = FastAPI()
app.include_router(login.router)
app.include_router(signup.router)


client = TestClient(app)


def test_signup_user():
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "phone_number": "1234567890",
        "password": "testpassword",
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 200
    assert "id" in response.json()


def test_signup_duplicate_email():
    data = {
        "name": "Test User2",
        "email": "testuser@example.com",
        "phone_number": "0987654321",
        "password": "testpassword",
    }
    response = client.post("/signup", json=data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"]


def test_login_access_token():
    # First, sign up
    data = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "phone_number": "0987567321",
        "password": "testpassword",
    }
    client.post("/signup", json=data)
    # Now, login
    response = client.post(
        "/login/access-token",
        params={"email": "loginuser@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_me():
    # Sign up and login to get token
    data = {
        "name": "Me User",
        "email": "meuser@example.com",
        "phone_number": "0987654421",
        "password": "testpassword",
    }
    client.post("/signup", json=data)
    token_resp = client.post(
        "/login/access-token",
        params={"email": "meuser@example.com", "password": "testpassword"},
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/login/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "meuser@example.com"
