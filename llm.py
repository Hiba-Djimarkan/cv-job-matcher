"""llm.py - All communication with the Groq API (calls, retry, JSON parsing)."""
import json
import os
import time

from dotenv import load_dotenv
from groq import (
    Groq,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
)

load_dotenv()  # reads GROQ_API_KEY from the .env file (if it exists)

# Change the model here only: the rest of the project uses this variable.
MODEL_NAME = "openai/gpt-oss-120b"


class LLMError(Exception):
    """Our own error type, with a message that is safe to show to the user."""


def _get_client(api_key=None):
    """Use the key given by the user (sidebar) or fall back to the .env file."""
    api_key = api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError(
            "API key missing: enter it in the sidebar, add GROQ_API_KEY to the "
            ".env file, or switch on demo mode."
        )
    # timeout: never wait more than 30 seconds for an answer
    return Groq(api_key=api_key, timeout=30.0)


def call_llm(system, user, temperature, max_tokens, model=MODEL_NAME,
             retries=3, top_p=1.0, api_key=None):
    """Send one prompt to the model and return the text answer.

    Retries with exponential backoff (1s, 2s, 4s) on temporary errors
    (timeout, rate limit, network). Permanent errors stop immediately.
    """
    if not user or not user.strip():
        raise LLMError("Empty input: there is nothing to send to the model.")

    client = _get_client(api_key)
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,  # low = stable, high = creative
                max_tokens=max_tokens,    # upper limit of the answer length
                top_p=top_p,              # nucleus sampling
            )
            text = response.choices[0].message.content
            if not text:
                raise LLMError("Empty answer: try increasing max_tokens.")
            return text.strip()
        except (APITimeoutError, APIConnectionError, RateLimitError):
            if attempt == retries - 1:
                raise LLMError("The API is unavailable after several attempts.")
            time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s
        except AuthenticationError:
            raise LLMError("Invalid API key: check the key you entered.")
        except NotFoundError:
            raise LLMError(f"Model '{model}' not found: update MODEL_NAME.")


def _clean_json(text):
    """Remove markdown fences (```json ... ```) if the model added them."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def call_llm_json(system, user, temperature, max_tokens, model=MODEL_NAME,
                  api_key=None):
    """Like call_llm, but returns a Python dict parsed from the JSON answer.

    If the first answer is not valid JSON, we ask once more, more strictly.
    """
    text = call_llm(system, user, temperature, max_tokens, model, api_key=api_key)
    try:
        return json.loads(_clean_json(text))
    except json.JSONDecodeError:
        strict_user = user + "\n\nReturn ONLY valid JSON, with no other text."
        text = call_llm(system, strict_user, 0.0, max_tokens, model, api_key=api_key)
        try:
            return json.loads(_clean_json(text))
        except json.JSONDecodeError:
            raise LLMError("The model did not return valid JSON.")