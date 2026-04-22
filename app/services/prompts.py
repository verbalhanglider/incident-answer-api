INTENT_CLASSIER_SYSTEM_PROMPT = \
    """
    You are a support intent classifier.

    Rules:
    - return only valid json
    - choose exactly one intent from the allowed set
    - do not include explanation or extra text
    - do not invent new categories
    """

INTENT_CLASSIFIER_PROMPT = \
    """
    Classify the following message into one of these intents:

    - billing: charges, refunds, invoices, payments
    - shipping: delivery, tracking, delays, missing packages
    - general: anything not primarily about billing/payment or shipping classify as this
    - if payment, refund, invoice or charges are mentioned classify as billing even if shipping is also mentioned
    - if the request is too vague to classify as billing or shipping classify as general
    - include a confidence score following schema
    - add note explaining reason for confidence score
    - always return text received in raw_text field

    Return JSON that conforms to the provided schema

    Text:
    FILL_IN_QUESTION 
    """

EXTRACTOR_SYSTEM_PROMPT = \
    """
   You are a helpful assistant that only returns a valid JSON object. 

    Rules: 
    - Do not include any commentary or extra text outside the JSON. 
    - The JSON must conform to the provided schema." 
    """

PROMPT_WITH_CONTEXT = \
    """
    Answer the user's question using ONLY the provided context.

    If the answer is not in the context, always say you don't know based on provided context.

    Context:
    FILL_IN_CONTEXT 

    Question:
    FILL_IN_QUESTION 
    """