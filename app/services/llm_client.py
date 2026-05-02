import json
import logging
from urllib import request
from urllib.error import HTTPError
from json import JSONDecodeError
from jsonschema import validate, ValidationError, SchemaError
from typing import Dict, Any

from ..models.internals import LLMRequestSpec, build_ollama_provider_payload

logger = logging.getLogger(__name__)

def validate_output(data: dict, schema) -> tuple[bool, str | None]:
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        logger.exception("Validation error", extra={"error_detail": str(e)})
        return False, str(e)
    except SchemaError as e:
        logger.exception("Schema error", extra={"error_detail": str(e)})
        return False, str(e)

def _build_requeset_payload(spec: LLMRequestSpec) -> dict[str, Any]:
    if spec.provider == "ollama":
        return build_ollama_provider_payload(spec).model_dump()
    raise ValueError(f"unsupported provider {spec.provider}")

def call_llm_with_retry(spec: LLMRequestSpec, retries=3) -> dict:
    payload = _build_requeset_payload(spec)
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(spec.url, body, headers={'Content-Type': 'application/json'}, method="POST")
    last_result = {
        "status_code": 500,
        "error": "unknown llm failure",
        "raw": None,
    }
    body = None
    for count in range(retries+1):
        logger.info(f'safe retry {count}')
        try:
            with request.urlopen(req) as response:
                body = response.read().decode('utf-8')
                outer = json.loads(body)
                inner = outer['message']['content']
                if isinstance(inner, str):
                    inner = json.loads(inner)
                is_valid, error_detail = validate_output(inner, spec.output_schema)
                if is_valid is True:
                    return inner
                last_result = {
                    "status_code": 422,
                    "error": error_detail,
                    "raw": json.dumps(inner),
                }
        except HTTPError as e:
            last_result = {"error": str(e.reason), "status_code": e.code, "raw": body}
        except JSONDecodeError as e:
            last_result = {"error": "invalid json from llm service", "status_code": 502, "raw": body}
    return last_result