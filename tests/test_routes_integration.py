import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import routes

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "I am alive"}

def test_classify_invalid_payload():
    response = client.post("/classify", json={})
    assert response.status_code == 422

def test_extract_invalid_payload():
    response = client.post("/extract", json={})
    assert response.status_code == 422

def test_extract_billing(monkeypatch):
    calls = []

    def fake_make_ollama_request(text, **kwargs):
        calls.append((text, kwargs))
        if "needs_classification" in kwargs:
            return {"intent": "billing"}
        if "needs_extraction" in kwargs:
            return {"customer": "john doe", "amount": 200, "issue_type": "refund", "summary": "some note"}
        if "needs_context" in kwargs:
            return {"answer": "I do not know"}
    
    monkeypatch.setattr(routes, 'make_ollama_request', fake_make_ollama_request)
    response = client.post("/extract", json={"text": "help me get a refund"})
    assert response.status_code == 200
    assert calls == [
        ("help me get a refund", {"needs_classification": True}),
        ("help me get a refund", {"needs_extraction": True})
    ]

def test_extract_general(monkeypatch):
    calls = []

    def fake_make_ollama_request(text, **kwargs):
        calls.append((text, kwargs))
        if "needs_classification" in kwargs:
            return {"intent": "general"}
        if "needs_context" in kwargs:
            return {"answer": "I do not know"}
    
    monkeypatch.setattr(routes, 'make_ollama_request', fake_make_ollama_request)
    response = client.post("/extract", json={"text": "what is your return policy"})
    assert response.status_code == 200
    assert calls == [
        ("what is your return policy", {"needs_classification": True}),
        ("what is your return policy", {"needs_context": True})
    ]

def test_extract_shipping(monkeypatch):
    calls = []

    def fake_make_ollama_request(text, **kwargs):
        calls.append((text, kwargs))
        if "needs_classification" in kwargs:
            return {"intent": "shipping"}
    
    monkeypatch.setattr(routes, 'make_ollama_request', fake_make_ollama_request)
    response = client.post("/extract", json={"text": "you guys lost my package"})
    assert response.status_code == 200
    assert calls == [
        ("you guys lost my package", {"needs_classification": True}),
    ] 