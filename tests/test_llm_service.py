import pytest
import json
from urllib.request import Request
from urllib.error import HTTPError
from jsonschema import validate
from app.services import llm_service

ERROR_SCHEMA = {
    'type': 'object',
    'properties': {
        'error': {'type': 'string'},
        'raw': {'type': 'string'}
    },
    'required': ['error', 'raw']
}

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

def test_make_ollama_request_needs_classifier_ok(mocker):
    spy = mocker.patch('app.services.llm_service.safe_retry', return_value={'answer': 'ok'})
    response = llm_service.make_ollama_request(
        "a user question",
        "you are a helpful agent answering questions for an e-commerce customer support service",
        { "type": "object", "properties": [{"name": "foo", "type": "string"}]},
        needs_extraction=True
    )
    (req_arg, schema_arg), _ = spy.call_args
    spy.assert_called_once_with(req_arg, schema_arg)

def test_safe_retry_ok(mocker):
    answer = {"message": {"content": {"result": "hello my name is"}}}
    def fake_urlopen(req):
        return FakeURLResponse(json.dumps(answer).encode('ascii'))

    req = Request(
        "http://example.com/",
        json.dumps({"test": "foo"}).encode("utf-8"),
        {'Content-Type': 'application/json', }, 'POST'
    )
    schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string"}
        }
    }
    spy = mocker.patch('app.services.llm_service.request.urlopen', new=fake_urlopen)
    output = llm_service.safe_retry(req, schema)
    assert output == answer['message']['content']

def test_safe_retry_with_http_error(mocker):
    def fake_urlopen(req):
        raise HTTPError(
            url=req.full_url,
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )
    req = Request(
        "http://example.com/",
         json.dumps({"test": "foo"}).encode("utf-8"),
         {"Content-Type": "application/json"},
         method="POST",
    )
    spy = mocker.patch('app.services.llm_service.request.urlopen', sie_effect=fake_urlopen)

