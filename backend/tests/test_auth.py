import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_demo_student():
    response = client.post("/api/v1/auth/login", json={
        "email": "student@careervoice.ai",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"

def test_login_demo_recruiter():
    response = client.post("/api/v1/auth/login", json={
        "email": "recruiter@careervoice.ai",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "recruiter"

def test_invalid_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@careervoice.ai",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
