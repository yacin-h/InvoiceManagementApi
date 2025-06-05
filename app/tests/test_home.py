from fastapi import __version__
from fastapi.testclient import TestClient

from app.main import app



client = TestClient(app)
response = client.get("/")

def test_home_code():
    assert response.status_code == 200

def test_home_content():
    assert "Welcome" in response.text
    assert "FastAPI" in response.text

def test_home_version():
    assert str(__version__) in response.text
    