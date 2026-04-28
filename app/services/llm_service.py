from copy import deepcopy
import sys
import logging
import urllib
from urllib import request
import json
from typing_extensions import Literal
from jsonschema import Draft202012Validator
from jsonschema import validate, ValidationError, SchemaError
from .prompts import PROMPT_WITH_CONTEXT, INTENT_CLASSIER_SYSTEM_PROMPT, INTENT_CLASSIFIER_PROMPT, EXTRACTOR_SYSTEM_PROMPT, INTENT_CLASSIER_SYSTEM_PROMPT
from .schemas import CLASSIFIER_SCHEMA, EXTRACTION_SCHEMA, EXTRACTION_FROM_CONTEXT_SCHEMA
from app.models.internals import BuildLLMPromptAndSchema


logger = logging.getLogger(__name__)

TASK = Literal["classify", "extract", "answer_with_context"]

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

def build_prompt_and_schema(user_question: str, task: TASK) -> BuildLLMPromptAndSchema:
    system_prompt = EXTRACTOR_SYSTEM_PROMPT
    output_schema = EXTRACTION_SCHEMA
    prompt_msg = user_question
    if task == "classify":
        system_prompt = INTENT_CLASSIER_SYSTEM_PROMPT
        output_schema = CLASSIFIER_SCHEMA
        prompt_msg = deepcopy(INTENT_CLASSIFIER_PROMPT)
        prompt_msg = prompt_msg.replace("FILL_IN_QUESTION", user_question)
    if task == "answer_with_context":
        context = '\n'.join(DOCS)
        output_schema = EXTRACTION_FROM_CONTEXT_SCHEMA
        prompt_msg = deepcopy(PROMPT_WITH_CONTEXT)
        prompt_msg = prompt_msg.replace("FILL_IN_CONTEXT", context)
        prompt_msg = prompt_msg.replace("FILL_IN_QUESTION", user_question)
    prompt_schema_info = BuildLLMPromptAndSchema(
        llm_system_prompt=system_prompt,
        llm_output_schema=output_schema,
        llm_prompt=prompt_msg
    )
    return prompt_schema_info

def make_llm_request(user_question, task: TASK, retries=0) -> dict:
    url = "http://localhost:11434/api/chat"
    logger.info(f'making request for user question {user_question}')
    llm_prompt_info = build_prompt_and_schema(user_question, task)
    payload = {
           "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": llm_prompt_info.llm_system_prompt
               },
               {
                   "role": "user",
                   "content": llm_prompt_info.llm_prompt
              ,}
           ],
           "format": llm_prompt_info.llm_output_schema,
           "stream": False
    }
    payload = json.dumps(payload).encode('utf-8')
    req = request.Request(url, payload, headers={'Content-Type': 'application/json'}, method='POST')
    result = safe_retry(req, llm_prompt_info.llm_output_schema)
    return result
