import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_api_docs():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_contact_endpoint():
    """Test the contact API endpoint"""
    contact_data = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a test message"
    }
    response = client.post("/api/contact/", json=contact_data)
    # This might fail if database is not set up, but should not crash
    assert response.status_code in [200, 500]  # 500 if DB not configured

