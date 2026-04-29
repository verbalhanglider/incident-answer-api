
from copy import deepcopy
from .schemas import CLASSIFIER_SCHEMA
from .prompts import INTENT_CLASSIER_SYSTEM_PROMPT, INTENT_CLASSIFIER_PROMPT
from app.models.internals import BuildLLMPromptAndSchema
import logging

from .llm_client import call_llm_with_retry

logger = logging.getLogger(__name__)

def llm_classify_request(user_question, retries=0) -> dict:
    url = "http://localhost:11434/api/chat"
    logger.info(f'making request for user question {user_question}')
    prompt_msg = deepcopy(INTENT_CLASSIFIER_PROMPT)
    prompt_msg = prompt_msg.replace("FILL_IN_QUESTION", user_question)
    llm_prompt_info = BuildLLMPromptAndSchema(
        llm_system_prompt=INTENT_CLASSIER_SYSTEM_PROMPT,
        llm_output_schema=CLASSIFIER_SCHEMA,
        llm_prompt=prompt_msg
    )
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
    result = call_llm_with_retry(url, payload, llm_prompt_info.llm_output_schema)
    return result