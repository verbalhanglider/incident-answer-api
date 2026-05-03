from fastapi.testclient import TestClient
from app.main import app
from app.api import routes
from app.models.requests import ExtractionRequest, ClassificationRequest, ContextAnswerRequest

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "I am alive"}

def test_extract_invalid_payload():
    response = client.post("/extract", json={})
    assert response.status_code == 422

def test_answer_with_context_ok(monkeypatch):
    calls = []

    def fake_llm_answer_from_contextt(text):
        calls.append(text)
        return {"kind": "context", "answer": "I do not know"}
    
    monkeypatch.setattr(routes, 'llm_answer_from_context', fake_llm_answer_from_contextt)
    payload = {"text": "help me get a refund"} 
    response = client.post("/answer/context", json=payload)
    assert response.status_code == 200
    assert response.json()['answer'] == 'I do not know'
    assert calls == [ContextAnswerRequest(**payload)]


def test_extract(monkeypatch):
    calls = []

    def fake_llm_extract_request(text, **kwargs):
        calls.append(text)
        return {"kind": "extract", "issue":"billing", "customer": "john doe", "amount": 200, "issue_type": "refund", "summary": "some note"}

    monkeypatch.setattr(routes, 'llm_extract_request', fake_llm_extract_request)
    payload = {"text": "what is your return policy"}
    response = client.post("/extract", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response['issue'] == 'billing'
    assert json_response['customer'] == 'john doe'
    assert json_response['amount'] == 200
    assert json_response['issue_type'] == 'refund'
    assert json_response['summary'] == 'some note'  
    assert calls == [ExtractionRequest(**payload)]

def test_classify(monkeypatch):
    calls = []

    def fake_llm_classify_request(fake_request, **kwargs):
        calls.append(fake_request)
        return {"kind": "classification", "intent": "get_refund", "confidence": 0.95, "confidence_notes": "the user is asking about a refund", "raw_text":  fake_request.text}

    monkeypatch.setattr(routes, 'llm_classify_request', fake_llm_classify_request)
    payload = {"text": "what is your return policy"}
    response = client.post("/classify", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response['intent'] == 'get_refund'
    assert json_response['confidence'] == 0.95
    assert json_response['confidence_notes'] == 'the user is asking about a refund'
    assert json_response['raw_text'] == payload['text']
    assert calls == [ClassificationRequest(**payload)]