import json
from urllib.request import Request 
from urllib.error import HTTPError
from unittest.mock import Mock
from app.services import llm_client
from app.models.internals import LLMRequestSpec

class FakeURLResponse:
    def __init__(self, body):
        self._body = body
    def read(self):
        return self._body
    def __enter__(self):
        # for contextmanager
        return self
    def __exit__(self, exec_type, exec, tb):
        # cleanup hook
        # for contextmanager
        return False

def test_call_llm_with_retry_ok(mocker):
    answer = {"message": {"content": {"result": "hello my name is"}}}
    def fake_urlopen(req):
        return FakeURLResponse(json.dumps(answer).encode('ascii'))

    spec = LLMRequestSpec(
        model_name="gemma3",
        system_prompt="Test system prompt",
        prompt="Test prompt for LLLM request",
        provider="ollama",
        url="http://example.com/",
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    )
    spy = mocker.patch('app.services.llm_client.request.urlopen', new=fake_urlopen)
    output = llm_client.call_llm_with_retry(spec)
    assert output == answer['message']['content']

def test_call_llm_with_retry_http_error(mocker):
    def fake_urlopen(req):
        raise HTTPError(
            url=req.full_url,
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )
    spec = LLMRequestSpec(
        model_name="gemma3",
        system_prompt="Test system prompt",
        prompt="Test prompt for LLLM request",
        provider="ollama",
        url="http://example.com/",
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    )
    spy = mocker.patch('app.services.llm_client.request.urlopen', side_effect=fake_urlopen)
    response = llm_client.call_llm_with_retry(spec)
    assert response['status_code'] == 500
    assert spy.call_count == 4

def test_call_llm_with_retry_invalid_json(mocker):
    fake_response = Mock()
    fake_response.read.return_value = b'invalid json' 
    mock_urlopen = mocker.patch('app.services.llm_client.request.urlopen')
    mock_urlopen.return_value.__enter__.return_value = fake_response
    spec = LLMRequestSpec(
        model_name="gemma3",
        system_prompt="Test system prompt",
        prompt="Test prompt for LLLM request",
        provider="ollama",
        url="http://example.com/",
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    )
    response = llm_client.call_llm_with_retry(spec)
    assert response['status_code'] == 502
    assert response['error'] == "invalid json from llm service"
    assert response['raw'] == 'invalid json'
    assert mock_urlopen.call_count == 4

def test_call_llm_with_retry_invalid_schema(mocker):
    answer = {"message": {"content": {"result": "hello my name is"}}}
    def fake_urlopen(req):
        return FakeURLResponse(json.dumps(answer).encode('ascii'))
    spec = LLMRequestSpec(
        model_name="gemma3",
        system_prompt="Test system prompt",
        prompt="Test prompt for LLLM request",
        provider="ollama",
        url="http://example.com/",
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    )
    spy = mocker.patch('app.services.llm_client.request.urlopen', new=fake_urlopen)
    mocker.patch('app.services.llm_client.validate_output', return_value=(False, "validation error"))
    response = llm_client.call_llm_with_retry(spec)
    assert response['status_code'] == 422
    assert response['error'] == "validation error"
    assert response['raw'] == json.dumps(answer['message']['content'])