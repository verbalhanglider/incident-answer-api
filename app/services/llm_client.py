import json
import logging
from urllib import request
from urllib.error import HTTPError
from jsonschema import validate, ValidationError, SchemaError
from typing import Dict, Any

logger = logging.getLogger(__name__)

def validate_output(data: dict, schema) -> bool:
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logger.exception("Validation error", extra={"error_detail": str(e)})
    except SchemaError as e:
        logger.exception("Schema error", extra={"error_detail": str(e)})
    return False

def call_llm_with_retry(url: str, payload: dict, schema: Dict[str, Any], retries=3) -> dict:
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(url, body, headers={'Content-Type': 'application/json'}, method="POST")
    last_result = {}
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
                if validate_output(inner, schema):
                    last_result = inner
                    return last_result
                last_result = {"error": "invalid schema", "raw": inner}
        except urllib.error.HTTPError as e: # type: ignore
            body = e.read().decode("utf-8", errors="replace")
            last_inner = {"error": str(e.reason), "status": e.code, "body": body}
    return last_result