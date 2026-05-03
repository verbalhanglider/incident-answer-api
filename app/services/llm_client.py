import json
import logging
from urllib import request
from urllib.error import HTTPError, URLError
from json import JSONDecodeError
from jsonschema import validate, ValidationError, SchemaError
from typing import Dict, Any



from .providers.base import LLMRequestSpec
from .providers.registry import PROVIDER_REGISTRY
from ..models.errors import (
     InternalSchemaConfigurationException,
     ServiceRequestValidationException,
     UpstreamServiceInvalidResponseException,
     InternalSchemaConfigurationException,
     UpstreamServiceHttpException,
     AppException
)


logger = logging.getLogger(__name__)

def validate_output(data: dict, schema):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        logger.warning("Validation error", extra={"error_detail": str(e)})
        raise ServiceRequestValidationException(
            message="LLM output did not match expected schema",
            details={
                "reason": e.message,
                "schema": e.schema
            }
        )
    except SchemaError as e:
        logger.exception(f"LLM received invalid schema", extra={"error_detail": e.message, "schema": e.schema})
        raise InternalSchemaConfigurationException(
            message="Invalid JSON schema configuration",
            details={"reason": e.message}
        )

def call_llm_with_retry(spec: LLMRequestSpec, retries=3) -> dict:
    adapter = PROVIDER_REGISTRY.get(spec.provider)
    if not adapter:
        raise ValueError(f"unsupported provider {spec.provider}")
    payload = adapter.build_payload(spec)
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(spec.url, body, headers={'Content-Type': 'application/json'}, method="POST")
    last_exc: Exception | None = None
    raw_body = None
    for count in range(retries+1):
        try:
            logger.info(f"{req.method} {req.get_full_url()} with retry {count}")
            with request.urlopen(req) as response:
                raw_body = response.read().decode('utf-8')
                outer = json.loads(raw_body)
                inner = adapter.extract_response(outer)
                if isinstance(inner, str):
                    inner = json.loads(inner)
                validate_output(inner, spec.output_schema)
                return inner
        except KeyError as e:
            last_exc = e 
            logger.warning(f"llm service sent invalid response: missing field ${str(e)}")
        except HTTPError as e:
            last_exc = e
            logger.warning(f"llm service experience HTTPError {str(e)}")
        except URLError as e:
            last_exc = e
            logger.warning(f"llm service experience network failure {str(e)}")
        except JSONDecodeError as e:
            last_exc = e
            logger.warning(f"llm service sent invalid JSON: {str(e)}")
    if isinstance(last_exc, KeyError):
        raise UpstreamServiceInvalidResponseException(message="LLM Service experience an http exception",
                                                      details=str(str(last_exc))
                                                     )
    if isinstance(last_exc, HTTPError):
        raise UpstreamServiceHttpException(message="LLM Service experience an http exception",
                                          details=str(last_exc.reason)
                                          )
    if isinstance(last_exc, URLError):
        raise UpstreamServiceInvalidResponseException(details=str(last_exc.reason),
                                                      message="LLM Service experienced network failure" 
                                                     )
    if isinstance(last_exc, JSONDecodeError):
        raise UpstreamServiceInvalidResponseException(details=str(last_exc.msg),
                                                      message="LLM Service returned invalid JSON"
                                                     )
    if last_exc is not None:
        raise AppException("LLM call failed", details={"raw": raw_body}) from last_exc
    raise AppException("LLM call failed with unknown error")
