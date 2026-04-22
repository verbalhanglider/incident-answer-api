from copy import deepcopy
import sys
import urllib
from urllib import request
import json
from jsonschema import validate, ValidationError


LLM_API_URL = 'http://localhost:11434/api/chat'
VALID_INTENTS = set(["billing", "shipping", "general"])
EXTRACTION_SCHEMA = {

                   "type": "object",
                   "properties": {
                       "customer": {"type": ["string", "null"]},
                       "issue_type": {"type": "string", "enum": ["refund", "payment_due", "double_charge", "invoice", "other"]},
                        "amount": {"type": ["number", "null"]},
                       "summary": {"type": "string"},
                   },
                   "required": ["customer", "issue_type", "amount", "summary"]
}
EXTRACTION_SYSTEM_PROMPT = \
    """
    You are a helpful assistant that only returns a valid JSON object. 

    Rules: 
    - Do not include any commentary or extra text outside the JSON. 
    - The JSON must conform to the provided schema.
    """
EXTRACTION_PROMPT = {
           "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": EXTRACTION_SYSTEM_PROMPT
               },
               {
                   "role": "user",
                   "content": None
              ,}
           ],
           "format": EXTRACTION_SCHEMA,
           "stream": False
}
CLASSIFIER_SYSTEM_PROMPT = \
    """
    You are a support intent classifier.
    
    Rules:
    - return only valid json
    - choose exactly one intent from the allowed set
    - do not include explanation or extra text
    - do not invent new categories
    """
CLASSIFIER_TEXT = \
    """
    Classify the following message into one of these intents:

    - billing: charges, refunds, invoices, payments
    - shipping: delivery, tracking, delays, missing packages
    - general: anything not primarily about billing/payment or shipping classify as this
    - if payment, refund, invoice or charges are mentioned classify as billing even if shipping is also mentioned
    - if the request is too vague to classify as billing or shipping classify as general
    - include a confidence score following schema
    - add note explaining reason for confidence score

    Return JSON that conforms to the provided schema

    Text:
    %s
    """
CONTEXT_TEXT = \
    """
    Answer the user's question using ONLY the provided context.
j
    If the answer is not in the context, always say you don't know based on provided context.

    Context:
       FILL_IN_CONTEXT

    Question:
        FILL_IN_QUESTION        
    """
CLASSIFICATION_SCHEMA = {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["billing", "shipping", "general"]},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "confidence_notes": {"type": "string"}
            },
            "required": ["intent"]
}
CLASSIFY_PROMPT = {
            "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": CLASSIFIER_SYSTEM_PROMPT
               },
               {
                   "role": "user",
                   "content": None
              ,}
           ],
           "format": CLASSIFICATION_SCHEMA,
           "stream": False
}

GENERAL_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"}
    },
    "required": ["answer"]

}

CLASSIFY_PROMPT = {
           "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": CLASSIFIER_SYSTEM_PROMPT
               },
               {
                   "role": "user",
                   "content": None
              ,}
           ],
           "format": CLASSIFICATION_SCHEMA,
           "stream": False
}

GENERAL_PROMPT = {
           "model": "gemma3",
           "messages": [
               {
                   "role": "system",
                   "content": EXTRACTION_SYSTEM_PROMPT
               },
               {
                   "role": "user",
                   "content": None
              ,}
           ],
           "format": GENERAL_SCHEMA,
           "stream": False
}

DOCS = [
    "You can request a refund within 30 days of purchase.",
    "Shipping usually takes 3-5 business days.",
    "You can reset your password from the account settings page.",
    "Invoices are available in your billing dashboard.",
]

def validate_output(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        print("Validation error", e)
        return False

def send_http_post_req(req: request.Request, validation_schema, retries=2):
    last_inner = None
    for attempt in range(retries+1):
        try:
            with request.urlopen(req) as response:
                outer = json.load(response)
                inner = json.loads(outer['message']['content'])
                if validate_output(inner, validation_schema):
                    return inner
                else:
                    return {"error": "invalid schema",
                            "raw": inner
                        }
        except urllib.error.HTTPError as e: # type: ignore
            body = e.read().decode("utf-8", errors="replace")
            last_inner = {"error": str(e.reason), "status": e.code, "body": body}
    return {
        "error": "invalid_json_after_retries",
        "raw": last_inner
    }

def classify_request(text):
    data = deepcopy(CLASSIFY_PROMPT)
    data["messages"][1]["content"] = CLASSIFIER_TEXT % text
    payload = json.dumps(data).encode('utf-8')
    req = request.Request(LLM_API_URL, payload, headers={'Content-Type': 'application/json'}, method='POST')
    return send_http_post_req(req, CLASSIFICATION_SCHEMA)

def extract_billing_ticket(text: str):
    data = deepcopy(EXTRACTION_PROMPT)
    data["messages"][1]["content"] = text
    payload = json.dumps(data).encode('utf-8')
    req = request.Request(LLM_API_URL, payload, headers={'Content-Type': 'application/json'}, method='POST')
    return send_http_post_req(req, EXTRACTION_SCHEMA)

def extract_general_ticket(text: str):
    data = deepcopy(GENERAL_PROMPT)
    data["messages"][1]["content"] = text 
    payload = json.dumps(data).encode('utf-8')
    req = request.Request(LLM_API_URL, payload, headers={'Content-Type': 'application/json'}, method='POST')
    return send_http_post_req(req, GENERAL_SCHEMA)


def answer_general_request(text: str, context):
    data = deepcopy(GENERAL_PROMPT)
    data["messages"][1]["content"] = CONTEXT_TEXT % (text, '\n'.join(context))
    payload = json.dumps(data).encode('utf-8')
    req = request.Request(LLM_API_URL, payload, headers={'Content-Type': 'application/json'}, method='POST')
    return send_http_post_req(req, GENERAL_SCHEMA)


def retrieve_context(text:str):
    matches = []
    for doc in DOCS:
        if any(word in doc.lower() for word in text.lower().split()):
            matches.append(doc)
    return matches[2:]

def handle_request(prompt):
    classify_answer = classify_request(prompt)
    intent = classify_answer.get("intent", None)
    confidence = classify_answer.get("confidence", 0.0)
    confidence_notes = classify_answer.get("confidence_notes", None)
    if intent not in VALID_INTENTS or confidence < 0.8:
        answer = {"error": "low_cofidence_or_invalid_intent", "intent": intent, "promp": prompt, "notes": confidence_notes}
        sys.exit(2)
    if intent == "billing":
        answer = extract_billing_ticket(prompt)
    elif intent == "shipping":
        answer = {"status": "not_implemented", "intent": intent}
    else:
        print("hi")
        context = retrieve_context(prompt)
        answer = answer_general_request(prompt, context)
    return answer

if __name__ == "__main__":
    prompts = open(sys.argv[1]).readlines()
    for prompt in prompts:
        response = handle_request(prompt)
        print(
            json.dumps({"prompt": prompt, "result": response}, ensure_ascii=False)
        )