import json
from typing import Any
from langchain_core.output_parsers import JsonOutputParser

_langchain_json_parser = JsonOutputParser()


def clean_json_response(raw_text: str) -> str:
    """Strip markdown backticks, fences, and whitespace from LLM output."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def parse_json_safely(raw_text: Any, default: Any = None) -> Any:
    """
    Parses JSON output from LLMs using LangChain's JsonOutputParser.
    Handles markdown backtick fences (```json ... ```), partial JSON streaming,
    and unstructured text wrapper removal. Falls back to standard json or default on failure.
    """
    text = raw_text if isinstance(raw_text, str) else getattr(raw_text, "content", str(raw_text))
    
    try:
        return _langchain_json_parser.parse(text)
    except Exception:
        cleaned = clean_json_response(text)
        try:
            return json.loads(cleaned)
        except Exception:
            return default if default is not None else {}
