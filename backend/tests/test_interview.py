import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token():
    res = client.post("/api/v1/auth/login", json={
        "email": "student@careervoice.ai",
        "password": "password123"
    })
    return res.json()["access_token"]

def test_get_roles():
    res = client.get("/api/v1/interviews/roles")
    assert res.status_code == 200
    roles = res.json()
    assert "Full Stack Engineer" in roles
    assert "Frontend Engineer" in roles

def test_get_domains():
    res = client.get("/api/v1/interviews/domains")
    assert res.status_code == 200
    catalog = res.json()
    assert "Full Stack Engineer" in catalog
    assert "MERN Stack (MongoDB, Express, React, Node)" in catalog["Full Stack Engineer"]["stacks"]
    assert "AI / ML Engineer" in catalog
    assert "Deep Learning & PyTorch / TensorFlow" in catalog["AI / ML Engineer"]["stacks"]

def test_create_interview_session_with_tech_stack():
    token = get_auth_token()
    res = client.post(
        "/api/v1/interviews/sessions",
        json={
            "role": "Full Stack Engineer",
            "difficulty": "intermediate",
            "question_count": 3,
            "interview_type": "technical",
            "tech_stack": ["MERN Stack (MongoDB, Express, React, Node)", "React.js"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert "session_id" in data
    assert data["tech_stack"] == ["MERN Stack (MongoDB, Express, React, Node)", "React.js"]
    assert "current_question" in data
    # Check that MERN/React keywords or prompt tailoring is present
    q_text = data["current_question"]["question_text"]
    assert any(term in q_text for term in ["MERN", "React", "Express", "MongoDB", "full-stack", "architecture"])
