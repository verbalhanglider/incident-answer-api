from copy import deepcopy
import sys
import logging
import urllib
from urllib import request
import json
from jsonschema import Draft202012Validator
from jsonschema import validate, ValidationError, SchemaError
from .prompts import PROMPT_WITH_CONTEXT, INTENT_CLASSIER_SYSTEM_PROMPT, INTENT_CLASSIFIER_PROMPT, EXTRACTOR_SYSTEM_PROMPT, INTENT_CLASSIER_SYSTEM_PROMPT
from .schemas import CLASSIFIER_SCHEMA, EXTRACTION_SCHEMA, EXTRACTION_FROM_CONTEXT_SCHEMA

logger = logging.getLogger(__name__)

DOCS = [
    "You can request a refund within 30 days of purchase.",
    "Shipping usually takes 3-5 business days.",
    "You can reset your password from the account settings page.",
    "Invoices are available in your billing dashboard.",
]

def validate_output(data: dict, schema) -> bool:
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logger.exception("Validation error", extra={"error_detail": str(e)})
    except SchemaError as e:
        logger.exception("Schema error", extra={"error_detail": str(e)})
    return False

def safe_retry(req: request.Request, schema, retries=3) -> dict:
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

def make_ollama_request(user_question, needs_classification=False, needs_context=False, needs_extraction=False, retries=0) -> dict:
    url = "http://localhost:11434/api/chat"
    logger.info(f'making request for user question {user_question}')
    system_prompt = EXTRACTOR_SYSTEM_PROMPT
    schema = EXTRACTION_SCHEMA
    if needs_classification is True: # sending a prompt for LLM to classify the user request only
        system_prompt = INTENT_CLASSIFIER_PROMPT
        schema = CLASSIFIER_SCHEMA
        prompt_msg = deepcopy(INTENT_CLASSIFIER_PROMPT)
        prompt_msg = prompt_msg.replace("FILL_IN_QUESTION", user_question)
    elif needs_context is True: # sending request for LLM to answer the user's general request from context provided
        context = '\n'.join(DOCS)
        schema = EXTRACTION_FROM_CONTEXT_SCHEMA
        prompt_msg = deepcopy(PROMPT_WITH_CONTEXT)
        prompt_msg = prompt_msg.replace("FILL_IN_CONTEXT", context)
        prompt_msg = prompt_msg.replace("FILL_IN_QUESTION", user_question)
    else: # basic request to LLM to extract answer from user message
        prompt_msg = user_question
    payload = {
           "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": system_prompt
               },
               {
                   "role": "user",
                   "content": prompt_msg
              ,}
           ],
           "format": schema,
           "stream": False
    }
    payload = json.dumps(payload).encode('utf-8')
    req = request.Request(url, payload, headers={'Content-Type': 'application/json'}, method='POST')
    result = safe_retry(req, schema)
    return result
