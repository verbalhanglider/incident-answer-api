CLASSIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": ["billing", "shipping", "general"]},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "confidence_notes": {"type": "string"},
        "raw_text": {"type": "string"}
    },
    "required": ["intent", "confidence","confidence_notes", "raw_text"]
}

EXTRACTION_SCHEMA = {

    "type": "object",
    "properties": {
        "customer": {"type": ["string", "null"]},
        "issue_type": {"type": "string", "enum": ["refund", "payment_due", "double_charge", "invoice", "other"]},
        "amount": {"type": ["number", "null"]},
        "summary": {"type": "string"}
    },
    "required": ["customer", "issue_type", "amount", "summary"]
}

EXTRACTION_FROM_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"}
    },
    "required": ["answer"]

}