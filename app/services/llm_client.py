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
     AppException,
     UnsupportedLLMProviderException
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

def do_http_call(body: dict[str, Any], url: str) -> dict[str, Any]:
    req = request.Request(
                          url,
                          json.dumps(body).encode('utf-8'),
                          headers={'Content-Type': 'application/json'},
                          method="POST"
                         )
    with request.urlopen(req) as response:
        raw_body = response.read().decode('utf-8')
        outer = json.loads(raw_body)
        if isinstance(outer, str):
            outer = json.loads(outer)
        return outer


def call_llm_with_retry(spec: LLMRequestSpec, retries=3) -> dict:
    adapter = PROVIDER_REGISTRY.get(spec.provider)
    if not adapter:
        raise AppException(message=f"unsupported provider {spec.provider}", details=f"provider {spec.provider}")
    payload = adapter.build_payload(spec)
    raw_body = None
    last_exc: Exception | None = None
    for attempt in range(retries):
        try: 
            raw_body = do_http_call(payload, spec.url)
            output = adapter.extract_response(raw_body)
            print(output)
            print(spec.output_schema)
            logger.info("output=%r type=%s schema=%r", output, type(output), spec.output_schema)
            validate_output(output, spec.output_schema)
            return  output
        except ServiceRequestValidationException as e:
            last_exc = e
            logger.warning(f"llm service sent invalid response ${str(e)} on {attempt+1}")
        except KeyError as e:
            last_exc = e 
            logger.warning(f"llm service sent invalid response: missing field ${str(e)} on attempt {attempt+1}")
        except HTTPError as e:
            last_exc = e
            logger.warning(f"llm service experience HTTPError {str(e)} on attempt {attempt+1}")
        except URLError as e:
            last_exc = e
            logger.warning(f"llm service experience network failure {str(e)} on {attempt+1}")
        except JSONDecodeError as e:
            last_exc = e
            logger.warning(f"llm service sent invalid JSON: {str(e)} on {attempt+1}")
    if isinstance(last_exc, KeyError):
        raise UpstreamServiceInvalidResponseException(message="LLM Service sent invalid response",
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
