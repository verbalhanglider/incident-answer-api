import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import routes

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "I am alive"}

def test_extract_invalid_payload():
    response = client.post("/llm_request", json={})
    assert response.status_code == 422

def test_extract_billing(monkeypatch):
    calls = []

    def fake_make_ollama_request(text, task, **kwargs):
        calls.append((text, task))
        if task == "classify":
            return {"intent": "billing"}
        if task == "extract":
            return {"kind": "billing","customer": "john doe", "amount": 200, "issue_type": "refund", "summary": "some note"}
        if task == "answer_with_context":
            return {"kind": "context", "answer": "I do not know"}
    
    monkeypatch.setattr(routes, 'llm_extract_request', fake_make_ollama_request)
    response = client.post("/llm_request", json={"text": "help me get a refund", "task": "extract"})
    print(calls)
    assert response.status_code == 200
    assert calls == [
        ("help me get a refund", "extract")
    ]

def test_extract_general(monkeypatch):
    calls = []

    def fake_make_llm_request(text, task, **kwargs):
        calls.append((text, task))
        if task == "classify":
            return {"intent": "billing"}
        if task == "extract":
            return {"kind": "billing","customer": "john doe", "amount": 200, "issue_type": "refund", "summary": "some note"}
        if task == "answer_with_context":
            return {"kind":"context","answer": "I do not know"}

    
    monkeypatch.setattr(routes, 'llm_extract_request', fake_make_llm_request)
    response = client.post("/llm_request", json={"text": "what is your return policy", "task": "answer_with_context"})
    assert response.status_code == 200
    assert calls == [
        ("what is your return policy", "answer_with_context")
    ]