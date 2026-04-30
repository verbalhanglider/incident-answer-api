import json
import logging
from urllib import request
from urllib.error import HTTPError
from json import JSONDecodeError
from jsonschema import validate, ValidationError, SchemaError
from typing import Dict, Any

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

def call_llm_with_retry(url: str, payload: dict, schema: Dict[str, Any], retries=3) -> dict:
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(url, body, headers={'Content-Type': 'application/json'}, method="POST")
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
                is_valid, error_detail = validate_output(inner, schema)
                if is_valid is True:
                    return inner
                last_result = {
                    "status_code": 422,
                    "error": "output from llm did not match expected schema",
                    "raw": json.dumps(inner),
                }
        except HTTPError as e:
            last_result = {"error": str(e.reason), "status_code": e.code, "raw": body}
        except JSONDecodeError as e:
            last_result = {"error": "invalid json from llm service", "status_code": 502, "raw": body}
    return last_result